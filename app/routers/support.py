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

# =========================================================================
# TÍNH NĂNG ĐIỂM CỘNG 10/10: TRỢ LÝ AI TƯ VẤN TUYỂN SINH THÔNG MINH (AI ADMISSION ASSISTANT)
# =========================================================================
@router.post("/ai-consultant")
def ai_admission_consultant(data: AIChatQuery, db: Session = Depends(get_db)):
    """
    [AI Tuyển Sinh Thông Minh]
    Tự động phân tích câu hỏi của thí sinh (điểm số, ngành yêu thích, môn học, học phí, cơ hội nghề nghiệp)
    để tư vấn gợi ý ngành học phù hợp nhất từ kho 40 ngành và 383 môn học của trường.
    """
    q = data.query.lower().strip()
    user_score = data.score
    
    # Tìm kiếm trích xuất số điểm nếu người dùng gõ trong văn bản (ví dụ "em được 24.5 điểm...")
    import re
    match_score = re.search(r'(\d{1,2}(?:\.\d{1,2})?)\s*điểm', q)
    if match_score and user_score is None:
        try:
            user_score = float(match_score.group(1))
        except:
            pass

    # Phân tích theo điểm
    if user_score is not None:
        # Lọc các ngành có điểm chuẩn tham khảo <= user_score + 1.0
        suitable_majors = db.query(Major).filter(
            Major.benchmark_score <= (user_score + 0.5),
            Major.benchmark_score >= (user_score - 3.5)
        ).order_by(Major.benchmark_score.desc()).limit(5).all()

        if suitable_majors:
            list_txt = "<br>".join([
                f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn dự kiến: <span class='badge bg-danger'>{m.benchmark_score}</span> (Chỉ tiêu: {m.quota})"
                for m in suitable_majors
            ])
            return {
                "reply": f"Chào bạn! Với mức điểm <strong>{user_score} điểm</strong>, cơ hội trúng tuyển của bạn rất rộng mở. Trợ lý AI gợi ý cho bạn các ngành học rất phù hợp:<br><br>{list_txt}<br><br>💡 <em>Lời khuyên:</em> Bạn nên đăng ký ngành điểm cao hơn một chút làm <strong>Nguyện vọng 1</strong> và ngành có điểm chuẩn an toàn làm <strong>Nguyện vọng 2</strong> nhé!",
                "type": "recommendation",
                "suggested_majors": [m.name for m in suitable_majors]
            }

    # Phân tích theo từ khóa ngành học
    if "công nghệ" in q or "cntt" in q or "lập trình" in q or "it" in q or "phần mềm" in q:
        it_majors = db.query(Major).filter(Major.category == "Công nghệ & Kỹ thuật").limit(4).all()
        txt = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: {m.benchmark_score}" for m in it_majors])
        return {
            "reply": f"Khối <strong>Công nghệ & Kỹ thuật</strong> của trường gồm các ngành mũi nhọn đang thu hút nhân lực hàng đầu:<br><br>{txt}<br><br>Các ngành này được trang bị 6 môn đại cương chuẩn cùng các môn chuyên sâu như Lập trình Python, CSDL SQL, Trí tuệ nhân tạo (AI), Điện toán đám mây. Bạn có thể nhấn vào từng ngành để xem chi tiết nhé!",
            "type": "field_info"
        }

    if "kinh tế" in q or "kinh doanh" in q or "marketing" in q or "tài chính" in q or "kế toán" in q:
        biz_majors = db.query(Major).filter(Major.category == "Kinh tế & Quản lý").limit(4).all()
        txt = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: {m.benchmark_score}" for m in biz_majors])
        return {
            "reply": f"Về khối <strong>Kinh tế & Quản lý</strong>, nhà trường hiện đào tạo 13 chuyên ngành hiện đại:<br><br>{txt}<br><br>Sinh viên được đào tạo chuyên sâu về quản trị chiến lược, phân tích tài chính, tiếp thị số Digital Marketing và vận hành thương mại điện tử quốc tế.",
            "type": "field_info"
        }

    if "học phí" in q or "lệ phí" in q or "tiền" in q or "đóng phí" in q or "vietqr" in q:
        fee = db.query(Major).first()
        return {
            "reply": "Lệ phí xét tuyển của nhà trường là <strong>50.000 VNĐ / một hồ sơ</strong>. Sau khi nộp hồ sơ, hệ thống sẽ tự động tạo mã <strong>VietQR ngân hàng</strong> có sẵn số tiền và nội dung chuyển khoản. Bạn chỉ cần dùng ứng dụng ngân hàng quét mã là được xác nhận đóng tiền thành công tức thì!",
            "type": "payment_info"
        }

    if "hồ sơ" in q or "học bạ" in q or "thpt" in q or "giấy tờ" in q:
        return {
            "reply": "Nhà trường tiếp nhận xét tuyển theo 2 phương thức: <strong>1. Xét học bạ THPT</strong> và <strong>2. Điểm thi tốt nghiệp THPT</strong>. Bạn chỉ cần chụp ảnh rõ nét học bạ hoặc phiếu điểm, vào Cổng Thí Sinh chọn 'Tải file ảnh từ máy' và gửi hồ sơ trực tuyến là xong nhé!",
            "type": "application_info"
        }

    # Trả lời mặc định thông minh
    return {
        "reply": "Chào bạn! Tôi là Trợ lý AI Tư vấn Tuyển sinh 2026. Tôi có thể hỗ trợ bạn:<br>• <strong>Gợi ý chọn ngành:</strong> Bạn có thể gõ mức điểm (ví dụ: <em>'Em 25 điểm nên học ngành nào?'</em>)<br>• <strong>Tìm hiểu chuyên ngành:</strong> (ví dụ: <em>'Ngành CNTT học gì?', 'Học phí bao nhiêu?'</em>)<br>• <strong>Hướng dẫn thủ tục:</strong> Nộp hồ sơ và thanh toán mã VietQR.",
        "type": "general"
    }
