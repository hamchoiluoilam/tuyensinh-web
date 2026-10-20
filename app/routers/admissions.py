import random
import datetime
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Major, AdmissionApplication, PaymentTransaction, Subject
from ..schemas import (
    MajorOut, MajorDetailOut, MajorUpdateQuota,
    ApplicationCreate, ApplicationOut, ApplicationStatusUpdate
)

router = APIRouter(prefix="/api/admissions", tags=["M02 - Tuyển sinh (Người 1)"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        method=data.method,
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

@router.get("/lookup/{identifier}")
def lookup_application(identifier: str, db: Session = Depends(get_db)):
    """[Thí sinh] Tra cứu trạng thái hồ sơ theo Mã hồ sơ hoặc CCCD"""
    app = db.query(AdmissionApplication).filter(
        (AdmissionApplication.app_code == identifier) |
        (AdmissionApplication.id_card == identifier)
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ xét tuyển!")

    payment_info = {
        "status": app.payment.status if app.payment else "CHUA_TAO",
        "tx_code": app.payment.tx_code if app.payment else None,
        "amount": app.payment.amount if app.payment else 0,
        "paid_at": app.payment.paid_at if app.payment else None
    }

    return {
        "id": app.id,
        "app_code": app.app_code,
        "full_name": app.full_name,
        "id_card": app.id_card,
        "email": app.email,
        "phone": app.phone,
        "method": app.method,
        "score": app.score,
        "proof_url": app.proof_url,
        "major_name": app.major.name if app.major else "",
        "major_code": app.major.code if app.major else "",
        "major_nv2_name": app.major_nv2.name if app.major_nv2 else None,
        "admitted_major_name": app.admitted_major_name,
        "status": app.status,
        "created_at": app.created_at,
        "payment": payment_info
    }

@router.patch("/applications/{app_id}/status")
def update_application_status(app_id: int, data: ApplicationStatusUpdate, db: Session = Depends(get_db)):
    """[Cán bộ Admin] Duyệt hồ sơ (HOP_LE hoặc TU_CHOI)"""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Hồ sơ không tồn tại!")

    app.status = data.status
    db.commit()
    return {"message": "Cập nhật trạng thái hồ sơ thành công", "status": app.status}

@router.post("/run-virtual-filtering")
def run_virtual_filtering(major_id: int, db: Session = Depends(get_db)):
    """
    [Cán bộ Admin] THUẬT TOÁN LỌC ẢO 2 NGUYỆN VỌNG (NV1 VÀ NV2)
    1. Lấy ứng viên đăng ký NV1 vào ngành này có hồ sơ HOP_LE và ĐÃ THANH TOÁN (PAID).
    2. Sắp xếp điểm xét tuyển từ cao xuống thấp.
    3. Cắt top N theo chỉ tiêu Quota -> Trúng tuyển NV1.
    4. Các thí sinh còn lại (trượt NV1) nếu có đăng ký NV2 vào các ngành khác sẽ được chuyển tiếp xét ở NV2!
    5. Cập nhật điểm chuẩn chính thức.
    """
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Ngành không tồn tại!")

    # 1. Thí sinh đăng ký NV1
    nv1_candidates = db.query(AdmissionApplication).join(PaymentTransaction).filter(
        AdmissionApplication.major_id == major_id,
        AdmissionApplication.status.in_(["HOP_LE", "TRUNG_TUYEN_NV1", "KHONG_TRUNG_TUYEN", "TRUNG_TUYEN_NV2"]),
        PaymentTransaction.status == "PAID"
    ).order_by(AdmissionApplication.score.desc()).all()

    # 2. Thí sinh trượt NV1 ở ngành khác nhưng đăng ký NV2 vào ngành này
    nv2_candidates = db.query(AdmissionApplication).join(PaymentTransaction).filter(
        AdmissionApplication.major_nv2_id == major_id,
        AdmissionApplication.status.in_(["KHONG_TRUNG_TUYEN"]),
        PaymentTransaction.status == "PAID"
    ).order_by(AdmissionApplication.score.desc()).all()

    all_eligible = sorted(nv1_candidates + nv2_candidates, key=lambda x: x.score, reverse=True)

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
