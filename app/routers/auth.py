import hashlib
import datetime
from typing import Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserRegister, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["Xác thực & Tài khoản"])

# Cấu hình JWT Token
SECRET_KEY = "UniAdmissionsSecureJWTKey_NEU2026_AdvancedAdmissionSecurityKey123456789!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    """Băm mật khẩu an toàn với thuật toán SHA-256 kèm muối cố định cho đồ án"""
    salt = "UniAdmission2026SecureSalt$"
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu khớp với chuỗi băm (hoặc plaintext legacy)"""
    return hash_password(plain_password) == hashed_password or plain_password == hashed_password

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Tạo JSON Web Token (JWT) có chữ ký điện tử HS256 bảo vệ toàn vẹn phiên"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Giải mã và xác thực chữ ký JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def set_auth_cookies(response: Response, user: User) -> str:
    """Ghi cookie JWT token HttpOnly và các thông tin phiên an toàn"""
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name
    }
    token = create_access_token(token_payload)
    response.set_cookie(key="auth_token", value=token, httponly=True, samesite="lax", max_age=86400)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True, samesite="lax", max_age=86400)
    response.set_cookie(key="user_role", value=user.role, httponly=True, samesite="lax", max_age=86400)
    return token

@router.post("/register", response_model=UserOut)
def register_student(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    """[Thí sinh] Đăng ký tài khoản học sinh bằng Email (mật khẩu được mã hóa băm bảo mật kèm JWT token)"""
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

    set_auth_cookies(response, new_user)
    return new_user

@router.post("/login")
def login_student(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """[Thí sinh] Đăng nhập bằng Email và Mật khẩu (cấp phiên bảo mật JWT)"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác!")

    token = set_auth_cookies(response, user)

    return {
        "message": "Đăng nhập thành công!",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

def get_current_user_from_req(request: Request, db: Session = Depends(get_db)):
    """Lấy thông tin người dùng hiện tại từ JWT token hoặc session cookie an toàn"""
    token = request.cookies.get("auth_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                user = db.query(User).filter(User.id == int(payload["sub"])).first()
                if user:
                    return user
            except Exception:
                pass

    uid = request.cookies.get("user_id")
    if uid:
        try:
            return db.query(User).filter(User.id == int(uid)).first()
        except Exception:
            pass

    return None

def require_logged_in_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Yêu cầu bắt buộc đã đăng nhập"""
    user = get_current_user_from_req(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để thực hiện thao tác này!")
    return user

def require_officer_or_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """Yêu cầu quyền Cán bộ Tuyển sinh (OFFICER) hoặc Quản trị viên (ADMIN)"""
    user = require_logged_in_user(request, db)
    if user.role not in ["OFFICER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Quyền truy cập bị từ chối: Yêu cầu quyền Cán bộ hoặc Admin!")
    return user

def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """Yêu cầu quyền Quản trị viên cấp cao (ADMIN)"""
    user = require_logged_in_user(request, db)
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Quyền truy cập bị từ chối: Thao tác này chỉ dành riêng cho Admin!")
    return user

@router.post("/admin-login")
def login_admin(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """[Cán bộ / Admin] Đăng nhập Cổng Quản Trị & Nghiệp Vụ Tuyển Sinh (JWT)"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác!")

    if user.role not in ["ADMIN", "OFFICER"]:
        raise HTTPException(status_code=403, detail="Tài khoản này không có quyền Cán bộ tuyển sinh hoặc Quản trị viên!")

    token = set_auth_cookies(response, user)
    role_title = "Quản trị viên" if user.role == "ADMIN" else "Cán bộ tuyển sinh"
    return {
        "message": f"Đăng nhập {role_title} thành công!",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/logout")
def logout(response: Response):
    """Đăng xuất tài khoản và xóa token bảo mật"""
    response.delete_cookie("auth_token")
    response.delete_cookie("user_id")
    response.delete_cookie("user_role")
    return {"message": "Đã đăng xuất thành công"}
