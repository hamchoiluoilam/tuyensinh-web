import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from ..models import FeeConfig, PaymentTransaction, AdmissionApplication
from ..schemas import PaymentOut, FeeConfigUpdate

router = APIRouter(prefix="/api/finance", tags=["M07 - Tài chính kế toán (Người 2)"])

@router.get("/fee-configs")
def get_fee_configs(db: Session = Depends(get_db)):
    """[Kế toán / Thí sinh] Xem biểu phí xét tuyển hiện hành"""
    return db.query(FeeConfig).all()

@router.patch("/fee-configs/{config_id}")
def update_fee_config(config_id: int, data: FeeConfigUpdate, db: Session = Depends(get_db)):
    """[Kế toán] Cập nhật mức thu lệ phí xét tuyển"""
    fee = db.query(FeeConfig).filter(FeeConfig.id == config_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Không tìm thấy cấu hình biểu phí!")
    fee.amount = data.amount
    if data.fee_name:
        fee.fee_name = data.fee_name
    if data.description:
        fee.description = data.description
    db.commit()
    return {"message": "Cập nhật biểu phí thành công!", "amount": fee.amount}

@router.get("/transactions", response_model=List[PaymentOut])
def list_transactions(status: Optional[str] = None, db: Session = Depends(get_db)):
    """[Cán bộ Kế toán] Xem toàn bộ giao dịch đóng lệ phí"""
    query = db.query(PaymentTransaction)
    if status:
        query = query.filter(PaymentTransaction.status == status)
    return query.order_by(PaymentTransaction.created_at.desc()).all()

@router.get("/transaction/{tx_code}")
def get_transaction_by_code(tx_code: str, db: Session = Depends(get_db)):
    """Tra cứu chi tiết một giao dịch thanh toán kèm mã QR và thông tin biên lai"""
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch thanh toán!")

    app = tx.application
    bank_account = "9999888899"
    bank_name = "VIETCOMBANK"
    amount = int(tx.amount)
    memo = tx.tx_code
    vietqr_url = f"https://api.vietqr.io/image/970436-{bank_account}-compact.jpg?amount={amount}&addInfo={memo}"

    return {
        "tx_code": tx.tx_code,
        "amount": tx.amount,
        "status": tx.status,
        "method": tx.method,
        "created_at": tx.created_at,
        "paid_at": tx.paid_at,
        "candidate_name": app.full_name if app else "",
        "id_card": app.id_card if app else "",
        "app_code": app.app_code if app else "",
        "major_name": app.major.name if (app and app.major) else "",
        "bank_account": bank_account,
        "bank_name": bank_name,
        "memo": memo,
        "qr_image_url": vietqr_url
    }

@router.post("/simulate-pay/{tx_code}")
def simulate_payment(tx_code: str, db: Session = Depends(get_db)):
    """
    [Giả lập Cổng Thanh toán / Thí sinh] Xác nhận thanh toán thành công
    Cập nhật trạng thái sang 'PAID' và ghi nhận thời gian nộp tiền.
    """
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Giao dịch không tồn tại!")

    if tx.status == "PAID":
        return {"message": "Giao dịch này đã được thanh toán trước đó rồi!", "status": "PAID"}

    tx.status = "PAID"
    tx.paid_at = datetime.datetime.utcnow()
    db.commit()

    return {
        "message": f"Thanh toán thành công {tx.amount:,.0f} VNĐ cho hồ sơ!",
        "tx_code": tx.tx_code,
        "status": tx.status,
        "paid_at": tx.paid_at
    }

@router.get("/receipt/{tx_code}")
def get_payment_receipt(tx_code: str, db: Session = Depends(get_db)):
    """[Biên lai điện tử] Lấy dữ liệu in phiếu thu biên lai cho thí sinh"""
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx or tx.status != "PAID":
        raise HTTPException(status_code=400, detail="Giao dịch chưa thanh toán hoặc không tồn tại để xuất biên lai!")

    app = tx.application
    return {
        "receipt_number": f"BL-{tx.tx_code}",
        "tx_code": tx.tx_code,
        "app_code": app.app_code,
        "full_name": app.full_name,
        "id_card": app.id_card,
        "email": app.email,
        "phone": app.phone,
        "major_name": app.major.name,
        "amount": tx.amount,
        "paid_at": tx.paid_at.strftime("%H:%M:%S ngày %d/%m/%Y") if tx.paid_at else "---",
        "method": tx.method,
        "status": "ĐÃ XÁC NHẬN NỘP ĐỦ LỆ PHÍ"
    }

@router.get("/revenue-summary")
def get_revenue_summary(db: Session = Depends(get_db)):
    """
    [Cán bộ Kế toán / Ban Giám hiệu] Dashboard thống kê doanh thu lệ phí
    """
    total_tx = db.query(func.count(PaymentTransaction.id)).scalar() or 0
    paid_tx = db.query(func.count(PaymentTransaction.id)).filter(PaymentTransaction.status == "PAID").scalar() or 0
    unpaid_tx = total_tx - paid_tx

    total_revenue = db.query(func.sum(PaymentTransaction.amount)).filter(PaymentTransaction.status == "PAID").scalar() or 0.0
    expected_revenue = db.query(func.sum(PaymentTransaction.amount)).scalar() or 0.0

    return {
        "total_applications": total_tx,
        "paid_count": paid_tx,
        "unpaid_count": unpaid_tx,
        "total_revenue": total_revenue,
        "expected_revenue": expected_revenue,
        "payment_rate_percent": round((paid_tx / total_tx * 100), 1) if total_tx > 0 else 0
    }
