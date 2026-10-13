from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from ..database import get_db
from ..models import Major, AdmissionApplication, PaymentTransaction, SupportTicket, FAQItem, FeeConfig, User, Subject

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter(include_in_schema=False)

def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    try:
        return db.query(User).filter(User.id == int(user_id)).first()
    except:
        return None

# --- TRANG CHỦ & CHI TIẾT NGÀNH ---
@router.get("/")
def home_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    majors = db.query(Major).all()
    faqs = db.query(FAQItem).all()
    total_subjects = db.query(Subject).count()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "majors": majors,
        "faqs": faqs,
        "total_subjects": total_subjects
    })

@router.get("/majors/{major_id}")
def major_detail_page(major_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngành học!")

    subjects = db.query(Subject).filter(Subject.major_id == major_id).order_by(Subject.semester, Subject.code).all()
    total_credits = sum(s.credits for s in subjects)

    return templates.TemplateResponse("major_detail.html", {
        "request": request,
        "user": user,
        "major": major,
        "subjects": subjects,
        "total_credits": total_credits
    })

# --- ĐĂNG NHẬP / ĐĂNG KÝ HỌC SINH ---
@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and user.role == "STUDENT":
        return RedirectResponse(url="/student")
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@router.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and user.role == "STUDENT":
        return RedirectResponse(url="/student")
    return templates.TemplateResponse("register.html", {"request": request, "user": None})

@router.get("/logout")
def logout_view():
    resp = RedirectResponse(url="/")
    resp.delete_cookie("user_id")
    resp.delete_cookie("user_role")
    return resp

# --- ĐĂNG NHẬP ADMIN ---
@router.get("/admin/login")
def admin_login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user and user.role == "ADMIN":
        return RedirectResponse(url="/admin")
    return templates.TemplateResponse("admin_login.html", {"request": request, "user": None})

# --- CỔNG HỌC SINH (YÊU CẦU ĐĂNG NHẬP) ---
@router.get("/student")
def student_portal(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?msg=please_login")

    majors = db.query(Major).all()
    fees = db.query(FeeConfig).all()
    # Lấy hồ sơ và ticket của chính học sinh này
    my_applications = db.query(AdmissionApplication).filter(
        (AdmissionApplication.user_id == user.id) | (AdmissionApplication.email == user.email)
    ).order_by(AdmissionApplication.created_at.desc()).all()

    my_tickets = db.query(SupportTicket).filter(
        (SupportTicket.user_id == user.id) | (SupportTicket.sender_email == user.email)
    ).order_by(SupportTicket.created_at.desc()).all()

    return templates.TemplateResponse("student_portal.html", {
        "request": request,
        "user": user,
        "majors": majors,
        "fees": fees,
        "my_applications": my_applications,
        "my_tickets": my_tickets
    })

# --- CỔNG ADMIN (YÊU CẦU QUYỀN ADMIN) ---
@router.get("/admin")
def admin_portal(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/admin/login?msg=admin_required")

    majors = db.query(Major).all()
    applications = db.query(AdmissionApplication).order_by(AdmissionApplication.score.desc()).all()
    transactions = db.query(PaymentTransaction).order_by(PaymentTransaction.created_at.desc()).all()
    tickets = db.query(SupportTicket).order_by(SupportTicket.created_at.desc()).all()
    
    paid_tx = [t for t in transactions if t.status == 'PAID']
    revenue = sum(t.amount for t in paid_tx)

    return templates.TemplateResponse("admin_portal.html", {
        "request": request,
        "user": user,
        "majors": majors,
        "applications": applications,
        "transactions": transactions,
        "tickets": tickets,
        "revenue": revenue,
        "paid_count": len(paid_tx),
        "total_count": len(transactions)
    })

# --- FILE SWAGGER UI RIÊNG & TÀI LIỆU OPENAPI ---
@router.get("/swagger-ui")
def custom_swagger_ui():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "swagger_ui.html"))
    return FileResponse(file_path, media_type="text/html")

@router.get("/swagger_spec.json")
def custom_swagger_spec():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "swagger_spec.json"))
    return FileResponse(file_path, media_type="application/json")
