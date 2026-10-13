import random
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Major, AdmissionApplication, PaymentTransaction, Subject
from ..schemas import MajorOut, MajorDetailOut, ApplicationCreate, ApplicationOut, ApplicationStatusUpdate

router = APIRouter(prefix="/api/admissions", tags=["M02 - Tuyển sinh (Người 1)"])

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

@router.post("/apply", response_model=ApplicationOut)
def submit_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    """
    [Thí sinh] Nộp hồ sơ xét tuyển trực tuyến.
    Tự động sinh mã hồ sơ TS2026-XXXX và liên kết lệ phí mặc định.
    """
    # 1. Kiểm tra ngành học tồn tại
    major = db.query(Major).filter(Major.id == data.major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Ngành xét tuyển không tồn tại!")

    # 2. Kiểm tra nếu CCCD này đã nộp cùng ngành
    existing = db.query(AdmissionApplication).filter(
        AdmissionApplication.id_card == data.id_card,
        AdmissionApplication.major_id == data.major_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Thí sinh với số CCCD này đã nộp hồ sơ vào ngành này rồi!")

    # 3. Tạo mã hồ sơ ngẫu nhiên
    app_code = f"TS2026-{random.randint(100000, 999999)}"

    # 4. Lưu hồ sơ
    new_app = AdmissionApplication(
        app_code=app_code,
        full_name=data.full_name,
        id_card=data.id_card,
        email=data.email,
        phone=data.phone,
        method=data.method,
        score=data.score,
        major_id=data.major_id,
        user_id=data.user_id,
        proof_url=data.proof_url or "https://via.placeholder.com/400x300.png?text=Minh+Chung+Hoc+Ba",
        status="CHO_DUYET"
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # 5. Tự động sinh phiếu thu lệ phí chưa thanh toán bên Module M07
    tx_code = f"PAY-{app_code}"
    new_payment = PaymentTransaction(
        tx_code=tx_code,
        application_id=new_app.id,
        amount=50000.0,
        status="UNPAID",
        qr_payload=f"2vcb://pay?acc=99998888&amount=50000&memo={tx_code}"
    )
    db.add(new_payment)
    db.commit()

    return new_app

@router.get("/applications", response_model=List[ApplicationOut])
def list_applications(
    major_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """[Cán bộ Admin] Xem và lọc danh sách hồ sơ tuyển sinh"""
    query = db.query(AdmissionApplication)
    if major_id:
        query = query.filter(AdmissionApplication.major_id == major_id)
    if status:
        query = query.filter(AdmissionApplication.status == status)
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
        "major_name": app.major.name if app.major else "",
        "major_code": app.major.code if app.major else "",
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
    [Cán bộ Admin] THUẬT TOÁN LỌC ẢO & XÉT TRÚNG TUYỂN
    - Lấy các hồ sơ đã duyệt HOP_LE và ĐÃ THANH TOÁN LỆ PHÍ (liên kết M07).
    - Sắp xếp điểm xét tuyển từ cao xuống thấp.
    - Lấy top N thí sinh theo đúng chỉ tiêu (quota) của ngành -> Set TRUNG_TUYEN.
    - Điểm của thí sinh thứ N chính là điểm chuẩn (benchmark_score).
    - Các thí sinh còn lại set KHONG_TRUNG_TUYEN.
    """
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Ngành không tồn tại!")

    # Lấy các hồ sơ hợp lệ thuộc ngành này
    candidates = db.query(AdmissionApplication).join(PaymentTransaction).filter(
        AdmissionApplication.major_id == major_id,
        AdmissionApplication.status.in_(["HOP_LE", "TRUNG_TUYEN", "KHONG_TRUNG_TUYEN"]),
        PaymentTransaction.status == "PAID" # Điều kiện bắt buộc: Đã đóng lệ phí
    ).order_by(AdmissionApplication.score.desc()).all()

    if not candidates:
        return {
            "message": "Không có ứng viên nào hợp lệ và đã đóng lệ phí để lọc ảo!",
            "passed_count": 0,
            "benchmark_score": 0.0
        }

    quota = major.quota
    passed = candidates[:quota]
    failed = candidates[quota:]

    for c in passed:
        c.status = "TRUNG_TUYEN"

    for c in failed:
        c.status = "KHONG_TRUNG_TUYEN"

    # Cập nhật điểm chuẩn ngành
    benchmark = passed[-1].score if passed else 0.0
    major.benchmark_score = benchmark

    db.commit()

    return {
        "message": f"Chạy lọc ảo thành công cho ngành {major.name}!",
        "major_code": major.code,
        "quota": quota,
        "total_eligible": len(candidates),
        "passed_count": len(passed),
        "benchmark_score": benchmark
    }
