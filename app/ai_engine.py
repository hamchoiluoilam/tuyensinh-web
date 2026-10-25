"""
AI ADMISSION & CAREER CONSULTANT ENGINE (HỆ THỐNG TRÍ TUỆ NHÂN TẠO TƯ VẤN TUYỂN SINH)
Hỗ trợ chế độ kép:
1. Google Gemini API (khi cấu hình GEMINI_API_KEY hoặc GOOGLE_API_KEY).
2. Autonomous Expert Reasoning & Multi-Factor Matching Engine (Offline / Tự chủ 100%).
"""
import os
import re
import json
import urllib.request
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from .models import Major, Subject

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def call_gemini_api(prompt: str, system_instruction: str, history: Optional[List[dict]] = None) -> Optional[str]:
    """Gọi trực tiếp Google Gemini API qua REST request chuẩn"""
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        contents = []
        if history:
            for msg in history[-6:]:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.get("text", "")}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        body = {
            "contents": contents,
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800
            }
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[Gemini API Notice] Fallback to Autonomous Engine: {e}")
        return None


def normalize_vn(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt thành chữ thường không dấu để so khớp chính xác"""
    s = text.lower()
    mapping = {
        'à':'a','á':'a','ả':'a','ã':'a','ạ':'a','ă':'a','ằ':'a','ắ':'a','ẳ':'a','ẵ':'a','ặ':'a','â':'a','ầ':'a','ấ':'a','ẩ':'a','ẫ':'a','ậ':'a',
        'è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e','ê':'e','ề':'e','ế':'e','ể':'e','ễ':'e','ệ':'e',
        'ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i',
        'ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o','ô':'o','ồ':'o','ố':'o','ổ':'o','ỗ':'o','ộ':'o','ơ':'o','ờ':'o','ớ':'o','ở':'o','ỡ':'o','ợ':'o',
        'ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u','ư':'u','ừ':'u','ứ':'u','ử':'u','ữ':'u','ự':'u',
        'ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y',
        'đ':'d'
    }
    for k, v in mapping.items():
        s = s.replace(k, v)
    return s.strip()


MAJOR_ALIASES = {
    "cntt": "Công nghệ thông tin",
    "it": "Công nghệ thông tin",
    "lap trinh": "Công nghệ thông tin",
    "phan mem": "Kỹ thuật phần mềm",
    "ktpm": "Kỹ thuật phần mềm",
    "khoa hoc may tinh": "Khoa học máy tính",
    "khmt": "Khoa học máy tính",
    "an toan thong tin": "An toàn thông tin",
    "attt": "An toàn thông tin",
    "tri tue nhan tao": "Trí tuệ nhân tạo (AI)",
    "nganh ai": "Trí tuệ nhân tạo (AI)",
    "khoa hoc du lieu": "Khoa học dữ liệu (Data Science)",
    "data science": "Khoa học dữ liệu (Data Science)",
    "mang may tinh": "Mạng máy tính & Truyền thông dữ liệu",
    "he thong thong tin": "Hệ thống thông tin quản lý",
    "httt": "Hệ thống thông tin quản lý",
    "tu dong hoa": "Kỹ thuật điều khiển & Tự động hóa",
    "co dien tu": "Kỹ thuật cơ điện tử",
    "o to": "Kỹ thuật ô tô",
    "oto": "Kỹ thuật ô tô",
    "dien tu vien thong": "Kỹ thuật điện tử - viễn thông",
    "vi mach": "Thiết kế vi mạch & Bán dẫn",
    "ban dan": "Thiết kế vi mạch & Bán dẫn",
    "xay dung": "Kỹ thuật xây dựng",
    "quan tri kinh doanh": "Quản trị kinh doanh",
    "qtkd": "Quản trị kinh doanh",
    "marketing": "Marketing & Truyền thông số",
    "mkt": "Marketing & Truyền thông số",
    "kinh doanh quoc te": "Kinh doanh quốc tế",
    "kdqt": "Kinh doanh quốc tế",
    "tai chinh ngan hang": "Tài chính - Ngân hàng",
    "tcnh": "Tài chính - Ngân hàng",
    "ke toan": "Kế toán doanh nghiệp",
    "kiem toan": "Kiểm toán",
    "thuong mai dien tu": "Thương mại điện tử",
    "tmdt": "Thương mại điện tử",
    "e-commerce": "Thương mại điện tử",
    "logistics": "Logistics & Quản lý chuỗi cung ứng",
    "quan ly chuoi cung ung": "Logistics & Quản lý chuỗi cung ứng",
    "quan tri nhan luc": "Quản trị nhân lực",
    "nhan su": "Quản trị nhân lực",
    "luat": "Luật kinh tế",
    "luat kinh te": "Luật kinh tế",
    "kinh te doi ngoai": "Kinh tế đối ngoại",
    "du lich": "Quản trị dịch vụ du lịch & lữ hành",
    "khach san": "Quản trị khách sạn",
    "ngon ngu anh": "Ngôn ngữ Anh",
    "tieng anh": "Ngôn ngữ Anh",
    "nna": "Ngôn ngữ Anh",
    "ngon ngu trung": "Ngôn ngữ Trung Quốc",
    "tieng trung": "Ngôn ngữ Trung Quốc",
    "ngon ngu nhat": "Ngôn ngữ Nhật",
    "tieng nhat": "Ngôn ngữ Nhật",
    "ngon ngu han": "Ngôn ngữ Hàn Quốc",
    "tieng han": "Ngôn ngữ Hàn Quốc",
    "quan he cong chung": "Quan hệ công chúng (PR)",
    "pr": "Quan hệ công chứng (PR)",
    "bao chi": "Báo chí & Truyền thông đa phương tiện",
    "thiet ke do hoa": "Thiết kế đồ họa",
    "graphic design": "Thiết kế đồ họa",
    "tam ly hoc": "Tâm lý học",
    "y khoa": "Y khoa (Bác sĩ đa khoa)",
    "nganh y": "Y khoa (Bác sĩ đa khoa)",
    "bac si": "Y khoa (Bác sĩ đa khoa)",
    "duoc hoc": "Dược học",
    "nganh duoc": "Dược học",
    "dieu duong": "Điều dưỡng",
    "cong nghe sinh hoc": "Công nghệ sinh học",
    "kien truc": "Kiến trúc"
}


class StandaloneAIAdvisor:
    """
    Công cụ AI Suy luận Chuyên gia Tuyển sinh (Autonomous Expert Reasoning Engine 3.0)
    - Nhận diện thực thể và chủ đích (Intent Recognition):
      + Tra cứu điểm chuẩn, chỉ tiêu và khung môn học của từng ngành cụ thể trong 40 ngành.
      + Giải đáp 4 phương thức xét tuyển (PT1: THPT, PT2: ĐGNL, PT3: IELTS/SAT, PT4: Tuyển thẳng).
      + Lịch trình, hạn nộp hồ sơ, lọc ảo và công bố kết quả.
      + Học phí chương trình chuẩn và tiên tiến, học bổng.
      + Lệ phí xét tuyển 50.000 VNĐ và thanh toán VietQR ngân hàng.
      + Quy trình xác nhận nhập học, cấp MSSV và email trường.
      + Quy trình phúc khảo điểm và rút hồ sơ.
      + Phân tích xác suất đỗ theo điểm thi và khuyến nghị chiến lược NV1 / NV2.
    """

    @staticmethod
    def extract_entities(query: str, explicit_score: Optional[float] = None, explicit_combo: Optional[str] = None):
        q = query.lower()
        score = explicit_score
        if score is None:
            match = re.search(r'(\d{1,2}(?:[\.,]\d{1,2})?)\s*(?:điểm|đ\b|\bpt\b)', q)
            if not match:
                match = re.search(r'(?:được|tầm|khoảng|mức|thi)\s*(\d{1,2}(?:[\.,]\d{1,2})?)', q)
            if match:
                try:
                    val = float(match.group(1).replace(',', '.'))
                    if 10.0 <= val <= 30.0:
                        score = val
                except:
                    pass

        combo = explicit_combo
        if not combo:
            combos = re.findall(r'\b([a-d]\d{2})\b', q, re.IGNORECASE)
            if combos:
                combo = combos[0].upper()

        return score, combo

    @classmethod
    def evaluate_admission_probability(cls, user_score: float, db: Session) -> Dict:
        """Phân tích xác suất trúng tuyển theo 3 tầng khoa học"""
        all_majors = db.query(Major).all()

        safe_majors = []     # Điểm chuẩn <= user_score - 1.0 (Xác suất đỗ > 90%)
        target_majors = []   # user_score - 1.0 < Điểm chuẩn <= user_score + 0.5 (Xác suất đỗ 70-85%)
        reach_majors = []    # user_score + 0.5 < Điểm chuẩn <= user_score + 2.0 (Thử thách 40-60%)

        for m in all_majors:
            delta = user_score - m.benchmark_score
            if delta >= 1.0:
                safe_majors.append(m)
            elif -0.5 <= delta < 1.0:
                target_majors.append(m)
            elif -2.0 <= delta < -0.5:
                reach_majors.append(m)

        safe_majors.sort(key=lambda x: x.benchmark_score, reverse=True)
        target_majors.sort(key=lambda x: x.benchmark_score, reverse=True)
        reach_majors.sort(key=lambda x: x.benchmark_score, reverse=True)

        return {
            "safe": safe_majors[:4],
            "target": target_majors[:4],
            "reach": reach_majors[:3]
        }

    @classmethod
    def find_matched_major(cls, query: str, db: Session) -> Optional[Major]:
        """Tìm ngành học được người dùng nhắc đến trong câu hỏi"""
        norm_q = normalize_vn(query)
        all_majors = db.query(Major).all()

        # 1. Kiểm tra qua từ khóa alias
        for alias, target_name in MAJOR_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, norm_q):
                for m in all_majors:
                    if target_name.lower() in m.name.lower() or m.name.lower() in target_name.lower():
                        return m

        # 2. Kiểm tra trực tiếp tên ngành hoặc mã ngành
        for m in all_majors:
            if m.code in query:
                return m
            norm_name = normalize_vn(m.name)
            if norm_name in norm_q:
                return m

        return None

    @classmethod
    def consult(cls, query: str, user_score: Optional[float], combination: Optional[str], db: Session) -> Dict:
        norm_q = normalize_vn(query)
        extracted_score, extracted_combo = cls.extract_entities(query, user_score, combination)

        # -------------------------------------------------------------
        # 1. TRƯỜNG HỢP CÓ ĐIỂM SỐ + HỎI ĐÍCH DANH MỘT NGÀNH
        # -------------------------------------------------------------
        matched_major = cls.find_matched_major(query, db)
        if matched_major and extracted_score is not None:
            m = matched_major
            score = extracted_score
            diff = round(score - m.benchmark_score, 2)
            if diff >= 1.0:
                chance = "<span class='badge bg-success fs-6'>Xác suất trúng tuyển RẤT CAO (>90%)</span>"
                advice = f"Mức điểm {score} của bạn cao hơn điểm chuẩn ({m.benchmark_score}) tận <strong>+{diff} điểm</strong>. Đây là ngành rất an toàn để bạn đặt làm <strong>Nguyện vọng 1 (NV1)</strong>!"
            elif -0.5 <= diff < 1.0:
                chance = "<span class='badge bg-primary fs-6'>Cơ hội trúng tuyển TỐT (75% - 85%)</span>"
                advice = f"Mức điểm {score} của bạn tiệm cận sát điểm chuẩn ({m.benchmark_score}). Bạn hoàn toàn có thể tự tin đặt ngành này làm <strong>Nguyện vọng 1</strong>, kèm 01 nguyện vọng an toàn hơn làm NV2."
            else:
                chance = "<span class='badge bg-warning text-dark fs-6'>Cần cân nhắc / Nhóm thử thách</span>"
                advice = f"Mức điểm {score} thấp hơn điểm chuẩn tham khảo ({m.benchmark_score}) khoảng <strong>{abs(diff)} điểm</strong>. Bạn có thể đăng ký ngành này ở NV1 để thử sức và nên đăng ký một ngành có điểm chuẩn thấp hơn làm NV2."

            return {
                "reply": (
                    f"🎯 <strong>ĐÁNH GIÁ CƠ HỘI TRÚNG TUYỂN VÀO NGÀNH {m.name.upper()} ({m.code}):</strong><br><br>"
                    f"• Điểm thi của bạn: <strong class='text-primary fs-5'>{score} điểm</strong><br>"
                    f"• Điểm chuẩn tham khảo: <strong class='text-danger fs-5'>{m.benchmark_score} điểm</strong> | Chỉ tiêu: <strong>{m.quota}</strong> SV<br>"
                    f"• Đánh giá cơ hội: {chance}<br><br>"
                    f"💡 <strong>Lời khuyên chiến thuật:</strong> {advice}<br><br>"
                    f"👉 <a href='/major/{m.code}' class='btn btn-sm btn-outline-primary fw-bold mt-1'>"
                    f"<i class='bi bi-journal-bookmark-fill me-1'></i> Xem Chi Tiết Khung Chương Trình Ngành {m.name} &raquo;</a>"
                ),
                "type": "major_score_eval"
            }

        # -------------------------------------------------------------
        # 2. HỎI VỀ MỘT NGÀNH CỤ THỂ (Điểm chuẩn, chỉ tiêu, môn học)
        # -------------------------------------------------------------
        if matched_major:
            m = matched_major
            subj_count = db.query(Subject).filter(Subject.major_id == m.id).count()
            if subj_count == 0:
                subj_count = 29
            return {
                "reply": (
                    f"🎓 <strong>THÔNG TIN TUYỂN SINH NGÀNH: {m.name.upper()} ({m.code})</strong><br><br>"
                    f"• <strong>Khối ngành:</strong> {m.category}<br>"
                    f"• 🎯 <strong>Điểm chuẩn tham khảo:</strong> <span class='badge bg-danger fs-6'>{m.benchmark_score} điểm</span> (Thang điểm 30)<br>"
                    f"• 👥 <strong>Chỉ tiêu tuyển sinh 2026:</strong> <strong>{m.quota}</strong> sinh viên chính quy<br>"
                    f"• 📚 <strong>Quy mô chương trình:</strong> Gồm <strong>{subj_count} học phần</strong> (125-135 tín chỉ) đào tạo xuyên suốt 8 học kỳ (4 năm).<br>"
                    f"• 📝 <strong>Tổ hợp xét tuyển phổ biến:</strong> A00, A01, D01, D07 (hoặc B00 đối với khối Y sinh)<br>"
                    f"• 📖 <strong>Khái quát đào tạo:</strong> {m.description}<br><br>"
                    f"👉 <a href='/major/{m.code}' class='btn btn-sm btn-primary text-white text-decoration-none fw-bold mt-1'>"
                    f"<i class='bi bi-journal-bookmark-fill me-1'></i> Xem Chi Tiết Khung 29 Môn Học Ngành {m.name} &raquo;</a>"
                ),
                "type": "major_detail"
            }

        # -------------------------------------------------------------
        # 2. HỎI VỀ 4 PHƯƠNG THỨC XÉT TUYỂN (Admission Methods)
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["phuong thuc", "cach xet", "xet tuyen nhu the nao", "xet hoc ba", "ielts", "sat", "dgnl", "danh gia nang luc", "hsa", "tsa", "tuyen thang"]):
            return {
                "reply": (
                    f"📋 <strong>4 PHƯƠNG THỨC XÉT TUYỂN CHÍNH THỨC NĂM 2026 (KHÓA 68):</strong><br><br>"
                    f"1️⃣ <strong>Phương thức 1 (PT1) - Điểm thi Tốt nghiệp THPT 2026:</strong><br>"
                    f"Xét theo tổng điểm 3 môn trong tổ hợp xét tuyển (A00, A01, D01, D07, B00...) cộng điểm ưu tiên khu vực/đối tượng.<br><br>"
                    f"2️⃣ <strong>Phương thức 2 (PT2) - Đánh giá năng lực (ĐGNL & ĐGTD):</strong><br>"
                    f"Áp dụng kết quả thi HSA (ĐHQG Hà Nội), APT (ĐHQG TP.HCM) và TSA (ĐHBK Hà Nội). Điểm thi được quy đổi chuẩn hóa về thang điểm 30.<br><br>"
                    f"3️⃣ <strong>Phương thức 3 (PT3) - Kết hợp Chứng chỉ Tiếng Anh Quốc tế:</strong><br>"
                    f"Thí sinh có chứng chỉ <strong>IELTS >= 5.5</strong>, <strong>SAT >= 1200</strong> hoặc <strong>ACT >= 26</strong> kết hợp với điểm thi môn Toán + 01 môn tự chọn trong kỳ thi THPT.<br>"
                    f"<em>* Điểm quy đổi IELTS: 5.5 = 8.0 | 6.0 = 8.5 | 6.5 = 9.0 | 7.0 = 9.5 | >=7.5 = 10.0 điểm.</em><br><br>"
                    f"4️⃣ <strong>Phương thức 4 (PT4) - Xét tuyển thẳng & Ưu tiên xét tuyển:</strong><br>"
                    f"Theo quy chế của Bộ GD&ĐT (Học sinh đoạt giải Nhất, Nhì, Ba kỳ thi HSG Quốc gia, Quốc tế hoặc KHKT).<br><br>"
                    f"💡 <em>Thí sinh có thể nộp nhiều hồ sơ theo các phương thức khác nhau để tối đa hóa cơ hội trúng tuyển!</em>"
                ),
                "type": "admission_methods"
            }

        # -------------------------------------------------------------
        # 3. HỎI VỀ THỜI GIAN, LỊCH TRÌNH & HẠN NỘP HỒ SƠ
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["han nop", "khi nao", "thoi gian", "lich tuyen sinh", "lich trinh", "bao gio", "het han", "dot 1", "dot 2", "ngay bao nhieu"]):
            return {
                "reply": (
                    f"🗓️ <strong>KẾ HOẠCH & MỐC THỜI GIAN TUYỂN SINH ĐẠI HỌC 2026:</strong><br><br>"
                    f"• <strong>Đợt 1 (Xét tuyển sớm - PT2 & PT3):</strong><br>"
                    f"Tiếp nhận hồ sơ trực tuyến từ <strong>15/04/2026 đến 17h00 ngày 30/06/2026</strong>.<br><br>"
                    f"• <strong>Đợt 2 (Đăng ký nguyện vọng theo Cổng Bộ GD&ĐT):</strong><br>"
                    f"Thời gian đăng ký và điều chỉnh nguyện vọng từ <strong>10/07/2026 đến 17h00 ngày 30/07/2026</strong>.<br><br>"
                    f"• <strong>Chạy Lọc ảo & Công bố điểm chuẩn chính thức:</strong><br>"
                    f"Từ ngày <strong>15/08/2026 đến trước 17h00 ngày 20/08/2026</strong>.<br><br>"
                    f"• <strong>Xác nhận nhập học trực tuyến:</strong><br>"
                    f"Hạn chót trước <strong>17h00 ngày 28/08/2026</strong> trực tiếp tại Cổng Thí Sinh.<br><br>"
                    f"⚡ <em>Lời khuyên:</em> Hãy hoàn thiện và nộp hồ sơ sớm để được cán bộ khảo thí kiểm tra tính hợp lệ của giấy tờ minh chứng!"
                ),
                "type": "timeline_guide"
            }

        # -------------------------------------------------------------
        # 4. HỎI VỀ HỌC PHÍ & HỌC BỔNG
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["hoc phi", "tien hoc", "chi phi", "ton bao nhieu", "hoc bong"]):
            return {
                "reply": (
                    f"💰 <strong>CHÍNH SÁCH HỌC PHÍ & HỌC BỔNG NĂM HỌC 2026 - 2027:</strong><br><br>"
                    f"• <strong>Chương trình chuẩn (Chính quy):</strong><br>"
                    f"Dự kiến khoảng <strong>22.000.000đ - 28.000.000đ / năm học</strong> (tương đương khoảng 650.000đ - 780.000đ / tín chỉ tùy ngành).<br><br>"
                    f"• <strong>Chương trình Tiên tiến & Chất lượng cao (Dạy bằng Tiếng Anh):</strong><br>"
                    f"Khoảng <strong>45.000.000đ - 65.000.000đ / năm học</strong>.<br><br>"
                    f"• <strong>Chính sách Học bổng Khuyến khích Tài năng:</strong><br>"
                    f"Nhà trường dành hơn 30 tỷ đồng cấp học bổng cho tân sinh viên Khóa 68:<br>"
                    f"- Học bổng Thủ khoa / Á khoa: Tài trợ <strong>100% học phí toàn khóa</strong>.<br>"
                    f"- Học bổng Xuất sắc: Miễn giảm 50% - 100% học phí năm học đầu tiên.<br>"
                    f"- Học bổng doanh nghiệp đối tác đồng hành tài trợ hàng năm."
                ),
                "type": "tuition_guide"
            }

        # -------------------------------------------------------------
        # 5. HỎI VỀ LỆ PHÍ XÉT TUYỂN & THANH TOÁN VIETQR
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["le phi", "vietqr", "dong tien", "thanh toan", "chuyen khoan", "50k", "50.000", "bien lai"]):
            return {
                "reply": (
                    f"💳 <strong>HƯỚNG DẪN ĐÓNG LỆ PHÍ XÉT TUYỂN QUA VIETQR:</strong><br><br>"
                    f"• <strong>Mức lệ phí:</strong> <strong>50.000 VNĐ / hồ sơ xét tuyển</strong>.<br>"
                    f"• <strong>Phương thức:</strong> Quét mã chuẩn <strong>VietQR Ngân hàng MBBank</strong> tự động 100%.<br>"
                    f"• <strong>Quy trình thực hiện:</strong><br>"
                    f"1. Sau khi nộp hồ sơ, chọn tab <strong>'Đóng lệ phí QR'</strong> tại Cổng Thí Sinh.<br>"
                    f"2. Dùng App ngân hàng bất kỳ (MBBank, Vietcombank, Techcombank, BIDV...) quét mã QR hiển thị.<br>"
                    f"3. Hệ thống ngân hàng tự động khớp nội dung `PAY-TS2026-XXXX` và chuyển sang trạng thái <strong>ĐÃ NỘP ĐỦ</strong> trong 1-2 giây.<br>"
                    f"4. Thí sinh có thể bấm <strong>'In Biên Lai'</strong> để tải phiếu thu điện tử có mã xác thực."
                ),
                "type": "payment_guide"
            }

        # -------------------------------------------------------------
        # 6. HỎI VỀ XÁC NHẬN NHẬP HỌC & SAU TRÚNG TUYỂN
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["nhap hoc", "trung tuyen roi", "lam gi tiep", "mssv", "giay bao", "email truong", "xac nhan nhap hoc"]):
            return {
                "reply": (
                    f"🎉 <strong>QUY TRÌNH XÁC NHẬN NHẬP HỌC TRỰC TUYẾN DÀNH CHO THÍ SINH TRÚNG TUYỂN:</strong><br><br>"
                    f"Khi hồ sơ đạt trạng thái <strong>TRÚNG TUYỂN</strong>, bạn thực hiện 4 bước sau:<br>"
                    f"1️⃣ <strong>Bước 1:</strong> Đăng nhập vào Cổng Thí Sinh.<br>"
                    f"2️⃣ <strong>Bước 2:</strong> Tại hồ sơ trúng tuyển, nhấn nút màu xanh <strong>'Xác Nhận Nhập Học'</strong>.<br>"
                    f"3️⃣ <strong>Bước 3:</strong> Hệ thống tự động cấp ngay <strong>Mã số sinh viên (MSSV)</strong> và hòm thư điện tử sinh viên chính thức dạng <code>MSSV@st.neu.edu.vn</code>.<br>"
                    f"4️⃣ <strong>Bước 4:</strong> Nhấn nút <strong>'Giấy Báo Nhập Học'</strong> để tải về Giấy báo trúng tuyển điện tử có chữ ký số và mã QR xác thực của Hội đồng Tuyển sinh."
                ),
                "type": "enrollment_guide"
            }

        # -------------------------------------------------------------
        # 7. HỎI VỀ PHÚC KHẢO ĐIỂM & RÚT HỒ SƠ
        # -------------------------------------------------------------
        if any(k in norm_q for k in ["phuc khao", "khieu nai", "rut ho so", "cham lai", "sai diem"]):
            return {
                "reply": (
                    f"⚖️ <strong>QUY TRÌNH PHÚC KHẢO & RÚT HỒ SƠ XÉT TUYỂN:</strong><br><br>"
                    f"• <strong>Phúc khảo điểm số:</strong><br>"
                    f"- Áp dụng trong vòng <strong>07 ngày</strong> kể từ khi công bố kết quả xét tuyển.<br>"
                    f"- Thí sinh nhấn nút <strong>'Nộp Phúc Khảo'</strong> tại danh sách hồ sơ cá nhân, điền lý do và minh chứng điểm điều chỉnh.<br>"
                    f"- Hội đồng Tuyển sinh sẽ thẩm định và trả lời kết quả trong vòng 03 ngày làm việc.<br><br>"
                    f"• <strong>Rút hồ sơ hoặc Đổi nguyện vọng:</strong><br>"
                    f"- Khi hồ sơ còn ở trạng thái <strong>'Chờ xét duyệt'</strong>, thí sinh có toàn quyền bấm nút <strong>'Sửa NV'</strong> để đổi ngành hoặc <strong>'Rút HS'</strong> bất cứ lúc nào."
                ),
                "type": "appeal_guide"
            }

        # -------------------------------------------------------------
        # 8. TƯ VẤN THEO ĐIỂM SỐ & XÁC SUẤT TRÚNG TUYỂN (Probability Scoring)
        # -------------------------------------------------------------
        if extracted_score is not None:
            score = extracted_score
            analysis = cls.evaluate_admission_probability(score, db)

            reply_parts = [
                f"🎯 <strong>PHÂN TÍCH XÁC SUẤT TRÚNG TUYỂN DỰA TRÊN ĐIỂM THI: {score} ĐIỂM</strong>",
                f"Dựa trên dữ liệu điểm chuẩn tham khảo 40 ngành đào tạo, Trợ lý AI phân chia cơ hội trúng tuyển của bạn thành 3 nhóm chiến lược:<br>"
            ]

            if analysis["target"]:
                reply_parts.append("🟢 <strong>Nhóm Vừa Sức (Cơ hội trúng tuyển 75% - 85%):</strong>")
                for m in analysis["target"]:
                    reply_parts.append(f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: <span class='badge bg-primary'>{m.benchmark_score}</span> (Chỉ tiêu: {m.quota})")
                reply_parts.append("")

            if analysis["safe"]:
                reply_parts.append("🛡️ <strong>Nhóm An Toàn (Cơ hội trúng tuyển > 90% - Rất an tâm):</strong>")
                for m in analysis["safe"][:3]:
                    reply_parts.append(f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: <span class='badge bg-success'>{m.benchmark_score}</span>")
                reply_parts.append("")

            if analysis["reach"]:
                reply_parts.append("⚡ <strong>Nhóm Thử Thách (Cần bứt phá hoặc làm NV1 mơ ước):</strong>")
                for m in analysis["reach"][:2]:
                    reply_parts.append(f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: <span class='badge bg-danger'>{m.benchmark_score}</span>")
                reply_parts.append("")

            nv1_rec = analysis["target"][0] if analysis["target"] else (analysis["reach"][0] if analysis["reach"] else None)
            nv2_rec = analysis["safe"][0] if analysis["safe"] else (analysis["target"][-1] if len(analysis["target"]) > 1 else None)

            if nv1_rec and nv2_rec:
                reply_parts.append(
                    f"💡 <strong>Chiến lược Đăng ký 2 Nguyện vọng tối ưu cho bạn:</strong><br>"
                    f"1️⃣ <strong>Nguyện vọng 1 (NV1):</strong> Đăng ký <em>{nv1_rec.name} ({nv1_rec.code})</em> để chinh phục ngành yêu thích nhất.<br>"
                    f"2️⃣ <strong>Nguyện vọng 2 (NV2):</strong> Đăng ký <em>{nv2_rec.name} ({nv2_rec.code})</em> làm phương án an toàn chắc chắn đỗ nhờ cơ chế lọc ảo tự động của trường!"
                )

            return {
                "reply": "<br>".join(reply_parts),
                "type": "probability_analysis",
                "extracted_score": score
            }

        # -------------------------------------------------------------
        # 9. TƯ VẤN THEO TỔ HỢP XÉT TUYỂN (A00, A01, D01, D07, B00...)
        # -------------------------------------------------------------
        if extracted_combo:
            combo = extracted_combo
            combo_majors = []
            if combo in ["A00", "A01"]:
                combo_majors = db.query(Major).filter(Major.category == "Công nghệ & Kỹ thuật").limit(5).all()
                desc = "Tổ hợp xét tuyển thế mạnh cho các ngành Công nghệ thông tin, Kỹ thuật phần mềm, Trí tuệ nhân tạo, Tự động hóa, Vi mạch bán dẫn..."
            elif combo in ["D01", "D07"]:
                combo_majors = db.query(Major).filter(Major.category.in_(["Kinh tế & Quản lý", "Ngoại ngữ & Xã hội"])).limit(5).all()
                desc = "Tổ hợp rất phổ biến tại các ngành Quản trị kinh doanh, Marketing, Kinh doanh quốc tế, Tài chính - Ngân hàng, Ngôn ngữ Anh..."
            elif combo == "B00":
                combo_majors = db.query(Major).filter(Major.category == "Y Dược - Sinh học - Kiến trúc").limit(5).all()
                desc = "Tổ hợp Toán - Hóa - Sinh áp dụng cho các ngành Y khoa, Dược học, Điều dưỡng và Công nghệ sinh học..."
            else:
                combo_majors = db.query(Major).limit(5).all()
                desc = f"Tổ hợp {combo} được áp dụng xét tuyển rộng rãi vào nhiều ngành đào tạo của trường."

            txt = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: <span class='badge bg-primary'>{m.benchmark_score}</span> (Chỉ tiêu: {m.quota})" for m in combo_majors])
            return {
                "reply": f"📚 <strong>TƯ VẤN CÁC NGÀNH XÉT TUYỂN THEO TỔ HỢP {combo}:</strong><br>{desc}<br><br>{txt}<br><br>👉 Bạn có thể chia sẻ mức điểm dự kiến của mình để Trợ lý AI tính xác suất trúng tuyển chi tiết nhé!",
                "type": "combo_recommendation"
            }

        # -------------------------------------------------------------
        # 10. TRẢ LỜI TỔNG QUAN / MENU HỖ TRỢ TRỌNG TÂM
        # -------------------------------------------------------------
        return {
            "reply": (
                f"Xin chào bạn! 👋 Tôi là <strong>Trợ Lý AI Tư Vấn Tuyển Sinh 2026</strong>.<br><br>"
                f"Tôi có thể hỗ trợ giải đáp nhanh và chính xác các thông tin tuyển sinh sau:<br>"
                f"• 🔍 <strong>Tra cứu ngành học & điểm chuẩn:</strong> Nhập tên ngành (VD: <em>'Điểm chuẩn ngành Luật'</em>, <em>'Chỉ tiêu ngành CNTT'</em>, <em>'Ngành Marketing'</em>...)<br>"
                f"• 🎯 <strong>Tính xác suất đỗ:</strong> Nhập điểm thi của bạn (VD: <em>'Em thi được 25.5 điểm đỗ ngành nào?'</em>)<br>"
                f"• 📋 <strong>4 Phương thức xét tuyển:</strong> Hỏi về <em>'Các phương thức xét tuyển'</em>, <em>'Xét chứng chỉ IELTS/SAT'</em>, <em>'Điểm thi ĐGNL'</em>...<br>"
                f"• 🗓️ <strong>Hạn nộp hồ sơ & Lịch trình:</strong> Hỏi về <em>'Hạn nộp hồ sơ đợt 1'</em>, <em>'Lịch công bố điểm chuẩn'</em>...<br>"
                f"• 💰 <strong>Học phí & Lệ phí:</strong> Hỏi về <em>'Học phí một năm bao nhiêu'</em>, <em>'Cách đóng lệ phí VietQR'</em>...<br><br>"
                f"Bạn đang quan tâm đến ngành học hay cần hỗ trợ thông tin nào, hãy nhắn cho tôi nhé!"
            ),
            "type": "greeting"
        }


def process_ai_admission_chat(query: str, user_score: Optional[float], combination: Optional[str], history: Optional[List[dict]], db: Session) -> Dict:
    """Xử lý hội thoại AI: Ưu tiên Gemini LLM (nếu có key), fallback Engine AI tự chủ"""
    system_prompt = (
        "Bạn là Trợ lý AI Tư vấn Tuyển sinh Đại học chính quy 2026 của trường Đại học Kinh tế Quốc dân (NEU). "
        "Trường có 40 ngành đào tạo chính quy thuộc 4 khối: Công nghệ & Kỹ thuật, Kinh tế & Quản lý, Ngoại ngữ & Xã hội, Y Dược - Sinh học - Kiến trúc. "
        "Lệ phí xét tuyển là 50.000 VNĐ nộp qua VietQR MBBank. Có 4 phương thức xét tuyển: PT1 (Điểm thi THPT), PT2 (ĐGNL HSA/TSA), PT3 (IELTS/SAT kết hợp), PT4 (Tuyển thẳng). "
        "Thí sinh được đăng ký 2 nguyện vọng NV1 và NV2 với thuật toán lọc ảo tự động. "
        "Hãy trả lời thí sinh một cách nhiệt tình, chính xác, định dạng HTML thân thiện (sử dụng <strong>, <br>, <ul>, <li>, <em>, <span class='badge'>)."
    )

    if GEMINI_API_KEY:
        gemini_reply = call_gemini_api(prompt=query, system_instruction=system_prompt, history=history)
        if gemini_reply:
            return {
                "reply": gemini_reply.replace("\n", "<br>"),
                "type": "gemini_llm",
                "engine": "Google Gemini 1.5 Flash"
            }

    res = StandaloneAIAdvisor.consult(query, user_score, combination, db)
    res["engine"] = "Autonomous Expert Reasoning Engine 3.0"
    return res
