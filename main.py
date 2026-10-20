import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import datetime

from app.database import engine, Base, SessionLocal
from app.models import Major, Subject, FeeConfig, FAQItem, AdmissionApplication, PaymentTransaction, SupportTicket, User
from app.routers import admissions, finance, support, web_views, auth
from app.routers.auth import hash_password

# Tạo thư mục upload ảnh thật nếu chưa có
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "app", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Tạo bảng dữ liệu
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hệ Thống Tuyển Sinh & Tư Vấn Nhập Học Trực Tuyến",
    description="Đồ án Web Python 3 Phân hệ: M02 (Tuyển sinh) + M07 (Tài chính - Lệ phí) + M12 (Hỗ trợ người học)",
    version="2.0.0"
)

# Cấu hình Static Files cho Uploads & Assets
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "app", "static")), name="static")

# Đăng ký các router
app.include_router(auth.router)
app.include_router(admissions.router)
app.include_router(finance.router)
app.include_router(support.router)
app.include_router(web_views.router)

@app.on_event("startup")
def seed_demo_data():
    db = SessionLocal()
    try:
        # 1. Tạo tài khoản mẫu (Admin & Học sinh) với mật khẩu bảo mật băm SHA-256 + Salt
        if db.query(User).count() == 0:
            admin_user = User(
                email="admin@tuyensinh.edu.vn",
                password=hash_password("admin123"),
                full_name="Quản Trị Viên Tuyển Sinh",
                phone="0243888999",
                role="ADMIN"
            )
            student_user = User(
                email="student@gmail.com",
                password=hash_password("123456"),
                full_name="Nguyễn Văn An",
                phone="0987654321",
                role="STUDENT"
            )
            db.add_all([admin_user, student_user])
            db.commit()

        # 2. Tạo 40 ngành tuyển sinh và các môn học chi tiết
        from app.seed_data import MAJORS_40
        if db.query(Major).count() == 0:
            for m_item in MAJORS_40:
                major_obj = Major(
                    code=m_item["code"],
                    name=m_item["name"],
                    category=m_item["category"],
                    quota=m_item["quota"],
                    benchmark_score=m_item["benchmark_score"],
                    description=m_item["description"]
                )
                db.add(major_obj)
                db.commit()
                db.refresh(major_obj)

                # Thêm các môn học thuộc ngành này
                for s_item in m_item["subjects"]:
                    subj = Subject(
                        code=s_item[0],
                        name=s_item[1],
                        credits=s_item[2],
                        semester=s_item[3],
                        subject_type=s_item[4],
                        description=s_item[5],
                        major_id=major_obj.id
                    )
                    db.add(subj)
            db.commit()


        # 4. Biểu phí
        if db.query(FeeConfig).count() == 0:
            fee = FeeConfig(fee_name="Lệ phí xét tuyển đợt 1 năm 2026", amount=50000.0, description="Phí xét tuyển 1 nguyện vọng")
            db.add(fee)
            db.commit()

        # 5. Câu hỏi thường gặp FAQ
        if db.query(FAQItem).count() == 0:
            faqs = [
                FAQItem(category="Hồ sơ", question="Phương thức xét học bạ cần chuẩn bị những gì?", answer="Thí sinh chụp ảnh rõ nét học bạ THPT (các học kỳ theo tổ hợp xét tuyển) và số CCCD để điền vào form đăng ký."),
                FAQItem(category="Lệ phí", question="Lệ phí xét tuyển là bao nhiêu và nộp như thế nào?", answer="Mỗi hồ sơ xét tuyển có lệ phí là 50,000 VNĐ. Thí sinh quét mã VietQR tự động trên hệ thống để hoàn tất nộp tiền."),
                FAQItem(category="Quy chế", question="Khi nào có điểm chuẩn trúng tuyển?", answer="Sau khi kết thúc thời gian đăng ký và lọc ảo, nhà trường sẽ công bố điểm chuẩn và danh sách trúng tuyển chính thức trên hệ thống."),
            ]
            db.add_all(faqs)
            db.commit()

        # 6. Hồ sơ mẫu
        if db.query(AdmissionApplication).count() == 0:
            it = db.query(Major).filter(Major.code == "7480201").first() # CNTT
            se = db.query(Major).filter(Major.code == "7480103").first() # Kỹ thuật phần mềm
            if not se:
                se = db.query(Major).filter(Major.id != it.id).first()
            student = db.query(User).filter(User.role == "STUDENT").first()
            
            sample_candidates = [
                {"name": "Trần Thị Ánh", "cccd": "001202001111", "score": 27.5, "paid": True, "uid": None},
                {"name": "Nguyễn Văn An", "cccd": "001202002222", "score": 26.0, "paid": True, "uid": student.id}, # Thuộc về student
                {"name": "Phạm Quang Cường", "cccd": "001202003333", "score": 25.0, "paid": True, "uid": None},
                {"name": "Hoàng Minh Đức", "cccd": "001202004444", "score": 24.5, "paid": False, "uid": None},
                {"name": "Đỗ Thu Trang", "cccd": "001202005555", "score": 23.0, "paid": True, "uid": None},
            ]
            for idx, c in enumerate(sample_candidates, start=1):
                app_code = f"TS2026-10000{idx}"
                app = AdmissionApplication(
                    app_code=app_code,
                    full_name=c["name"],
                    id_card=c["cccd"],
                    email="student@gmail.com" if c["uid"] else f"candidate{idx}@gmail.com",
                    phone=f"091234560{idx}",
                    method="HOC_BA",
                    score=c["score"],
                    major_id=it.id if it else 1,
                    major_nv2_id=se.id if se else None,
                    proof_url="/static/uploads/default_proof.png",
                    user_id=c["uid"],
                    status="HOP_LE"
                )
                db.add(app)
                db.commit()

                tx = PaymentTransaction(
                    tx_code=f"PAY-{app_code}",
                    application_id=app.id,
                    amount=50000.0,
                    status="PAID" if c["paid"] else "UNPAID",
                    paid_at=datetime.datetime.utcnow() if c["paid"] else None,
                    qr_payload=f"2vcb://pay?acc=99998888&amount=50000&memo=PAY-{app_code}"
                )
                db.add(tx)
                db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
