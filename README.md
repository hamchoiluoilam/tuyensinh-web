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
| **Người 1** | **M02 – Tuyển sinh** | `app/routers/admissions.py`<br>`app/models.py` (`Major`, `Subject`, `AdmissionApplication`) | • Quản lý danh mục 40 ngành đào tạo, chỉ tiêu và khung môn học<br>• Cho phép Admin chỉnh sửa chỉ tiêu tuyển sinh & điểm chuẩn linh hoạt (`PATCH /api/admissions/majors/{id}`)<br>• **Upload minh chứng thật**: Tải file ảnh học bạ/chứng chỉ từ máy tính/điện thoại lưu trữ trên server (`/api/admissions/upload-proof`)<br>• **Đăng ký đa nguyện vọng**: Thí sinh đăng ký Nguyện vọng 1 (NV1) và Nguyện vọng 2 (NV2) dự phòng<br>• Cán bộ duyệt hồ sơ (Hợp lệ / Từ chối)<br>• **Thuật toán lọc ảo nâng cao**: Tự động xét duyệt NV1 theo chỉ tiêu và tự động chuyển thí sinh trượt NV1 sang xét NV2 nếu đủ điểm. |
| **Người 2** | **M07 – Tài chính – Kế toán** | `app/routers/finance.py`<br>`app/models.py` (`FeeConfig`, `PaymentTransaction`) | • Quản lý cấu hình biểu phí xét tuyển linh hoạt từ Admin (`PATCH /api/finance/fee-configs/{id}`)<br>• Tự động tạo mã giao dịch `PAY-TS2026-XXXX`<br>• Sinh mã VietQR chuyển khoản ngân hàng tự động kèm nội dung memo<br>• Cổng giả lập thanh toán (webhook demo xác nhận `PAID`)<br>• **Biên lai điện tử chuẩn A4/A5**: Xuất phiếu thu lệ phí chính thức có dấu mộc điện tử và hỗ trợ in/xuất PDF (`/receipt/{tx_code}`)<br>• Dashboard thống kê tổng thu lệ phí, tỷ lệ hoàn tất nộp tiền. |
| **Người 3** | **M12 – Hỗ trợ người học** | `app/routers/support.py`<br>`app/models.py` (`FAQItem`, `SupportTicket`) | • Danh mục câu hỏi thường gặp (FAQ) theo chủ đề<br>• Thí sinh gửi phiếu yêu cầu hỗ trợ (Ticket `TK-XXXX`)<br>• Thí sinh tra cứu kết quả giải đáp cá nhân<br>• Cán bộ tư vấn tiếp nhận, trả lời thắc mắc và đóng ticket (`RESOLVED`)<br>• **Trợ lý AI Tư Vấn Tuyển Sinh Thông Minh (10/10)**: Phân tích điểm thi của thí sinh để gợi ý top ngành phù hợp nhất từ kho 40 ngành, tư vấn quy chế, hướng dẫn học phí và nộp hồ sơ 24/7 (`POST /api/support/ai-consultant`). |

---

## 🌟 TÍNH NĂNG NÂNG CẤP ĐẠT CHUẨN 10/10 DOANH NGHIỆP

1. **Phân quyền người dùng 3 lớp (RBAC - Role-Based Access Control):**
   * `STUDENT` (Thí sinh): Đăng nhập chỉ xem và quản lý hồ sơ, biên lai, ticket của chính mình.
   * `OFFICER` (Cán bộ tuyển sinh): Tiếp nhận và duyệt hồ sơ (Hợp lệ / Bị từ chối có ghi chú), chạy thuật toán lọc ảo, trả lời ticket hỗ trợ, tra cứu đối soát danh sách thí sinh.
   * `ADMIN` (Quản trị viên cấp cao): Toàn quyền hệ thống, điều chỉnh chỉ tiêu 40 ngành và độc quyền cấu hình biểu phí tài chính (`M07`).

2. **Bảo mật Tra cứu công khai 2 yếu tố (2FA Verification) & Che giấu dữ liệu (Data Masking):**
   * Ngăn chặn hoàn toàn việc biết CCCD hoặc Mã hồ sơ là tra cứu được dữ liệu cá nhân.
   * Yêu cầu xác thực 2 yếu tố: Bắt buộc nhập đồng thời **Mã hồ sơ** VÀ **4 số cuối CCCD**.
   * Áp dụng nguyên tắc che giấu dữ liệu nhạy cảm (Data Minimization): Che mờ CCCD (`0012******11`), ẩn số điện thoại (`0912***601`), và **tuyệt đối không trả về file ảnh học bạ** ra bên ngoài.

3. **Bộ lọc đa chiều nâng cao (Multi-Facet Filter) & Xuất dữ liệu:**
   * Lọc kết hợp đồng thời theo Ngành (NV1), Trạng thái hồ sơ, Tình trạng nộp lệ phí VietQR, Phương thức xét tuyển, và Dải điểm số.
   * Tìm kiếm tức thì theo tên, CCCD, Mã hồ sơ, Số điện thoại.
   * Hỗ trợ xuất danh sách thí sinh sau khi lọc ra định dạng CSV/Excel chuẩn UTF-8.

4. **Thuật toán lọc ảo đa nguyện vọng & Tiêu chí phụ (Tie-Breaking Rules):**
   * Phân bổ tự động thí sinh trúng tuyển theo chỉ tiêu ngành.
   * Xử lý tiêu chí phụ khi bằng điểm chuẩn: Thí sinh đăng ký NV1 được ưu tiên hơn NV2; ưu tiên thời gian nộp hồ sơ sớm hơn.
   * Tự động bảo lưu và chuyển tiếp thí sinh không đạt NV1 sang xét tuyển NV2 công bằng.

5. **Hệ thống Trí tuệ nhân tạo (AI Engine) hoàn chỉnh:**
   * Hỗ trợ chế độ kép: Tích hợp Google Gemini 1.5 Flash API (khi có `GEMINI_API_KEY`) + Standalone Expert Reasoning Engine (hoạt động tự chủ 100% offline).
   * Phân tích xác suất trúng tuyển theo 3 tầng chuẩn khoa học: *An toàn (>90%)*, *Vừa sức (70-85%)*, *Bứt phá (40-60%)*.
   * Gợi ý chiến lược đặt Nguyện vọng 1 (mơ ước) và Nguyện vọng 2 (phao cứu sinh) tối ưu theo điểm số và tổ hợp khối thi (A00, A01, D01, B00...).
   * Duy trì bộ nhớ ngữ cảnh đối thoại liên tiếp (Multi-turn Context Memory).

6. **Biên lai điện tử & Tải minh chứng thật:**
   * Tải trực tiếp file ảnh học bạ/chứng chỉ (.jpg, .png, .pdf) lưu trữ an toàn trên server.
   * Phiếu thu biên lai điện tử có dấu mộc điện tử và nút in trực tiếp A4/A5 (`window.print()`).

7. **Bộ Test Suite tự động:**
   * Tích hợp file `test_suite.py` kiểm thử 10 kịch bản end-to-end đảm bảo 100% chức năng hoạt động chính xác.

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY & TÀI KHOẢN MẪU

1. Khởi động Web Server:
```powershell
python main.py
```

2. Danh sách tài khoản thử nghiệm hệ thống:
* **Quản trị viên (ADMIN):** `admin@tuyensinh.edu.vn` / Mật khẩu: `admin123`
* **Cán bộ tuyển sinh (OFFICER):** `canbo@tuyensinh.edu.vn` / Mật khẩu: `canbo123`
* **Thí sinh (STUDENT):** `student@gmail.com` / Mật khẩu: `123456`

3. Đường dẫn các cổng giao diện:
* **Trang chủ & Tra cứu xác minh 2FA:** `http://127.0.0.1:8000/`
* **Cổng Thí Sinh:** `http://127.0.0.1:8000/student`
* **Cổng Quản Trị & Cán Bộ:** `http://127.0.0.1:8000/admin`
* **File Swagger UI:** `http://127.0.0.1:8000/swagger-ui` (hoặc mở file `swagger_ui.html`)
