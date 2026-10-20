import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

# ==========================================================
# AUTH & TÀI KHOẢN NGƯỜI DÙNG (Dành cho Học Sinh & Admin)
# ==========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False) # Đã được mã hóa băm mật khẩu
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default="STUDENT") # STUDENT hoặc ADMIN
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    applications = relationship("AdmissionApplication", back_populates="user")
    tickets = relationship("SupportTicket", back_populates="user")


# ==========================================================
# MODULE 1 (Người 1 - M02): TUYỂN SINH & HỒ SƠ XÉT TUYỂN
# ==========================================================
class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False) # VD: 7480201 (CNTT)
    name = Column(String(200), nullable=False)                         # Công nghệ thông tin
    category = Column(String(100), default="Công nghệ & Kỹ thuật")     # Khối ngành
    description = Column(Text, nullable=True)                          # Giới thiệu ngành học & chuẩn đầu ra
    quota = Column(Integer, default=50)                               # Chỉ tiêu tuyển sinh
    benchmark_score = Column(Float, default=0.0)                      # Điểm chuẩn trúng tuyển (sau lọc ảo)

    applications = relationship("AdmissionApplication", back_populates="major", foreign_keys="[AdmissionApplication.major_id]")
    applications_nv2 = relationship("AdmissionApplication", back_populates="major_nv2", foreign_keys="[AdmissionApplication.major_nv2_id]")
    subjects = relationship("Subject", back_populates="major", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), index=True, nullable=False)              # VD: GEN101, IT101, BA203
    name = Column(String(200), nullable=False)                         # Tên môn học
    credits = Column(Integer, default=3)                               # Số tín chỉ (2, 3, 4)
    semester = Column(Integer, default=1)                              # Học kỳ (1 đến 8)
    subject_type = Column(String(50), default="Cơ sở ngành")          # Đại cương, Cơ sở ngành, Chuyên ngành
    description = Column(Text, nullable=True)                          # Tóm tắt nội dung môn học

    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    major = relationship("Major", back_populates="subjects")

class AdmissionApplication(Base):
    __tablename__ = "admission_applications"

    id = Column(Integer, primary_key=True, index=True)
    app_code = Column(String(50), unique=True, index=True, nullable=False) # Mã hồ sơ TS2026-XXXX
    full_name = Column(String(150), nullable=False)
    id_card = Column(String(20), index=True, nullable=False)              # Số CCCD
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    method = Column(String(50), nullable=False)                          # HOC_BA hoặc THPT
    score = Column(Float, nullable=False)                                # Tổng điểm xét tuyển
    proof_url = Column(Text, nullable=True)                              # Link ảnh hoặc đường dẫn file tải lên
    admitted_major_name = Column(String(200), nullable=True)             # Ngành trúng tuyển thực tế (NV1 hay NV2)

    # Nguyện vọng 1 (bắt buộc)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    major = relationship("Major", back_populates="applications", foreign_keys=[major_id])

    # Nguyện vọng 2 (tùy chọn)
    major_nv2_id = Column(Integer, ForeignKey("majors.id"), nullable=True)
    major_nv2 = relationship("Major", back_populates="applications_nv2", foreign_keys=[major_nv2_id])

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="applications")

    status = Column(String(50), default="CHO_DUYET") 
    # Trạng thái: CHO_DUYET, HOP_LE, TU_CHOI, TRUNG_TUYEN_NV1, TRUNG_TUYEN_NV2, KHONG_TRUNG_TUYEN
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Liên kết sang Module Finance (M07) và Support (M12)
    payment = relationship("PaymentTransaction", back_populates="application", uselist=False)
    tickets = relationship("SupportTicket", back_populates="application")


# ==========================================================
# MODULE 2 (Người 2 - M07): TÀI CHÍNH & LỆ PHÍ XÉT TUYỂN
# ==========================================================
class FeeConfig(Base):
    __tablename__ = "fee_configs"

    id = Column(Integer, primary_key=True, index=True)
    fee_name = Column(String(150), nullable=False)     # VD: Lệ phí xét tuyển đại học 2026
    amount = Column(Float, default=50000.0)            # 50.000 VNĐ / hồ sơ
    description = Column(String(255), nullable=True)

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_code = Column(String(60), unique=True, index=True, nullable=False) # Mã giao dịch PAY-XXXX
    application_id = Column(Integer, ForeignKey("admission_applications.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(50), default="QR_CHUYEN_KHOAN")
    status = Column(String(30), default="UNPAID")         # UNPAID, PAID, FAILED
    qr_payload = Column(Text, nullable=True)              # Dữ liệu nội dung chuyển khoản / QR
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("AdmissionApplication", back_populates="payment")


# ==========================================================
# MODULE 3 (Người 3 - M12): HỖ TRỢ NGƯỜI HỌC (TICKETING & FAQ)
# ==========================================================
class FAQItem(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), default="Chung")    # Hồ sơ, Lệ phí, Quy chế
    question = Column(String(300), nullable=False)
    answer = Column(Text, nullable=False)

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(50), unique=True, index=True, nullable=False) # TK-XXXX
    application_id = Column(Integer, ForeignKey("admission_applications.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="tickets")

    sender_name = Column(String(150), nullable=False)
    sender_email = Column(String(120), nullable=False)
    sender_phone = Column(String(20), nullable=True)
    category = Column(String(100), default="Thắc mắc hồ sơ")
    subject = Column(String(250), nullable=False)
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=True)
    status = Column(String(30), default="PENDING") # PENDING, RESOLVED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    application = relationship("AdmissionApplication", back_populates="tickets")
