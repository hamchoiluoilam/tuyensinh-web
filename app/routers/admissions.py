import random
import datetime
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Major, AdmissionApplication, PaymentTransaction, Subject, User
from ..schemas import (
    MajorOut, MajorDetailOut, MajorUpdateQuota,
    ApplicationCreate, ApplicationOut, ApplicationStatusUpdate,
    PublicVerifyLookupRequest, PublicVerifyLookupOut,
    ApplicationUpdate, ApplicationAppealRequest, ApplicationAppealReview
)
from .auth import get_current_user_from_req

router = APIRouter(prefix="/api/admissions", tags=["M02 - Tuyển sinh (Người 1)"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def mask_id_card(id_card: str) -> str:
    """Che giấu số CCCD bảo vệ quyền riêng tư (VD: 0012******11)"""
    if not id_card or len(id_card) < 6:
        return "******"
    return id_card[:4] + "*" * (len(id_card) - 6) + id_card[-2:]

def mask_phone(phone: str) -> str:
    """Che giấu số điện thoại cá nhân (VD: 0912***601)"""
    if not phone or len(phone) < 6:
        return "***"
    return phone[:4] + "***" + phone[-3:]

def mask_email(email: str) -> str:
    """Che giấu email (VD: st*****@gmail.com)"""
    if not email or "@" not in email:
        return "*****"
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    return (name[:2] + "*****" if len(name) > 2 else "*****") + "@" + domain

@router.get("/majors", response_model=List[MajorOut])
def get_majors(db: Session = Depends(get_db)):
    """Lấy danh sách các ngành tuyển sinh và chỉ tiêu"""
    return db.query(Major).all()

@router.get("/majors/{major_id}", response_model=MajorDetailOut)
def get_major_detail(major_id: int, db: Session = Depends(get_db)):
    """[Chi tiết ngành] Xem thông tin ngành và danh sách các môn học đào tạo"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngành học!")
    return major

@router.patch("/majors/{major_id}")
def update_major_quota(major_id: int, data: MajorUpdateQuota, db: Session = Depends(get_db)):
    """[Cán bộ Admin] Chỉnh sửa chỉ tiêu tuyển sinh và điểm chuẩn của ngành"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Ngành học không tồn tại!")
    major.quota = data.quota
    if data.benchmark_score is not None:
        major.benchmark_score = data.benchmark_score
    db.commit()
    return {"message": "Cập nhật ngành học thành công!", "quota": major.quota, "benchmark_score": major.benchmark_score}

@router.post("/upload-proof")
async def upload_proof_file(file: UploadFile = File(...)):
    """[Upload file thật] Tải trực tiếp ảnh học bạ/chứng chỉ từ máy tính hoặc điện thoại"""
    # Tạo tên file duy nhất tránh trùng lặp
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".pdf", ".webp"]:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ảnh (.jpg, .jpeg, .png, .webp) hoặc file PDF!")
    
    unique_name = f"proof_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/static/uploads/{unique_name}", "filename": file.filename}

@router.post("/apply", response_model=ApplicationOut)
def submit_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    """
    [Thí sinh] Nộp hồ sơ xét tuyển trực tuyến đa nguyện vọng (NV1 và NV2).
    Tự động sinh mã hồ sơ TS2026-XXXX và liên kết lệ phí mặc định.
    """
    major1 = db.query(Major).filter(Major.id == data.major_id).first()
    if not major1:
        raise HTTPException(status_code=404, detail="Ngành nguyện vọng 1 không tồn tại!")

    if data.major_nv2_id:
        if data.major_nv2_id == data.major_id:
            raise HTTPException(status_code=400, detail="Nguyện vọng 2 không được trùng với Nguyện vọng 1!")
        major2 = db.query(Major).filter(Major.id == data.major_nv2_id).first()
        if not major2:
            raise HTTPException(status_code=404, detail="Ngành nguyện vọng 2 không tồn tại!")

    # Kiểm tra số CCCD đã nộp trùng chưa
    existing = db.query(AdmissionApplication).filter(
        AdmissionApplication.id_card == data.id_card,
        AdmissionApplication.major_id == data.major_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Thí sinh với số CCCD này đã nộp hồ sơ vào ngành này rồi!")

    app_code = f"TS2026-{random.randint(100000, 999999)}"

    new_app = AdmissionApplication(
        app_code=app_code,
        full_name=data.full_name,
        id_card=data.id_card,
        email=data.email,
        phone=data.phone,
        method=data.method or data.method_code or "THPT",
        method_code=data.method_code or "THPT",
        method_name=data.method_name or "Xét tuyển kết quả thi tốt nghiệp THPT",
        subject_combination=data.subject_combination,
        priority_area=data.priority_area or "KV3",
        priority_score=data.priority_score or 0.0,
        score_details=data.score_details,
        score=data.score,
        major_id=data.major_id,
        major_nv2_id=data.major_nv2_id,
        user_id=data.user_id,
        proof_url=data.proof_url or "/static/uploads/default_proof.png",
        status="CHO_DUYET"
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Sinh phiếu thu lệ phí chưa thanh toán bên Module M07
    tx_code = f"PAY-{app_code}"
    new_payment = PaymentTransaction(
        tx_code=tx_code,
        application_id=new_app.id,
        amount=50000.0,
        status="UNPAID",
        qr_payload=f"2vcb://pay?acc=9999888899&amount=50000&memo={tx_code}"
    )
    db.add(new_payment)
    db.commit()

    return new_app

@router.get("/applications", response_model=List[ApplicationOut])
def list_applications(
    major_id: Optional[int] = None,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """[Cán bộ Admin] Xem và lọc danh sách hồ sơ tuyển sinh chuyên nghiệp"""
    query = db.query(AdmissionApplication)
    if major_id:
        query = query.filter(
            (AdmissionApplication.major_id == major_id) | (AdmissionApplication.major_nv2_id == major_id)
        )
    if status:
        query = query.filter(AdmissionApplication.status == status)
    if payment_status:
        query = query.join(PaymentTransaction).filter(PaymentTransaction.status == payment_status)
    if keyword:
        query = query.filter(
            (AdmissionApplication.full_name.ilike(f"%{keyword}%")) |
            (AdmissionApplication.id_card.ilike(f"%{keyword}%")) |
            (AdmissionApplication.app_code.ilike(f"%{keyword}%"))
        )
    return query.order_by(AdmissionApplication.score.desc()).all()

@router.post("/public-verify-lookup", response_model=PublicVerifyLookupOut)
def public_verify_lookup(data: PublicVerifyLookupRequest, db: Session = Depends(get_db)):
    """
    [Bảo Mật Tra Cứu Công Khai - Xác Minh 2 Yếu Tố 2FA & Che Giấu Dữ Liệu]
    Bắt buộc nhập đúng Mã hồ sơ VÀ 4 số cuối CCCD/CMND.
    Chỉ trả về dữ liệu cần thiết, đã được MASK (che mờ) hoàn toàn CCCD, SĐT.
    TUYỆT ĐỐI không trả về ảnh học bạ/minh chứng riêng tư.
    """
    app_code = data.app_code.strip()
    id_card_last4 = data.id_card_last4.strip()

    app = db.query(AdmissionApplication).filter(AdmissionApplication.app_code == app_code).first()
    if not app or not app.id_card.endswith(id_card_last4):
        raise HTTPException(
            status_code=400,
            detail="Mã hồ sơ hoặc 4 số cuối CCCD không trùng khớp. Vui lòng kiểm tra lại để bảo vệ thông tin thí sinh!"
        )

    return PublicVerifyLookupOut(
        app_code=app.app_code,
        full_name=app.full_name,
        id_card_masked=mask_id_card(app.id_card),
        phone_masked=mask_phone(app.phone),
        major_name=app.major.name if app.major else "",
        major_code=app.major.code if app.major else "",
        major_nv2_name=app.major_nv2.name if app.major_nv2 else None,
        method_code=app.method_code or app.method,
        method_name=app.method_name,
        subject_combination=app.subject_combination,
        priority_area=app.priority_area,
        priority_score=app.priority_score,
        score=app.score,
        status=app.status,
        admitted_major_name=app.admitted_major_name,
        payment_status=app.payment.status if app.payment else "UNPAID",
        created_at=app.created_at
    )

@router.get("/lookup/{identifier}")
def lookup_application(identifier: str, request: Request, db: Session = Depends(get_db)):
    """[Tra cứu hồ sơ] Kiểm tra quyền hạn: Chỉ trả về thông tin nhạy cảm (ảnh học bạ, CCCD) cho chính chủ hoặc cán bộ"""
    app = db.query(AdmissionApplication).filter(
        (AdmissionApplication.app_code == identifier) |
        (AdmissionApplication.id_card == identifier)
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ xét tuyển!")

    curr_user = get_current_user_from_req(request, db)
    is_owner = curr_user and (curr_user.id == app.user_id or curr_user.email == app.email)
    is_staff = curr_user and curr_user.role in ["OFFICER", "ADMIN"]

    payment_info = {
        "status": app.payment.status if app.payment else "CHUA_TAO",
        "tx_code": app.payment.tx_code if app.payment else None,
        "amount": app.payment.amount if app.payment else 0,
        "paid_at": app.payment.paid_at if app.payment else None
    }

    if is_owner or is_staff:
        return {
            "id": app.id,
            "app_code": app.app_code,
            "full_name": app.full_name,
            "id_card": app.id_card,
            "email": app.email,
            "phone": app.phone,
            "method": app.method,
            "method_code": app.method_code,
            "method_name": app.method_name,
            "subject_combination": app.subject_combination,
            "priority_area": app.priority_area,
            "priority_score": app.priority_score,
            "score_details": app.score_details,
            "score": app.score,
            "proof_url": app.proof_url,
            "officer_note": app.officer_note,
            "major_name": app.major.name if app.major else "",
            "major_code": app.major.code if app.major else "",
            "major_nv2_name": app.major_nv2.name if app.major_nv2 else None,
            "admitted_major_name": app.admitted_major_name,
            "status": app.status,
            "created_at": app.created_at,
            "payment": payment_info
        }
    else:
        # Khách vãng lai: Che mờ dữ liệu cá nhân & TUYỆT ĐỐI ẩn link minh chứng học bạ!
        return {
            "id": app.id,
            "app_code": app.app_code,
            "full_name": app.full_name,
            "id_card": mask_id_card(app.id_card),
            "email": mask_email(app.email),
            "phone": mask_phone(app.phone),
            "method": app.method,
            "method_code": app.method_code,
            "method_name": app.method_name,
            "subject_combination": app.subject_combination,
            "priority_area": app.priority_area,
            "priority_score": app.priority_score,
            "score": app.score,
            "proof_url": None,
            "major_name": app.major.name if app.major else "",
            "major_code": app.major.code if app.major else "",
            "major_nv2_name": app.major_nv2.name if app.major_nv2 else None,
            "admitted_major_name": app.admitted_major_name,
            "status": app.status,
            "created_at": app.created_at,
            "payment": payment_info,
            "is_masked": True
        }

@router.patch("/applications/{app_id}/status")
def update_application_status(app_id: int, data: ApplicationStatusUpdate, request: Request, db: Session = Depends(get_db)):
    """[Cán bộ / Admin] Duyệt hồ sơ (HOP_LE hoặc TU_CHOI) có ghi chú cán bộ"""
    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role not in ["OFFICER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Chỉ Cán bộ tuyển sinh hoặc Admin mới có quyền duyệt hồ sơ!")

    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Hồ sơ không tồn tại!")

    app.status = data.status
    if data.officer_note is not None:
        app.officer_note = data.officer_note
    db.commit()
    return {"message": "Cập nhật trạng thái hồ sơ thành công", "status": app.status, "officer_note": app.officer_note}

@router.post("/run-virtual-filtering")
def run_virtual_filtering(major_id: int, request: Request, db: Session = Depends(get_db)):
    """
    [Cán bộ / Admin] THUẬT TOÁN LỌC ẢO ĐA NGUYỆN VỌNG & TIÊU CHÍ PHỤ
    Tiêu chuẩn xếp hạng:
    1. Tổng điểm xét tuyển từ cao xuống thấp.
    2. Tiêu chí phụ 1 (Tie-breaker): Thí sinh đăng ký NV1 được ưu tiên trúng tuyển hơn NV2 khi bằng điểm.
    3. Tiêu chí phụ 2: Thời gian nộp hồ sơ sớm hơn được ưu tiên.
    4. Thí sinh trượt NV1 tự động được bảo lưu và chuyển tiếp xét ở NV2.
    """
    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role not in ["OFFICER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Chỉ Cán bộ tuyển sinh hoặc Admin mới có quyền chạy lọc ảo!")

    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Ngành không tồn tại!")

    # 1. Thí sinh đăng ký NV1
    nv1_candidates = db.query(AdmissionApplication).join(PaymentTransaction).filter(
        AdmissionApplication.major_id == major_id,
        AdmissionApplication.status.in_(["HOP_LE", "TRUNG_TUYEN_NV1", "KHONG_TRUNG_TUYEN", "TRUNG_TUYEN_NV2"]),
        PaymentTransaction.status == "PAID"
    ).all()

    # 2. Thí sinh trượt NV1 ở ngành khác nhưng đăng ký NV2 vào ngành này
    nv2_candidates = db.query(AdmissionApplication).join(PaymentTransaction).filter(
        AdmissionApplication.major_nv2_id == major_id,
        AdmissionApplication.status.in_(["KHONG_TRUNG_TUYEN"]),
        PaymentTransaction.status == "PAID"
    ).all()

    # Sắp xếp với tiêu chí phụ tie-breaking
    def get_sorting_rank(c):
        is_nv1 = 1 if c.major_id == major_id else 0
        ts = c.created_at.timestamp() if c.created_at else 0
        return (c.score, is_nv1, -ts)

    all_eligible = sorted(nv1_candidates + nv2_candidates, key=get_sorting_rank, reverse=True)

    if not all_eligible:
        return {
            "message": "Không có ứng viên nào hợp lệ và đã đóng lệ phí để lọc ảo!",
            "passed_count": 0,
            "benchmark_score": 0.0
        }

    quota = major.quota
    passed = all_eligible[:quota]
    failed = all_eligible[quota:]

    for c in passed:
        if c.major_id == major_id:
            c.status = "TRUNG_TUYEN_NV1"
            c.admitted_major_name = f"{major.name} (Nguyện vọng 1)"
        else:
            c.status = "TRUNG_TUYEN_NV2"
            c.admitted_major_name = f"{major.name} (Nguyện vọng 2)"

    for c in failed:
        if c.status not in ["TRUNG_TUYEN_NV1"]:
            c.status = "KHONG_TRUNG_TUYEN"
            c.admitted_major_name = None

    benchmark = passed[-1].score if passed else 0.0
    major.benchmark_score = benchmark

    db.commit()

    return {
        "message": f"Chạy lọc ảo đa nguyện vọng thành công cho ngành {major.name}!",
        "major_code": major.code,
        "quota": quota,
        "total_eligible": len(all_eligible),
        "passed_count": len(passed),
        "benchmark_score": benchmark
    }

@router.put("/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, data: ApplicationUpdate, request: Request, db: Session = Depends(get_db)):
    """[Thí sinh] Chỉnh sửa thông tin hồ sơ (Chỉ khả dụng khi hồ sơ ở trạng thái CHO_DUYET)"""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role == "STUDENT":
        if app.user_id != curr_user.id and app.email != curr_user.email:
            raise HTTPException(status_code=403, detail="Bảo mật: Bạn không có quyền chỉnh sửa hồ sơ này!")

    if app.status != "CHO_DUYET":
        raise HTTPException(status_code=400, detail=f"Hồ sơ đã ở trạng thái [{app.status}], không thể tự ý chỉnh sửa! Vui lòng liên hệ ban tuyển sinh hoặc nộp đơn phúc khảo.")

    if data.major_id is not None:
        major = db.query(Major).filter(Major.id == data.major_id).first()
        if not major:
            raise HTTPException(status_code=404, detail="Ngành NV1 không tồn tại!")
        app.major_id = data.major_id

    if data.major_nv2_id is not None:
        if data.major_nv2_id == app.major_id:
            raise HTTPException(status_code=400, detail="Nguyện vọng 2 không được trùng với Nguyện vọng 1!")
        app.major_nv2_id = data.major_nv2_id

    if data.method is not None:
        app.method = data.method
    if data.method_code is not None:
        app.method_code = data.method_code
    if data.method_name is not None:
        app.method_name = data.method_name
    if data.subject_combination is not None:
        app.subject_combination = data.subject_combination
    if data.priority_area is not None:
        app.priority_area = data.priority_area
    if data.priority_score is not None:
        app.priority_score = data.priority_score
    if data.score_details is not None:
        app.score_details = data.score_details
    if data.score is not None:
        app.score = data.score
    if data.proof_url is not None:
        app.proof_url = data.proof_url

    db.commit()
    db.refresh(app)
    return app

@router.post("/applications/{app_id}/withdraw")
def withdraw_application(app_id: int, request: Request, db: Session = Depends(get_db)):
    """[Thí sinh] Rút / Hủy hồ sơ xét tuyển"""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role == "STUDENT":
        if app.user_id != curr_user.id and app.email != curr_user.email:
            raise HTTPException(status_code=403, detail="Bảo mật: Bạn không có quyền thao tác trên hồ sơ này!")

    if app.status in ["DA_RUT", "HUY_HO_SO"]:
        return {"message": "Hồ sơ đã được rút trước đó rồi!", "status": app.status}

    if app.status == "DA_NHAP_HOC":
        raise HTTPException(status_code=400, detail="Thí sinh đã xác nhận nhập học chính thức, không thể tự rút hồ sơ trực tuyến. Vui lòng liên hệ Phòng Đào tạo NEU!")

    app.status = "DA_RUT"
    app.officer_note = (app.officer_note or "") + " [Thí sinh chủ động rút hồ sơ xét tuyển]"
    db.commit()

    return {"message": f"Đã rút thành công hồ sơ {app.app_code}!", "status": "DA_RUT"}

@router.post("/applications/{app_id}/appeal")
def submit_appeal(app_id: int, data: ApplicationAppealRequest, request: Request, db: Session = Depends(get_db)):
    """[Thí sinh] Nộp đơn xin phúc khảo hồ sơ / khiếu nại kết quả xét tuyển"""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role == "STUDENT":
        if app.user_id != curr_user.id and app.email != curr_user.email:
            raise HTTPException(status_code=403, detail="Bảo mật: Bạn không có quyền gửi đơn phúc khảo cho hồ sơ này!")

    app.appeal_note = data.appeal_note
    if data.appeal_proof_url:
        app.appeal_proof_url = data.appeal_proof_url
    app.appeal_status = "PENDING"
    db.commit()

    return {
        "message": f"Nộp đơn phúc khảo cho hồ sơ {app.app_code} thành công! Hội đồng tuyển sinh sẽ thụ lý hồ sơ của bạn.",
        "appeal_status": "PENDING"
    }

@router.post("/applications/{app_id}/review-appeal")
def review_appeal(app_id: int, data: ApplicationAppealReview, request: Request, db: Session = Depends(get_db)):
    """[Cán bộ / Admin] Xử lý & trả lời kết quả phúc khảo"""
    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role not in ["ADMIN", "OFFICER"]:
        raise HTTPException(status_code=403, detail="Chỉ Cán bộ tuyển sinh hoặc Admin mới có quyền xét duyệt phúc khảo!")

    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    app.appeal_status = data.appeal_status
    if data.officer_note:
        app.officer_note = data.officer_note
    if data.new_score is not None:
        app.score = data.new_score
    if data.new_status:
        app.status = data.new_status

    db.commit()
    return {
        "message": f"Đã hoàn tất xử lý phúc khảo cho hồ sơ {app.app_code}!",
        "appeal_status": app.appeal_status,
        "status": app.status,
        "score": app.score
    }

@router.post("/applications/{app_id}/enroll")
def confirm_enrollment(app_id: int, request: Request, db: Session = Depends(get_db)):
    """
    [Hậu tuyển sinh] Xác nhận nhập học trực tuyến & Cấp Mã số Sinh viên (MSSV) + Email trường
    Áp dụng cho thí sinh có trạng thái TRUNG_TUYEN_NV1, TRUNG_TUYEN_NV2, hoặc TRUNG_TUYEN
    """
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role == "STUDENT":
        if app.user_id != curr_user.id and app.email != curr_user.email:
            raise HTTPException(status_code=403, detail="Bảo mật: Bạn không có quyền xác nhận nhập học cho hồ sơ này!")

    admitted_statuses = ["TRUNG_TUYEN_NV1", "TRUNG_TUYEN_NV2", "TRUNG_TUYEN"]
    if app.status not in admitted_statuses and app.status != "DA_NHAP_HOC":
        raise HTTPException(
            status_code=400,
            detail=f"Hồ sơ hiện tại (trạng thái: {app.status}) chưa đủ điều kiện trúng tuyển để xác nhận nhập học!"
        )

    if app.status == "DA_NHAP_HOC" and app.student_code:
        return {
            "message": "Thí sinh đã hoàn tất xác nhận nhập học trực tuyến!",
            "student_code": app.student_code,
            "student_email": app.student_email,
            "enrolled_at": app.enrolled_at,
            "admitted_major": app.admitted_major_name or app.major.name,
            "cohort": "K68 (Niên khóa 2026 - 2030)"
        }

    target_major = app.major
    if app.status == "TRUNG_TUYEN_NV2" and app.major_nv2:
        target_major = app.major_nv2

    major_suffix = target_major.code.replace("7", "", 1)[:4] if len(target_major.code) >= 5 else "9999"
    seq = 1000 + (app.id % 9000)
    student_code = f"26{major_suffix}{seq}"
    student_email = f"{student_code}@st.neu.edu.vn"

    app.status = "DA_NHAP_HOC"
    app.student_code = student_code
    app.student_email = student_email
    app.enrolled_at = datetime.datetime.utcnow()
    db.commit()

    return {
        "message": "Chúc mừng bạn đã hoàn tất thủ tục xác nhận nhập học trực tuyến thành công!",
        "student_code": student_code,
        "student_email": student_email,
        "enrolled_at": app.enrolled_at,
        "admitted_major": app.admitted_major_name or target_major.name,
        "cohort": "K68 (Niên khóa 2026 - 2030)"
    }

@router.get("/certificate/{app_code}")
def get_admission_certificate(app_code: str, db: Session = Depends(get_db)):
    """[Giấy Báo Trúng Tuyển & Nhập Học Điện Tử] Tra cứu giấy chứng nhận điện tử trúng tuyển NEU có dấu xác thực"""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.app_code == app_code).first()
    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ!")

    if app.status not in ["TRUNG_TUYEN_NV1", "TRUNG_TUYEN_NV2", "TRUNG_TUYEN", "DA_NHAP_HOC"]:
        raise HTTPException(status_code=400, detail="Hồ sơ chưa đạt kết quả trúng tuyển chính thức để cấp Giấy báo nhập học!")

    admitted_major = app.major
    if app.status == "TRUNG_TUYEN_NV2" and app.major_nv2:
        admitted_major = app.major_nv2

    verify_url = f"https://tuyensinh.neu.edu.vn/api/admissions/certificate/{app.app_code}"
    verify_qr = f"https://img.vietqr.io/image/MB-0915852023-compact2.png?amount=0&addInfo=VERIFY-{app.app_code}&accountName=LE%20THIEN%20PHU"

    return {
        "app_code": app.app_code,
        "full_name": app.full_name,
        "id_card": app.id_card,
        "email": app.email,
        "phone": app.phone,
        "admitted_major_name": admitted_major.name,
        "admitted_major_code": admitted_major.code,
        "admitted_method": app.method_name or app.method,
        "score": app.score,
        "status": app.status,
        "student_code": app.student_code or "CHƯA_CẤP",
        "student_email": app.student_email or "---",
        "enrolled_at": app.enrolled_at.strftime("%H:%M ngày %d/%m/%Y") if app.enrolled_at else "Chưa xác nhận",
        "cohort": "K68 (Khóa 2026 - 2030)",
        "university": "TRƯỜNG ĐẠI HỌC KINH TẾ QUỐC DÂN (NEU)",
        "verification_url": verify_url,
        "verification_qr": verify_qr
    }
