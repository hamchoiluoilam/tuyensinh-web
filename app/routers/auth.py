import hashlib
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserRegister, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["Xác thực & Tài khoản"])

def hash_password(password: str) -> str:
    """Băm mật khẩu an toàn với thuật toán SHA-256 kèm muối cố định cho đồ án"""
    salt = "UniAdmission2026SecureSalt$"
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu khớp với chuỗi băm (hoặc plaintext legacy)"""
    return hash_password(plain_password) == hashed_password or plain_password == hashed_password

@router.post("/register", response_model=UserOut)
def register_student(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    """[Thí sinh] Đăng ký tài khoản học sinh bằng Email (mật khẩu được mã hóa băm bảo mật)"""
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký tài khoản!")

    new_user = User(
        email=data.email.lower(),
        password=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role="STUDENT"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Tự động set session cookie sau khi đăng ký
    response.set_cookie(key="user_id", value=str(new_user.id), httponly=True, max_age=86400)
    response.set_cookie(key="user_role", value="STUDENT", httponly=True, max_age=86400)

    return new_user

@router.post("/login")
def login_student(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """[Thí sinh] Đăng nhập bằng Email và Mật khẩu đã được mã hóa"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác!")

    response.set_cookie(key="user_id", value=str(user.id), httponly=True, max_age=86400)
    response.set_cookie(key="user_role", value=user.role, httponly=True, max_age=86400)

    return {
        "message": "Đăng nhập thành công!",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/admin-login")
def login_admin(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """[Cán bộ] Đăng nhập Cổng Quản Trị"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác!")

    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Tài khoản này không có quyền quản trị viên!")

    response.set_cookie(key="user_id", value=str(user.id), httponly=True, max_age=86400)
    response.set_cookie(key="user_role", value="ADMIN", httponly=True, max_age=86400)

    return {
        "message": "Đăng nhập quản trị thành công!",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/logout")
def logout(response: Response):
    """Đăng xuất tài khoản"""
    response.delete_cookie("user_id")
    response.delete_cookie("user_role")
    return {"message": "Đã đăng xuất"}
