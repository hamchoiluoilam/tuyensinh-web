
import datetime
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..database import get_db
from ..models import FeeConfig, PaymentTransaction, AdmissionApplication
from ..schemas import PaymentOut, FeeConfigUpdate, WebhookIPNPayload
from .auth import get_current_user_from_req
router = APIRouter(prefix="/api/finance", tags=["M07 - Tài chính kế toán (Người 2)"])
DEFAULT_BANK_NAME = "MBBank (Ngân hàng TMCP Quân Đội)"
DEFAULT_BANK_ACCOUNT = "0915852023"
DEFAULT_ACCOUNT_HOLDER = "LE THIEN PHU"
FALLBACK_QR_URL = "/static/uploads/my_qr_mb.png"
@router.get("/fee-configs")
def get_fee_configs(db: Session = Depends(get_db)):
    """[Kế toán / Thí sinh] Xem biểu phí xét tuyển hiện hành"""
    return db.query(FeeConfig).all()
@router.patch("/fee-configs/{config_id}")
def update_fee_config(config_id: int, data: FeeConfigUpdate, request: Request, db: Session = Depends(get_db)):
    """[Chỉ Admin] Cập nhật mức thu lệ phí xét tuyển của trường"""
    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Chỉ Quản trị viên cấp cao (ADMIN) mới có quyền điều chỉnh biểu phí lệ phí!")
    
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
    """Tra cứu chi tiết một giao dịch thanh toán kèm mã VietQR MBBank động và mã QR thực tế"""
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch thanh toán!")
    app = tx.application
    amount = int(tx.amount)
    memo = tx.tx_code
    vietqr_url = f"https://img.vietqr.io/image/MB-{DEFAULT_BANK_ACCOUNT}-compact2.png?amount={amount}&addInfo={memo}&accountName=LE%20THIEN%20PHU"
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
                "bank_account": DEFAULT_BANK_ACCOUNT,
                "bank_name": DEFAULT_BANK_NAME,
                "account_holder": DEFAULT_ACCOUNT_HOLDER,
                "memo": memo,
                "qr_image_url": vietqr_url,
                "fallback_qr_url": FALLBACK_QR_URL
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
@router.post("/webhook-ipn")
def webhook_ipn(payload: WebhookIPNPayload, db: Session = Depends(get_db)):
    """
    [Webhook Thanh toán Tự Động - IPN Auto Reconcile]
    Lắng nghe thông báo biến động số dư từ ngân hàng (MBBank / SePay / VietQR Gateway).
    Tự động quét mã memo (PAY-TS2026-XXXX) và gạch nợ tự động trong 0.5s.
    """
    search_text = f"{payload.content or ''} {payload.description or ''} {payload.memo or ''}".strip().upper()
    match = re.search(r"(PAY-TS2026-[A-Z0-9]+|PAY-[A-Z0-9]+)", search_text)
    if not match:
        raise HTTPException(status_code=400, detail="Không tìm thấy mã giao dịch hợp lệ (dạng PAY-TS2026-XXXX) trong nội dung chuyển khoản!")

    tx_code = match.group(1)
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy giao dịch {tx_code} trên hệ thống!")
    if tx.status == "PAID":
        return {"success": True, "message": "Giao dịch đã được thanh toán trước đó!", "tx_code": tx.tx_code}
    tx.status = "PAID"
    tx.paid_at = datetime.datetime.utcnow()
    db.commit()
    return {
        "success": True,
        "message": f"Đối soát tự động thành công! Đã ghi nhận lệ phí cho hồ sơ {tx.application.app_code if tx.application else ''}.",
        "tx_code": tx.tx_code,
        "amount": tx.amount,
        "paid_at": tx.paid_at
    }
@router.get("/receipt/{tx_code}")
def get_payment_receipt(tx_code: str, request: Request, db: Session = Depends(get_db)):
    """[Biên lai điện tử] Lấy dữ liệu in phiếu thu biên lai cho thí sinh (Có kiểm tra bảo mật quyền sở hữu)"""
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.tx_code == tx_code).first()
    if not tx or tx.status != "PAID":
        raise HTTPException(status_code=400, detail="Giao dịch chưa thanh toán hoặc không tồn tại để xuất biên lai!")
    app = tx.application
    curr_user = get_current_user_from_req(request, db)
    if curr_user and curr_user.role == "STUDENT":
        if app.user_id != curr_user.id and app.email != curr_user.email:
            raise HTTPException(status_code=403, detail="Bảo mật: Bạn không có quyền truy cập biên lai của thí sinh khác!")
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
        "bank_name": DEFAULT_BANK_NAME,
        "bank_account": DEFAULT_BANK_ACCOUNT,
        "account_holder": DEFAULT_ACCOUNT_HOLDER,
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

