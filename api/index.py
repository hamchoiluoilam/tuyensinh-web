import sys
import os

# Đảm bảo thư mục gốc dự án nằm trong sys.path để import toàn bộ module app
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from main import app as fastapi_app

class VercelPathFixMiddleware:
    """
    ASGI Middleware đặc trị lỗi 404 {"detail": "Not Found"} trên Vercel:
    Khi Vercel cấu hình rewrites: /(.*) -> /api/index.py, Vercel gửi đường dẫn tới hàm
    kèm header 'x-matched-path' (chứa URL gốc như '/', '/login', '/student', '/admin').
    Middleware này khôi phục chính xác scope['path'] về URL gốc trước khi FastAPI xử lý.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            
            # 1. Ưu tiên lấy đường dẫn thật từ header x-matched-path do Vercel cấp
            matched_path = headers.get(b"x-matched-path")
            if matched_path:
                decoded = matched_path.decode("utf-8").split("?")[0]
                scope["path"] = decoded if decoded else "/"
            else:
                # 2. Xóa tiền tố /api/index.py nếu bị dính trong scope['path']
                raw_path = scope.get("path", "")
                for prefix in ("/api/index.py", "/api/index"):
                    if raw_path.startswith(prefix):
                        stripped = raw_path[len(prefix):]
                        scope["path"] = stripped if stripped.startswith("/") else ("/" + stripped)
                        break
                if not scope.get("path"):
                    scope["path"] = "/"
                    
        await self.app(scope, receive, send)

# Xuất biến app chuẩn cho Vercel runtime
app = VercelPathFixMiddleware(fastapi_app)
