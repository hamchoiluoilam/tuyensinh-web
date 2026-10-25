import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tương thích với môi trường Serverless của Vercel (chỉ thư mục /tmp được phép ghi)
is_serverless = (
    not os.access(BASE_DIR, os.W_OK)
    or any(k in os.environ for k in ["VERCEL", "VERCEL_ENV", "AWS_LAMBDA_FUNCTION_NAME", "LAMBDA_TASK_ROOT"])
)

if is_serverless:
    DB_PATH = "/tmp/admission_system.db"
    orig_db = os.path.join(BASE_DIR, "admission_system.db")
    if not os.path.exists(DB_PATH) and os.path.exists(orig_db):
        try:
            shutil.copy2(orig_db, DB_PATH)
        except Exception as e:
            print(f"[Vercel SQLite Notice] Error copying DB to /tmp: {e}")
else:
    DB_PATH = os.path.join(BASE_DIR, "admission_system.db").replace("\\", "/")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
