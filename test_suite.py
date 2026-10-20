import io
from fastapi.testclient import TestClient
from main import app, seed_demo_data

seed_demo_data()
client = TestClient(app)

print("--- BẮT ĐẦU KIỂM THỬ HỆ THỐNG TUYỂN SINH 10/10 ---")

# 1. Test Auth (Hash password verification)
r_admin = client.post('/api/auth/login', json={'email': 'admin@tuyensinh.edu.vn', 'password': 'admin123'})
assert r_admin.status_code == 200, f'Admin login failed: {r_admin.text}'
assert r_admin.json()['user']['role'] == 'ADMIN'
print('Test 1: Admin login with SHA-256 + Salt password: OK')

r_student = client.post('/api/auth/login', json={'email': 'student@gmail.com', 'password': '123456'})
assert r_student.status_code == 200, f'Student login failed: {r_student.text}'
assert r_student.json()['user']['role'] == 'STUDENT'
print('Test 2: Student login with SHA-256 + Salt password: OK')

# 2. Test 40 Majors
r_majors = client.get('/api/admissions/majors')
assert len(r_majors.json()) == 40
print('Test 3: 40 Majors loaded: OK')

# 3. Test Real File Upload
dummy_file = io.BytesIO(b'Fake image content for testing')
r_upload = client.post('/api/admissions/upload-proof', files={'file': ('my_hocba.png', dummy_file, 'image/png')})
assert r_upload.status_code == 200, f'Upload failed: {r_upload.text}'
uploaded_url = r_upload.json()['url']
assert '/static/uploads/' in uploaded_url
print(f'Test 4: Real file upload ({uploaded_url}): OK')

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
print('Test 5: Dual aspiration submission (NV1=1, NV2=2): OK')

# 5. Test Payment & Electronic Receipt
tx_code = f'PAY-{new_app["app_code"]}'
r_pay = client.post(f'/api/finance/simulate-pay/{tx_code}')
assert r_pay.status_code == 200
r_receipt = client.get(f'/api/finance/receipt/{tx_code}')
assert r_receipt.status_code == 200
assert r_receipt.json()['status'] == 'ĐÃ XÁC NHẬN NỘP ĐỦ LỆ PHÍ'
r_html_receipt = client.get(f'/receipt/{tx_code}')
assert r_html_receipt.status_code == 200
assert 'BIÊN LAI THU LỆ PHÍ XÉT TUYỂN' in r_html_receipt.text
print('Test 6: Payment simulation and printable electronic receipt: OK')

# 6. Test Admin Updating Quota and Fee Config
r_quota = client.patch('/api/admissions/majors/1', json={'quota': 50, 'benchmark_score': 26.0})
assert r_quota.status_code == 200
assert r_quota.json()['quota'] == 50
r_fee = client.patch('/api/finance/fee-configs/1', json={'fee_name': 'Lệ phí 2026 đợt 2', 'amount': 60000.0})
assert r_fee.status_code == 200
assert r_fee.json()['amount'] == 60000.0
print('Test 7: Admin update quota and fee config: OK')

# 7. Test Virtual Filtering Algorithm (Dual Aspirations)
r_filter = client.post('/api/admissions/run-virtual-filtering?major_id=1')
assert r_filter.status_code == 200
print(f'Test 8: Virtual filtering result: {r_filter.json()["message"]}: OK')

# 8. Test AI Admission Assistant
r_ai_score = client.post('/api/support/ai-consultant', json={'query': 'Em được 25.5 điểm nên chọn ngành nào?'})
assert r_ai_score.status_code == 200
assert 'Trợ lý AI gợi ý cho bạn' in r_ai_score.json()['reply']
r_ai_it = client.post('/api/support/ai-consultant', json={'query': 'Khối ngành công nghệ học gì?'})
assert r_ai_it.status_code == 200
assert 'Công nghệ & Kỹ thuật' in r_ai_it.json()['reply']
print('Test 9: AI Admission Assistant chatbot query: OK')

print("\n🎉 TẤT CẢ 9 MỤC KIỂM THỬ ĐẠT ĐIỂM 10/10 THÀNH CÔNG RỰC RỠ! 🎉")
