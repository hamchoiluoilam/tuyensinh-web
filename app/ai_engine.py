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
                "temperature": 0.4,
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


class StandaloneAIAdvisor:
    """
    Công cụ AI Suy luận Chuyên gia Tuyển sinh (Autonomous Expert Reasoning Engine)
    - Trích xuất thực thể: Điểm số, tổ hợp xét tuyển (A00, A01, D01, B00...), lĩnh vực sở thích.
    - Thuật toán phân tầng xác suất trúng tuyển (Safe / Target / Reach).
    - Khuyến nghị chiến lược Đa nguyện vọng (NV1 bứt phá - NV2 an toàn).
    - Khám phá chương trình đào tạo chuyên sâu từ CSDL 383 môn học.
    """

    @staticmethod
    def extract_entities(query: str, explicit_score: Optional[float] = None, explicit_combo: Optional[str] = None):
        q = query.lower()
        score = explicit_score
        if score is None:
            # Nhận dạng điểm số dạng "25 điểm", "25.5 điểm", "được 26.75", "tầm 24 đ"
            match = re.search(r'(\d{1,2}(?:[\.,]\d{1,2})?)\s*(?:điểm|đ\b|\bpt\b)', q)
            if not match:
                match = re.search(r'(?:được|tầm|khoảng|mức|thi)\s*(\d{1,2}(?:[\.,]\d{1,2})?)', q)
            if match:
                try:
                    score = float(match.group(1).replace(',', '.'))
                except:
                    pass

        # Nhận dạng tổ hợp môn
        combo = explicit_combo
        if not combo:
            combos = re.findall(r'\b([a-d]\d{2})\b', q, re.IGNORECASE)
            if combos:
                combo = combos[0].upper()

        return score, combo

    @classmethod
    def evaluate_admission_probability(cls, user_score: float, db: Session) -> Dict:
        """Phân tích xác suất trúng tuyển theo 3 tầng chuẩn khoa học"""
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

        # Sắp xếp theo điểm chuẩn
        safe_majors.sort(key=lambda x: x.benchmark_score, reverse=True)
        target_majors.sort(key=lambda x: x.benchmark_score, reverse=True)
        reach_majors.sort(key=lambda x: x.benchmark_score, reverse=True)

        return {
            "safe": safe_majors[:4],
            "target": target_majors[:4],
            "reach": reach_majors[:3]
        }

    @classmethod
    def consult(cls, query: str, user_score: Optional[float], combination: Optional[str], db: Session) -> Dict:
        extracted_score, extracted_combo = cls.extract_entities(query, user_score, combination)
        q = query.lower()

        # 1. Trường hợp có Điểm số (Tư vấn theo điểm thi & xác suất)
        if extracted_score is not None:
            score = extracted_score
            analysis = cls.evaluate_admission_probability(score, db)

            reply_parts = [
                f"🎯 <strong>PHÂN TÍCH XÁC SUẤT TRÚNG TUYỂN DỰA TRÊN ĐIỂM SỐ: {score} ĐIỂM</strong>",
                f"Dựa trên dữ liệu điểm chuẩn tham khảo 40 ngành đào tạo, Trợ lý AI phân tích cơ hội của bạn thành 3 nhóm chiến lược:<br>"
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

            # Khuyến nghị chiến lược Đa nguyện vọng
            nv1_rec = analysis["target"][0] if analysis["target"] else (analysis["reach"][0] if analysis["reach"] else None)
            nv2_rec = analysis["safe"][0] if analysis["safe"] else (analysis["target"][-1] if len(analysis["target"]) > 1 else None)

            if nv1_rec and nv2_rec:
                reply_parts.append(
                    f"💡 <strong>Chiến lược Đăng ký Đa Nguyện vọng tối ưu cho bạn:</strong><br>"
                    f"1️⃣ <strong>Nguyện vọng 1 (NV1):</strong> Đăng ký <em>{nv1_rec.name} ({nv1_rec.code})</em> để nắm bắt cơ hội vào ngành yêu thích nhất.<br>"
                    f"2️⃣ <strong>Nguyện vọng 2 (NV2):</strong> Đăng ký <em>{nv2_rec.name} ({nv2_rec.code})</em> làm 'phao cứu sinh' an toàn tuyệt đối nhờ cơ chế lọc ảo tự động của trường!"
                )

            return {
                "reply": "<br>".join(reply_parts),
                "type": "probability_analysis",
                "extracted_score": score
            }

        # 2. Trường hợp hỏi theo Khối ngành / Tổ hợp môn
        if extracted_combo:
            combo = extracted_combo
            combo_majors = []
            if combo in ["A00", "A01"]:
                combo_majors = db.query(Major).filter(Major.category == "Công nghệ & Kỹ thuật").limit(5).all()
                desc = "Tổ hợp xét tuyển phù hợp với các ngành Công nghệ thông tin, Kỹ thuật phần mềm, Trí tuệ nhân tạo, Tự động hóa..."
            elif combo == "D01":
                combo_majors = db.query(Major).filter(Major.category.in_(["Kinh tế & Quản lý", "Ngoại ngữ & Xã hội"])).limit(5).all()
                desc = "Tổ hợp Toán - Văn - Anh rất mạnh thế tại các ngành Kinh doanh quốc tế, Marketing, Thương mại điện tử, Ngôn ngữ Anh..."
            elif combo == "B00":
                combo_majors = db.query(Major).filter(Major.category == "Y Dược, Sinh học & Kiến trúc").limit(5).all()
                desc = "Tổ hợp Toán - Hóa - Sinh xét tuyển thẳng vào Y khoa, Dược học, Điều dưỡng và Công nghệ sinh học..."
            else:
                combo_majors = db.query(Major).limit(5).all()
                desc = f"Tổ hợp {combo} được áp dụng xét tuyển rộng rãi vào nhiều ngành đào tạo của trường."

            txt = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn tham khảo: <span class='badge bg-primary'>{m.benchmark_score}</span>" for m in combo_majors])
            return {
                "reply": f"📚 <strong>TƯ VẤN XÉT TUYỂN THEO KHỐI THI / TỔ HỢP: {combo}</strong><br>{desc}<br><br>{txt}<br><br>👉 Bạn có thể chia sẻ mức điểm dự kiến của mình để AI tính toán cụ thể ngành nào có cơ hội trúng tuyển cao nhất nhé!",
                "type": "combo_recommendation"
            }

        # 3. Hỏi sâu về chuyên ngành CNTT / AI / Vi mạch
        if any(k in q for k in ["công nghệ", "cntt", "it", "phần mềm", "lập trình", "ai", "vi mạch", "khoa học máy tính"]):
            top_tech = db.query(Major).filter(Major.category == "Công nghệ & Kỹ thuật").limit(4).all()
            # Lấy mẫu các môn học thực tế
            tech_subjects = db.query(Subject).filter(Subject.major_id == top_tech[0].id).limit(4).all() if top_tech else []
            subj_txt = ", ".join([s.name for s in tech_subjects]) if tech_subjects else "Lập trình Python, CSDL SQL, Trí tuệ nhân tạo, Cấu trúc dữ liệu"

            list_majors = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: {m.benchmark_score} | Chỉ tiêu: {m.quota}" for m in top_tech])
            return {
                "reply": (
                    f"💻 <strong>KHỐI NGÀNH CÔNG NGHỆ, TRÍ TUỆ NHÂN TẠO & KỸ THUẬT:</strong><br><br>"
                    f"{list_majors}<br><br>"
                    f"📖 <strong>Chương trình đào tạo chuẩn quốc tế:</strong> Sinh viên được học các môn cốt lõi như: <em>{subj_txt}</em>. "
                    f"Trường có phòng Lab thực hành kết nối doanh nghiệp công nghệ lớn.<br><br>"
                    f"💡 <em>Gợi ý:</em> Bạn hãy nhập mức điểm xét tuyển để AI gợi ý xem ngành nào trong khối này hợp với bạn nhất!"
                ),
                "type": "tech_field"
            }

        # 4. Hỏi về khối ngành Kinh tế / Quản lý / Marketing
        if any(k in q for k in ["kinh tế", "quản trị", "marketing", "tài chính", "ngân hàng", "logistics", "kế toán"]):
            biz_majors = db.query(Major).filter(Major.category == "Kinh tế & Quản lý").limit(4).all()
            list_majors = "<br>".join([f"• <strong>{m.name} ({m.code})</strong> - Điểm chuẩn: {m.benchmark_score}" for m in biz_majors])
            return {
                "reply": (
                    f"📈 <strong>KHỐI NGÀNH KINH TẾ, TÀI CHÍNH & QUẢN LÝ HIỆN ĐẠI:</strong><br><br>"
                    f"{list_majors}<br><br>"
                    f"Chương trình kết hợp lý thuyết quản trị và thực chiến chuyển đổi số (Digital Business, FinTech). "
                    f"Bạn có thể bấm vào từng ngành trên trang chủ để xem 8 kỳ học và danh sách môn học chi tiết!"
                ),
                "type": "biz_field"
            }

        # 5. Hỏi về Học phí, Lệ phí xét tuyển, VietQR
        if any(k in q for k in ["lệ phí", "học phí", "bao nhiêu tiền", "đóng tiền", "vietqr", "thanh toán"]):
            return {
                "reply": (
                    f"💳 <strong>HƯỚNG DẪN LỆ PHÍ VÀ THANH TOÁN VIETQR:</strong><br><br>"
                    f"• <strong>Mức lệ phí xét tuyển:</strong> <strong>50.000 VNĐ / hồ sơ</strong>.<br>"
                    f"• <strong>Phương thức thanh toán:</strong> Tự động 100% qua chuẩn <strong>VietQR ngân hàng</strong>.<br>"
                    f"• <strong>Quy trình:</strong> Sau khi nộp hồ sơ, hệ thống tạo mã giao dịch `PAY-TS2026-XXXX`. "
                    f"Bạn dùng app ngân hàng quét mã QR, tiền sẽ được đối soát tự động tức thì sang trạng thái <strong>PAID</strong>.<br>"
                    f"• <strong>Biên lai điện tử:</strong> Sau khi nộp, thí sinh có thể in Phiếu thu lệ phí điện tử chuẩn A4/A5 ngay tại Cổng Thí Sinh."
                ),
                "type": "fee_guide"
            }

        # 6. Hỏi về Hồ sơ xét tuyển, Học bạ, Quy chế
        if any(k in q for k in ["hồ sơ", "học bạ", "minh chứng", "giấy tờ", "cần những gì", "quy chế"]):
            return {
                "reply": (
                    f"📋 <strong>HƯỚNG DẪN HỒ SƠ XÉT TUYỂN ĐẠI HỌC 2026:</strong><br><br>"
                    f"1. <strong>Phương thức xét tuyển:</strong> Xét học bạ THPT (các học kỳ theo tổ hợp) HOẶC Điểm thi tốt nghiệp THPT.<br>"
                    f"2. <strong>Minh chứng cần chuẩn bị:</strong> Chụp ảnh rõ nét Học bạ THPT hoặc Giấy chứng nhận điểm thi.<br>"
                    f"3. <strong>Tải file trực tuyến:</strong> Tại form nộp hồ sơ, chọn tính năng <em>'Tải file từ máy tính/điện thoại'</em> (hỗ trợ .jpg, .png, .pdf).<br>"
                    f"4. <strong>Đa nguyện vọng:</strong> Bạn được đăng ký cả <strong>Nguyện vọng 1</strong> và <strong>Nguyện vọng 2</strong> để tối ưu cơ hội trúng tuyển."
                ),
                "type": "doc_guide"
            }

        # Trả lời tổng quan có hướng dẫn tương tác
        return {
            "reply": (
                f"Xin chào bạn! 👋 Tôi là <strong>Trợ Lý AI Tư Vấn Tuyển Sinh 2026</strong>.<br><br>"
                f"Tôi có thể đồng hành cùng bạn giải quyết các băn khoăn tuyển sinh:<br>"
                f"• 🎯 <strong>Tính xác suất đỗ:</strong> Bạn hãy nhập điểm (ví dụ: <em>'Em thi được 25.5 điểm thì đỗ ngành nào?'</em>)<br>"
                f"• 🧭 <strong>Tư vấn theo tổ hợp:</strong> (ví dụ: <em>'Khối A01 xét những ngành nào?'</em>)<br>"
                f"• 📚 <strong>Chương trình học:</strong> (ví dụ: <em>'Ngành CNTT học những môn gì?'</em>)<br>"
                f"• 💳 <strong>Lệ phí & Hồ sơ:</strong> (ví dụ: <em>'Hướng dẫn nộp lệ phí VietQR'</em>)<br><br>"
                f"Bạn đang quan tâm đến ngành học hoặc mức điểm nào, hãy nhắn cho tôi nhé!"
            ),
            "type": "greeting"
        }


def process_ai_admission_chat(query: str, user_score: Optional[float], combination: Optional[str], history: Optional[List[dict]], db: Session) -> Dict:
    """Xử lý hội thoại AI: Ưu tiên Gemini LLM (nếu có key), fallback Engine AI tự chủ"""
    system_prompt = (
        "Bạn là Trợ lý AI Tư vấn Tuyển sinh Đại học 2026 của trường Đại học (UniAdmission 2026). "
        "Trường có 40 ngành đào tạo chính quy thuộc 4 khối: Công nghệ & Kỹ thuật, Kinh tế & Quản lý, Ngoại ngữ & Xã hội, Y Dược. "
        "Lệ phí xét tuyển là 50.000 VNĐ nộp qua VietQR. Thí sinh được đăng ký 2 nguyện vọng (NV1 và NV2) với cơ chế lọc ảo tự động. "
        "Hãy trả lời thí sinh một cách nhiệt tình, chính xác, định dạng HTML thân thiện (sử dụng <strong>, <br>, <ul>, <li>, <em>)."
    )

    # 1. Thử gọi LLM nếu có API key
    if GEMINI_API_KEY:
        gemini_reply = call_gemini_api(prompt=query, system_instruction=system_prompt, history=history)
        if gemini_reply:
            return {
                "reply": gemini_reply.replace("\n", "<br>"),
                "type": "gemini_llm",
                "engine": "Google Gemini 1.5 Flash"
            }

    # 2. Sử dụng Standalone AI Advisor Engine
    res = StandaloneAIAdvisor.consult(query, user_score, combination, db)
    res["engine"] = "Autonomous Expert Reasoning Engine 2.0"
    return res
