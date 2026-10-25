import random
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from ..models import FAQItem, SupportTicket, AdmissionApplication, Major, Subject
from ..schemas import FAQOut, TicketCreate, TicketReply, TicketOut, AIChatQuery

router = APIRouter(prefix="/api/support", tags=["M12 - Hỗ trợ người học (Người 3)"])

@router.get("/faqs", response_model=List[FAQOut])
def get_faqs(category: Optional[str] = None, db: Session = Depends(get_db)):
    """[Thí sinh / Cán bộ] Xem danh mục câu hỏi thường gặp FAQ"""
    query = db.query(FAQItem)
    if category:
        query = query.filter(FAQItem.category == category)
    return query.all()

@router.post("/tickets", response_model=TicketOut)
def create_support_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    """
    [Thí sinh] Gửi phiếu yêu cầu hỗ trợ / giải đáp thắc mắc tuyển sinh.
    Tự sinh mã phiếu hỗ trợ TK-XXXX.
    """
    ticket_code = f"TK-{random.randint(10000, 99999)}"

    app_id = None
    if data.application_id:
        app = db.query(AdmissionApplication).filter(AdmissionApplication.id == data.application_id).first()
        if app:
            app_id = app.id

    ticket = SupportTicket(
        ticket_code=ticket_code,
        application_id=app_id,
        user_id=data.user_id,
        sender_name=data.sender_name,
        sender_email=data.sender_email,
        sender_phone=data.sender_phone,
        category=data.category,
        subject=data.subject,
        message=data.message,
        status="PENDING"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/tickets", response_model=List[TicketOut])
def list_tickets(status: Optional[str] = None, db: Session = Depends(get_db)):
    """[Cán bộ Tư vấn] Danh sách các phiếu yêu cầu trợ giúp"""
    query = db.query(SupportTicket)
    if status:
        query = query.filter(SupportTicket.status == status)
    return query.order_by(SupportTicket.created_at.desc()).all()

@router.get("/tickets/lookup/{code}")
def lookup_ticket(code: str, db: Session = Depends(get_db)):
    """[Thí sinh] Tra cứu tiến độ giải quyết ticket theo mã phiếu"""
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_code == code).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu hỗ trợ!")
    return ticket

@router.patch("/tickets/{ticket_id}/reply")
def reply_ticket(ticket_id: int, data: TicketReply, db: Session = Depends(get_db)):
    """
    [Cán bộ Tư vấn] Trả lời giải đáp cho thí sinh và chuyển trạng thái sang RESOLVED
    """
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Phiếu hỗ trợ không tồn tại!")

    ticket.reply = data.reply
    ticket.status = "RESOLVED"
    ticket.resolved_at = datetime.datetime.utcnow()
    db.commit()

    return {"message": "Phản hồi ticket thành công!", "ticket_code": ticket.ticket_code, "status": ticket.status}

@router.get("/stats")
def get_support_stats(db: Session = Depends(get_db)):
    """Thống kê tình hình tiếp nhận và hỗ trợ người học"""
    total = db.query(func.count(SupportTicket.id)).scalar() or 0
    pending = db.query(func.count(SupportTicket.id)).filter(SupportTicket.status == "PENDING").scalar() or 0
    resolved = db.query(func.count(SupportTicket.id)).filter(SupportTicket.status == "RESOLVED").scalar() or 0

    return {
        "total_tickets": total,
        "pending_tickets": pending,
        "resolved_tickets": resolved,
        "resolution_rate": round((resolved / total * 100), 1) if total > 0 else 0
    }

from ..ai_engine import process_ai_admission_chat

# =========================================================================
# TÍNH NĂNG ĐIỂM CỘNG 10/10: TRỢ LÝ AI TƯ VẤN TUYỂN SINH THÔNG MINH (AI ADMISSION ASSISTANT)
# =========================================================================
@router.post("/ai-consultant")
def ai_admission_consultant(data: AIChatQuery, db: Session = Depends(get_db)):
    """
    [Hệ Thống Trí Tuệ Nhân Tạo Tuyển Sinh Hoàn Chỉnh]
    Xử lý tự nhiên đa luồng: Google Gemini LLM API (nếu có key) + Standalone Expert Reasoning Engine
    - Trích xuất điểm số, tổ hợp thi (A00, A01, D01, B00...)
    - Phân tích xác suất trúng tuyển theo 3 tầng (An toàn / Vừa sức / Bứt phá)
    - Tối ưu hóa chiến lược đăng ký Đa nguyện vọng (NV1 & NV2)
    - Phân tích môn học chuyên sâu từ kho 383 môn học của trường
    """
    return process_ai_admission_chat(
        query=data.query,
        user_score=data.score,
        combination=data.combination,
        history=data.history,
        db=db
    )
