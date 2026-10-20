from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==================== AUTH SCHEMAS ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SUBJECT & MAJOR SCHEMAS ====================
class SubjectOut(BaseModel):
    id: int
    code: str
    name: str
    credits: int
    semester: int
    subject_type: str
    description: Optional[str]

    class Config:
        from_attributes = True

class MajorOut(BaseModel):
    id: int
    code: str
    name: str
    category: Optional[str] = "Chung"
    description: Optional[str]
    quota: int
    benchmark_score: float

    class Config:
        from_attributes = True

class MajorUpdateQuota(BaseModel):
    quota: int
    benchmark_score: Optional[float] = None

class MajorDetailOut(MajorOut):
    subjects: List[SubjectOut] = []

    class Config:
        from_attributes = True


# ==================== M02 ADMISSIONS SCHEMAS ====================
class ApplicationCreate(BaseModel):
    full_name: str
    id_card: str
    email: EmailStr
    phone: str
    method: str # HOC_BA or THPT
    score: float
    major_id: int # Nguyện vọng 1
    major_nv2_id: Optional[int] = None # Nguyện vọng 2
    proof_url: Optional[str] = None
    user_id: Optional[int] = None

class ApplicationStatusUpdate(BaseModel):
    status: str # HOP_LE, TU_CHOI, etc.

class ApplicationOut(BaseModel):
    id: int
    app_code: str
    full_name: str
    id_card: str
    email: str
    phone: str
    method: str
    score: float
    status: str
    major_id: int
    major_nv2_id: Optional[int] = None
    admitted_major_name: Optional[str] = None
    user_id: Optional[int] = None
    proof_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== M07 FINANCE SCHEMAS ====================
class PaymentCreate(BaseModel):
    application_id: int
    method: Optional[str] = "QR_CHUYEN_KHOAN"

class FeeConfigUpdate(BaseModel):
    amount: float
    fee_name: Optional[str] = None
    description: Optional[str] = None

class PaymentSimulate(BaseModel):
    tx_code: str

class PaymentOut(BaseModel):
    id: int
    tx_code: str
    application_id: int
    amount: float
    method: str
    status: str
    qr_payload: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== M12 SUPPORT SCHEMAS ====================
class FAQOut(BaseModel):
    id: int
    category: str
    question: str
    answer: str

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    sender_name: str
    sender_email: EmailStr
    sender_phone: Optional[str] = None
    category: str
    subject: str
    message: str
    application_id: Optional[int] = None
    user_id: Optional[int] = None

class TicketReply(BaseModel):
    reply: str

class TicketOut(BaseModel):
    id: int
    ticket_code: str
    sender_name: str
    sender_email: str
    category: str
    subject: str
    message: str
    reply: Optional[str]
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class AIChatQuery(BaseModel):
    query: str
    score: Optional[float] = None
