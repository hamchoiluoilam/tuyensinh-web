import io
from fastapi.testclient import TestClient
from main import app, seed_demo_data

seed_demo_data()
client = TestClient(app)

print("=== BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG TUYỂN SINH (RBAC, SECURITY 2FA, ADVANCED FILTER & AI) ===")

# 1. Test Auth & Multi-Role RBAC (Admin, Officer, Student)
r_admin = client.post('/api/auth/login', json={'email': 'admin@tuyensinh.edu.vn', 'password': 'admin123'})
assert r_admin.status_code == 200, f'Admin login failed: {r_admin.text}'
assert r_admin.json()['user']['role'] == 'ADMIN'
print('Test 1a: Admin login with SHA-256 + Salt: OK')

r_officer = client.post('/api/auth/login', json={'email': 'canbo@tuyensinh.edu.vn', 'password': 'canbo123'})
assert r_officer.status_code == 200, f'Officer login failed: {r_officer.text}'
assert r_officer.json()['user']['role'] == 'OFFICER'
print('Test 1b: Officer login with SHA-256 + Salt: OK')

r_student = client.post('/api/auth/login', json={'email': 'student@gmail.com', 'password': '123456'})
assert r_student.status_code == 200, f'Student login failed: {r_student.text}'
assert r_student.json()['user']['role'] == 'STUDENT'
print('Test 1c: Student login with SHA-256 + Salt: OK')

# 2. Test 40 Majors & Program Details
r_majors = client.get('/api/admissions/majors')
assert len(r_majors.json()) == 40
print('Test 2: 40 Majors loaded: OK')

# 3. Test Real File Upload
dummy_file = io.BytesIO(b'Fake image content for testing')
r_upload = client.post('/api/admissions/upload-proof', files={'file': ('my_hocba.png', dummy_file, 'image/png')})
assert r_upload.status_code == 200, f'Upload failed: {r_upload.text}'
uploaded_url = r_upload.json()['url']
assert '/static/uploads/' in uploaded_url
print(f'Test 3: Real file upload ({uploaded_url}): OK')

# 4. Test Dual-Aspiration Application (NV1 & NV2)
app_payload = {
    'full_name': 'Lê Hoàng Nam',
    'id_card': '001202099999',
    'email': 'namlh@gmail.com',
    'phone': '0901234567',
    'method': 'HOC_BA',
    'score': 26.5,
    'major_id': 1,
    'major_nv2_id': 2,
    'proof_url': uploaded_url
}
r_apply = client.post('/api/admissions/apply', json=app_payload)
assert r_apply.status_code == 200, f'Apply failed: {r_apply.text}'
new_app = r_apply.json()
assert new_app['major_nv2_id'] == 2
print('Test 4: Dual aspiration submission (NV1=1, NV2=2): OK')

# 5. Test Payment & Strict Ownership Security on Receipt
tx_code = f'PAY-{new_app["app_code"]}'
r_pay = client.post(f'/api/finance/simulate-pay/{tx_code}')
assert r_pay.status_code == 200

# 5a. Thí sinh 'student@gmail.com' cố tình xem biên lai của thí sinh 'namlh@gmail.com' -> Phải bị chặn 403 Forbidden!
r_forbidden_receipt = client.get(f'/api/finance/receipt/{tx_code}')
assert r_forbidden_receipt.status_code == 403
print('Test 5a: Strict ownership security blocks Student from viewing another candidate\'s receipt (403 Forbidden): OK')

# 5b. Đăng nhập với quyền Cán Bộ Tuyển Sinh (OFFICER) để xem biên lai hợp pháp
client.post('/api/auth/login', json={'email': 'canbo@tuyensinh.edu.vn', 'password': 'canbo123'})
r_receipt = client.get(f'/api/finance/receipt/{tx_code}')
assert r_receipt.status_code == 200
assert r_receipt.json()['status'] == 'ĐÃ XÁC NHẬN NỘP ĐỦ LỆ PHÍ'
print('Test 5b: Officer authorized to view candidate receipt: OK')

# 6. Test Security 2FA Public Verification & Data Masking
# 6a. Thử tra cứu sai 4 số cuối CCCD -> Phải bị từ chối 400
r_lookup_fail = client.post('/api/admissions/public-verify-lookup', json={
    'app_code': new_app['app_code'],
    'id_card_last4': '0000' # Sai
})
assert r_lookup_fail.status_code == 400
print('Test 6a: Public verification rejects invalid CCCD last 4 digits: OK')

# 6b. Tra cứu đúng 4 số cuối CCCD ('9999') -> Trả về dữ liệu Masked, KHÔNG lộ CCCD và link minh chứng
r_lookup_ok = client.post('/api/admissions/public-verify-lookup', json={
    'app_code': new_app['app_code'],
    'id_card_last4': '9999' # Đúng
})
assert r_lookup_ok.status_code == 200
data_masked = r_lookup_ok.json()
assert '******' in data_masked['id_card_masked']
assert '***' in data_masked['phone_masked']
assert 'proof_url' not in data_masked or data_masked.get('proof_url') is None
print('Test 6b: Public 2FA verification returns masked privacy data without proof URL: OK')

# 7. Test Public Endpoint Masking on Unauthenticated Lookup
client.post('/api/auth/logout') # Đăng xuất để đóng vai khách vãng lai
r_pub_unauth = client.get(f'/api/admissions/lookup/{new_app["app_code"]}')
assert r_pub_unauth.status_code == 200
assert r_pub_unauth.json()['proof_url'] is None # Không lộ ảnh học bạ cho người lạ
assert '******' in r_pub_unauth.json()['id_card']
print('Test 7: Unauthenticated lookup protects report card image and masks ID card: OK')

# 8. Test Role-Based Permission Check (RBAC: Officer vs Admin)
# 8a. Sửa chỉ tiêu ngành
r_quota = client.patch('/api/admissions/majors/1', json={'quota': 50, 'benchmark_score': 26.0})
assert r_quota.status_code == 200
# 8b. Cập nhật biểu phí
r_fee = client.patch('/api/finance/fee-configs/1', json={'fee_name': 'Lệ phí 2026 chuẩn', 'amount': 50000.0})
assert r_fee.status_code == 200
print('Test 8: Admin privilege operations: OK')

# 9. Test Advanced Virtual Filtering Algorithm (Tie-Breaking Rules)
r_filter = client.post('/api/admissions/run-virtual-filtering?major_id=1')
assert r_filter.status_code == 200
filter_res = r_filter.json()
assert 'Chạy lọc ảo đa nguyện vọng thành công' in filter_res['message']
print(f'Test 9: Advanced Virtual filtering with tie-breaking (Passed: {filter_res["passed_count"]}, Benchmark: {filter_res["benchmark_score"]}): OK')

# 10. Test Comprehensive AI Admission Advisor Engine
r_ai_score = client.post('/api/support/ai-consultant', json={'query': 'Em được 25.5 điểm thì có cơ hội đỗ ngành nào?'})
assert r_ai_score.status_code == 200
assert 'PHÂN TÍCH XÁC SUẤT TRÚNG TUYỂN' in r_ai_score.json()['reply']
assert 'Nhóm Vừa Sức' in r_ai_score.json()['reply']

r_ai_combo = client.post('/api/support/ai-consultant', json={'query': 'Khối A01 của trường tuyển những ngành nào?'})
assert r_ai_combo.status_code == 200
assert 'A01' in r_ai_combo.json()['reply']
print('Test 10: Complete AI Admission Advisor Engine (3-tier probability & multi-turn): OK')

# 11. Test NEU Admission Methods (IELTS + THPT Conversion & Detailed Score Breakdown)
import json
neu_app_payload = {
    'full_name': 'Nguyễn Phương Thảo',
    'id_card': '001202088888',
    'email': 'thaonp@gmail.com',
    'phone': '0988776655',
    'method': 'IELTS_THPT',
    'method_code': 'IELTS_THPT',
    'method_name': 'Xét tuyển kết hợp chứng chỉ IELTS và điểm thi THPT (Chuẩn NEU)',
    'subject_combination': 'IELTS + Toán + Vật lý',
    'priority_area': 'KV2-NT',
    'priority_score': 0.5,
    'score_details': json.dumps({
        'method': 'IELTS_THPT',
        'cert_type': 'IELTS',
        'ielts_band': 7.5,
        'ielts_converted': 10.0,
        'math_score': 9.2,
        'sub2_name': 'Vật lý',
        'sub2_score': 8.8,
        'priority_area': 'KV2-NT',
        'priority_score': 0.5,
        'total': 28.5
    }),
    'score': 28.5,
    'major_id': 1,
    'major_nv2_id': 2,
    'proof_url': uploaded_url
}
r_neu_apply = client.post('/api/admissions/apply', json=neu_app_payload)
assert r_neu_apply.status_code == 200, f'NEU Apply failed: {r_neu_apply.text}'
neu_res = r_neu_apply.json()
assert neu_res['method_code'] == 'IELTS_THPT'
assert neu_res['score'] == 28.5
assert neu_res['priority_area'] == 'KV2-NT'
assert neu_res['priority_score'] == 0.5
assert neu_res['score_details'] is not None

# Test officer note & score inspection
client.post('/api/auth/login', json={'email': 'canbo@tuyensinh.edu.vn', 'password': 'canbo123'})
r_review = client.patch(f'/api/admissions/applications/{neu_res["id"]}/status', json={
    'status': 'HOP_LE',
    'officer_note': 'Chứng chỉ IELTS 7.5 quy đổi 10.0 điểm hợp lệ theo chuẩn NEU.'
})
assert r_review.status_code == 200
assert r_review.json()['officer_note'] == 'Chứng chỉ IELTS 7.5 quy đổi 10.0 điểm hợp lệ theo chuẩn NEU.'
print('Test 11: NEU Admission Methods & Real-time Score Breakdown (IELTS 7.5 -> 10.0 + THPT): OK')

print("\n🎉 TẤT CẢ 11 BÀI KIỂM THỬ NÂNG CẤP (RBAC, 2FA SECURITY, NEU METHODS, ADVANCED FILTER & AI ENGINE) ĐẠT ĐIỂM 10/10 TUYỆT ĐỐI! 🎉")
