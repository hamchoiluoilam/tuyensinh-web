# HỆ THỐNG TUYỂN SINH & TƯ VẤN NHẬP HỌC TRỰC TUYẾN (UniAdmission 2026)

## 🎯 PHÁT BIỂU BÀI TOÁN & MỤC TIÊU HỆ THỐNG
* **Phát biểu nhiệm vụ cụ thể:** *Xây dựng một hệ thống Web giải quyết hoàn chỉnh quy trình tuyển sinh đại học trực tuyến: Tiếp nhận hồ sơ xét tuyển theo phương thức Học bạ/Điểm thi THPT cho 40 ngành đào tạo, quản lý và thu nộp lệ phí xét tuyển tự động qua mã VietQR, và cung cấp tiện ích giải đáp thắc mắc (Ticket & FAQ) cho thí sinh.*
* **Backend:** Python (FastAPI + SQLAlchemy ORM).
* **Cơ sở dữ liệu:** SQLite / PostgreSQL / MySQL (mặc định SQLite zero-config).
* **Phân quyền người dùng:**
  * **Người dùng chính (Học sinh/Thí sinh):** Đăng ký tài khoản bằng email riêng, đăng nhập, nộp hồ sơ, quét mã QR đóng lệ phí, gửi ticket thắc mắc.
  * **Người quản trị (Admin/Cán bộ):** Quản trị danh mục 40 ngành và chỉ tiêu, duyệt hồ sơ hợp lệ, **chạy thuật toán lọc ảo & xét điểm chuẩn tự động**, đối soát doanh thu lệ phí, trả lời ticket hỗ trợ.

---

## 📑 TÀI LIỆU SWAGGER UI RIÊNG
Dự án được tạo sẵn file Swagger UI riêng biệt và OpenAPI JSON specification:
* **File HTML Swagger UI riêng:** [`swagger_ui.html`](file:///C:/Users/Admin/.gemini/antigravity/scratch/admission_portal/swagger_ui.html) *(có thể mở trực tiếp trong trình duyệt hoặc truy cập qua đường dẫn `http://127.0.0.1:8000/swagger-ui`)*
* **File đặc tả OpenAPI Spec JSON:** [`swagger_spec.json`](file:///C:/Users/Admin/.gemini/antigravity/scratch/admission_portal/swagger_spec.json) *(chuẩn OpenAPI 3.0 xuất file trong thư mục gốc)*

---

## 🎓 DANH SÁCH 40 NGÀNH TUYỂN SINH & CHỈ TIÊU (M02)
Hệ thống nạp sẵn đầy đủ **40 ngành đào tạo đại học chính quy** chuẩn Bộ GD&ĐT phân bổ theo 4 khối ngành lớn, mỗi ngành có chương trình đào tạo các môn học chi tiết:

1. **Khối Công nghệ & Kỹ thuật (14 ngành):**
   * Công nghệ thông tin (7480201) | Khoa học máy tính (7480101) | Kỹ thuật phần mềm (7480103)
   * An toàn thông tin (7480202) | Trí tuệ nhân tạo (7480107) | Khoa học dữ liệu (7480108)
   * Mạng máy tính & Truyền thông (7480204) | Hệ thống thông tin quản lý (7480104)
   * Kỹ thuật điều khiển & Tự động hóa (7520216) | Kỹ thuật cơ điện tử (7520114)
   * Kỹ thuật ô tô (7520130) | Kỹ thuật điện tử - viễn thông (7520207)
   * Thiết kế vi mạch & Bán dẫn (7520215) | Kỹ thuật xây dựng (7580201)

2. **Khối Kinh tế & Quản lý (13 ngành):**
   * Quản trị kinh doanh (7340101) | Marketing & Truyền thông số (7340115) | Kinh doanh quốc tế (7340120)
   * Tài chính - Ngân hàng (7340201) | Kế toán (7340301) | Kiểm toán (7340302)
   * Thương mại điện tử (7340122) | Logistics & Chuỗi cung ứng (7510605) | Quản trị nhân lực (7340404)
   * Luật kinh tế (7380107) | Kinh tế đối ngoại (7310106)
   * Quản trị du lịch & lữ hành (7810103) | Quản trị khách sạn (7810201)

3. **Khối Ngoại ngữ & Xã hội (8 ngành):**
   * Ngôn ngữ Anh (7220201) | Ngôn ngữ Trung Quốc (7220204) | Ngôn ngữ Nhật (7220209)
   * Ngôn ngữ Hàn Quốc (7220210) | Quan hệ công chúng (7320108)
   * Báo chí & Truyền thông đa phương tiện (7320101) | Thiết kế đồ họa (7210403) | Tâm lý học (7310401)

4. **Khối Y Dược, Sinh học & Kiến trúc (5 ngành):**
   * Y khoa (Bác sĩ đa khoa) (7720101) | Dược học (7720201) | Điều dưỡng (7720301)
   * Công nghệ sinh học (7420201) | Kiến trúc (7580101)

---

## 👥 PHÂN CHIA TRÁCH NHIỆM 3 MODULE (3 THÀNH VIÊN)

| Thành viên | Phân hệ đảm nhiệm | File code chính | Chức năng nghiệp vụ cụ thể |
|---|---|---|---|
| **Người 1** | **M02 – Tuyển sinh** | `app/routers/admissions.py`<br>`app/models.py` (`Major`, `Subject`, `AdmissionApplication`) | • Quản lý danh mục 40 ngành đào tạo, chỉ tiêu và khung môn học<br>• Nộp hồ sơ xét tuyển trực tuyến, sinh mã `TS2026-XXXX`<br>• Cán bộ duyệt hồ sơ (Hợp lệ / Từ chối)<br>• **Thuật toán lọc ảo & tính điểm chuẩn**: Tự động xét top thí sinh hợp lệ & đã đóng lệ phí theo chỉ tiêu, xác định điểm chuẩn và set trạng thái `TRUNG_TUYEN`. |
| **Người 2** | **M07 – Tài chính – Kế toán** | `app/routers/finance.py`<br>`app/models.py` (`FeeConfig`, `PaymentTransaction`) | • Quản lý biểu phí xét tuyển (50.000 VNĐ)<br>• Tự động tạo mã giao dịch `PAY-TS2026-XXXX`<br>• Sinh mã VietQR chuyển khoản ngân hàng tự động kèm nội dung memo<br>• Cổng giả lập thanh toán (webhook demo xác nhận `PAID`)<br>• Dashboard thống kê tổng thu lệ phí, tỷ lệ hoàn tất nộp tiền. |
| **Người 3** | **M12 – Hỗ trợ người học** | `app/routers/support.py`<br>`app/models.py` (`FAQItem`, `SupportTicket`) | • Danh mục câu hỏi thường gặp (FAQ) theo chủ đề<br>• Thí sinh gửi phiếu yêu cầu hỗ trợ (Ticket `TK-XXXX`)<br>• Thí sinh tra cứu kết quả giải đáp cá nhân<br>• Cán bộ tư vấn tiếp nhận, trả lời thắc mắc và đóng ticket (`RESOLVED`). |

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

1. Mở PowerShell tại thư mục:
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\admission_portal
```

2. Khởi động Web Server:
```powershell
python main.py
```

3. Truy cập trình duyệt:
* **Trang chủ & Danh sách 40 ngành:** `http://127.0.0.1:8000/`
* **File Swagger UI riêng:** `http://127.0.0.1:8000/swagger-ui` (hoặc mở trực tiếp file `swagger_ui.html`)
* **Đăng nhập thí sinh:** `http://127.0.0.1:8000/login` *(hoặc Đăng ký tại `/register`)*
* **Cổng quản trị viên Admin:** `http://127.0.0.1:8000/admin/login`
  * Tài khoản admin: `admin@tuyensinh.edu.vn` / Mật khẩu: `admin123`
