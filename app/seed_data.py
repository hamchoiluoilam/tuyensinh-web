# Danh mục các môn học đại cương chung (áp dụng cho tất cả 40 ngành)
COMMON_GENERAL_SUBJECTS = [
    ("GEN101", "Triết học Mác - Lênin", 3, 1, "Đại cương chung", "Thế giới quan và phương pháp luận duy vật biện chứng, quy luật phát triển tự nhiên và xã hội."),
    ("GEN102", "Tiếng Anh Đại cương 1", 3, 1, "Đại cương chung", "Rèn luyện 4 kỹ năng nghe, nói, đọc, viết tiếng Anh giao tiếp cơ bản."),
    ("GEN103", "Pháp luật Đại cương", 2, 1, "Đại cương chung", "Nguồn gốc nhà nước, hệ thống pháp luật Việt Nam, quyền và nghĩa vụ công dân."),
    ("GEN201", "Kinh tế Chính trị Mác - Lênin", 2, 2, "Đại cương chung", "Hàng hóa, tiền tệ, giá trị thặng dư và quy luật kinh tế thị trường định hướng XHCN."),
    ("GEN202", "Tư tưởng Hồ Chí Minh", 2, 2, "Đại cương chung", "Hệ thống quan điểm toàn diện và sâu sắc của Chủ tịch Hồ Chí Minh về cách mạng Việt Nam."),
    ("GEN203", "Kỹ năng mềm & Làm việc nhóm", 2, 2, "Đại cương chung", "Kỹ năng thuyết trình, tư duy phản biện, giải quyết xung đột và làm việc nhóm hiệu quả.")
]

# Danh mục môn cơ sở và chuyên ngành đặc trưng cho từng ngành
MAJOR_SPECIFIC_SUBJECTS = {
    # --- KHỐI CÔNG NGHỆ & KỸ THUẬT ---
    "7480201": [ # CNTT
        ("IT101", "Nhập môn Lập trình Python", 3, 1, "Cơ sở ngành", "Cú pháp căn bản Python, hàm, hướng đối tượng cơ bản và thư viện chuẩn."),
        ("IT102", "Cơ sở dữ liệu & SQL", 3, 2, "Cơ sở ngành", "Mô hình ERD, chuẩn hóa dữ liệu, thiết kế CSDL quan hệ với PostgreSQL."),
        ("IT201", "Cấu trúc dữ liệu & Giải thuật", 4, 3, "Cơ sở ngành", "Danh sách liên kết, ngăn xếp, hàng đợi, cây nhị phân, thuật toán sắp xếp và tìm kiếm."),
        ("IT202", "Lập trình Hướng đối tượng C++", 3, 3, "Cơ sở ngành", "Tính đóng gói, kế thừa, đa hình, trừu tượng và mẫu thiết kế Design Patterns."),
        ("IT301", "Phát triển Ứng dụng Web Fullstack", 4, 4, "Chuyên ngành", "Xây dựng RESTful API với Python FastAPI và giao diện Single Page App hiện đại."),
        ("IT302", "Công nghệ Phần mềm & Agile/Scrum", 3, 4, "Chuyên ngành", "Vòng đời phần mềm, tài liệu đặc tả SRS, mô hình UML và quản trị dự án Scrum."),
        ("IT401", "Điện toán Đám mây & DevOps", 3, 5, "Chuyên ngành", "Đóng gói Docker containers, quy trình CI/CD và kiến trúc Microservices."),
        ("IT402", "Khóa luận Tốt nghiệp CNTT", 10, 8, "Khóa luận tốt nghiệp", "Nghiên cứu ứng dụng công nghệ hoặc phát triển sản phẩm phần mềm hoàn chỉnh.")
    ],
    "7480101": [ # Khoa học máy tính
        ("CS101", "Toán rời rạc & Giải thuật ứng dụng", 3, 1, "Cơ sở ngành", "Lý thuyết đồ thị, tổ hợp, logic mệnh đề và đại số Boole."),
        ("CS201", "Lý thuyết Tính toán & Ôtômat", 3, 3, "Cơ sở ngành", "Mô hình máy Turing, ngữ pháp phi ngữ cảnh và độ phức tạp tính toán."),
        ("CS301", "Thuật toán Nâng cao", 4, 4, "Chuyên ngành", "Quy hoạch động nâng cao, luồng cực đại và hình học tính toán."),
        ("CS302", "Thị giác Máy tính (Computer Vision)", 3, 5, "Chuyên ngành", "Xử lý ảnh số, mạng tích chập CNN, nhận diện vật thể và khuôn mặt."),
        ("CS401", "Xử lý Ngôn ngữ Tự nhiên (NLP)", 4, 6, "Chuyên ngành", "Mô hình Transformer, Word2Vec, trích xuất thực thể và tóm tắt văn bản.")
    ],
    "7480103": [ # Kỹ thuật phần mềm
        ("SE101", "Quy trình Phát triển Phần mềm", 3, 2, "Cơ sở ngành", "Mô hình thác nước, Agile, Scrum, Kanban và quản trị phiên bản Git."),
        ("SE201", "Kiến trúc & Thiết kế Phần mềm", 4, 3, "Chuyên ngành", "Clean Architecture, Domain-Driven Design (DDD) và Design Patterns."),
        ("SE301", "Kiểm thử & Đảm bảo Chất lượng (QA/QC)", 3, 4, "Chuyên ngành", "Kiểm thử tự động Selenium, PyTest, kiểm thử tải và bảo mật phần mềm."),
        ("SE302", "Lập trình Ứng dụng Di động Flutter/React Native", 4, 5, "Chuyên ngành", "Phát triển ứng dụng Android/iOS đa nền tảng kết nối API.")
    ],
    "7480202": [ # An toàn thông tin
        ("SEC101", "Nhập môn Mật mã học", 3, 2, "Cơ sở ngành", "Mật mã khóa đối xứng AES, khóa công khai RSA, hàm băm SHA và chữ ký số."),
        ("SEC201", "An toàn Mạng & Tường lửa", 3, 3, "Chuyên ngành", "Phân tích gói tin Wireshark, hệ thống IDS/IPS, VPN và mạng an toàn."),
        ("SEC301", "Kiểm thử Xâm nhập (Penetration Testing)", 4, 5, "Chuyên ngành", "Khai thác lỗ hổng OWASP Top 10, công cụ Metasploit, Burp Suite."),
        ("SEC302", "Điều tra Số & Ứng cứu Sự cố (Digital Forensics)", 3, 6, "Chuyên ngành", "Thu thập chứng cứ số, phân tích nhật ký log và khôi phục dữ liệu.")
    ],
    "7480107": [ # AI
        ("AI101", "Đại số Tuyến tính & Tối ưu hóa cho AI", 3, 1, "Cơ sở ngành", "Ma trận, vector, tích phân tối ưu gradient descent."),
        ("AI201", "Học sâu & Mạng nơ-ron (Deep Learning)", 4, 4, "Chuyên ngành", "Framework PyTorch, kiến trúc MLP, CNN, RNN và Attention mechanism."),
        ("AI301", "Mô hình Ngôn ngữ Lớn (LLMs & Generative AI)", 4, 6, "Chuyên ngành", "Prompt engineering, kỹ thuật RAG, Fine-tuning mô hình ngôn ngữ Llama."),
        ("AI302", "Học tăng cường & Robot thông minh", 3, 7, "Chuyên ngành", "Q-Learning, Policy Gradient và thuật toán điều khiển tự trị.")
    ],
    "7480108": [ # Data Science
        ("DS101", "Xác suất Thống kê cho Dữ liệu lớn", 3, 1, "Cơ sở ngành", "Phân phối xác suất, ước lượng tham số, kiểm định A/B testing."),
        ("DS201", "Khai phá & Tiền xử lý Dữ liệu", 3, 3, "Chuyên ngành", "Thư viện Pandas, NumPy, xử lý dữ liệu khuyết, Feature Engineering."),
        ("DS301", "Hạ tầng Dữ liệu lớn (Big Data)", 4, 5, "Chuyên ngành", "Apache Spark, Hadoop, Kafka và xây dựng Data Warehouse."),
        ("DS302", "Trực quan hóa Dữ liệu Kinh doanh (BI)", 3, 6, "Chuyên ngành", "Tableau, Power BI, thiết kế Dashboard thông minh hỗ trợ ra quyết định.")
    ],
    "7480204": [ # Mạng máy tính
        ("NET101", "Giao thức Mạng TCP/IP", 3, 2, "Cơ sở ngành", "Mô hình OSI, định tuyến RIP/OSPF/BGP, chuyển mạch phân đoạn VLAN."),
        ("NET201", "Lập trình Hệ thống Mạng", 3, 3, "Chuyên ngành", "Socket programming, WebSocket và truyền thông thời gian thực."),
        ("NET301", "Mạng Không dây & IoT", 3, 5, "Chuyên ngành", "Giao thức MQTT, cảm biến Zigbee, LoRa và vi điều khiển ESP32."),
        ("NET302", "Quản trị Hệ thống Linux Server", 3, 6, "Chuyên ngành", "Cấu hình Nginx, DNS BIND, DHCP, sao lưu và giám sát Zabbix.")
    ],
    "7480104": [ # HTTT
        ("IS101", "Phân tích & Thiết kế Hệ thống Thông tin", 3, 2, "Cơ sở ngành", "Sơ đồ dòng dữ liệu DFD, biểu đồ Use Case UML, thiết kế CSDL."),
        ("IS201", "Hệ thống Hoạch định Tài nguyên (ERP)", 3, 4, "Chuyên ngành", "Triển khai phần mềm quản trị Odoo/SAP, tích hợp quy trình doanh nghiệp."),
        ("IS301", "Quản trị Dự án Chuyển đổi số", 3, 5, "Chuyên ngành", "Chiến lược số hóa, quản lý thay đổi và đánh giá rủi ro công nghệ.")
    ],
    "7520216": [ # Tự động hóa
        ("AUT101", "Lý thuyết Điều khiển Tự động", 3, 2, "Cơ sở ngành", "Hàm truyền, quỹ đạo nghiệm số, biểu đồ Bode, bộ điều khiển PID."),
        ("AUT201", "Lập trình PLC & Mạng Công nghiệp", 4, 3, "Chuyên ngành", "PLC Siemens S7-1200, ngôn ngữ LAD/FBD, truyền thông Profinet."),
        ("AUT301", "Hệ thống Giám sát SCADA & HMI", 3, 5, "Chuyên ngành", "Thiết kế giao diện WinCC, thu thập dữ liệu và cảnh báo sự cố công nghiệp."),
        ("AUT302", "Cánh tay Robot Công nghiệp", 3, 6, "Chuyên ngành", "Động học Robot KUKA/ABB, lập trình quỹ đạo gắp đặt tự động.")
    ],
    "7520114": [ # Cơ điện tử
        ("MEC101", "Cơ sở Thiết kế Máy & CAD/CAM", 3, 2, "Cơ sở ngành", "Tính toán chi tiết máy, vẽ kỹ thuật SolidWorks và gia công CNC."),
        ("MEC201", "Cảm biến & Cơ cấu Chấp hành", 3, 3, "Chuyên ngành", "Động cơ bước, động cơ servo, xi lanh khí nén và thủy lực."),
        ("MEC301", "Hệ thống Nhúng Điều khiển", 4, 5, "Chuyên ngành", "Lập trình STM32/ARM, xử lý ngắt, PWM và giao tiếp SPI/I2C.")
    ],
    "7520130": [ # Ô tô
        ("OTO101", "Kết cấu Ô tô Hiện đại", 3, 2, "Cơ sở ngành", "Nguyên lý động cơ đốt trong, hệ thống treo, phanh ABS, lái điện EPS."),
        ("OTO201", "Điện - Điện tử Ô tô & Mạng CAN Bus", 3, 4, "Chuyên ngành", "Hệ thống phun xăng điện tử EFI, chẩn đoán lỗi OBD-II, mạng CAN."),
        ("OTO301", "Công nghệ Xe điện EV & Pin Lithium", 4, 5, "Chuyên ngành", "Động cơ xoay chiều ba pha, quản lý bộ pin BMS và trạm sạc điện."),
        ("OTO302", "Hệ thống Hỗ trợ Lái xe Nâng cao (ADAS)", 3, 6, "Chuyên ngành", "Cảm biến Radar, Camera nhận diện làn đường, phanh khẩn cấp tự động.")
    ],
    "7520207": [ # Điện tử viễn thông
        ("ECE101", "Mạch Điện tử Tương tự & Số", 3, 2, "Cơ sở ngành", "Transistor, Op-Amp, cổng logic, mạch vi xử lý và FPGA."),
        ("ECE201", "Xử lý Tín hiệu Số (DSP)", 3, 3, "Chuyên ngành", "Biến đổi Fourier nhanh FFT, bộ lọc số IIR/FIR."),
        ("ECE301", "Kỹ thuật Thông tin Vô tuyến & 5G", 3, 5, "Chuyên ngành", "Điều chế số QAM, công nghệ MIMO, ăng-ten mảng và mạng di động 5G.")
    ],
    "7520215": [ # Vi mạch bán dẫn
        ("SEMI101", "Vật lý Bán dẫn & Thiết bị Siêu vi", 3, 2, "Cơ sở ngành", "Vùng năng lượng, hạt tải điện, cấu trúc bóng bán dẫn FinFET."),
        ("SEMI201", "Thiết kế Mạch số với Verilog/VHDL", 4, 3, "Chuyên ngành", "Mô tả phần cứng RTL, mô phỏng ModelSim, tổng hợp mạch logic."),
        ("SEMI301", "Thiết kế Vi mạch Tích hợp VLSI", 4, 5, "Chuyên ngành", "Bố trí layout chip, kiểm tra quy tắc hình học DRC/LVS và Tape-out."),
        ("SEMI302", "Quy trình Chế tạo Bán dẫn Cleanroom", 3, 6, "Chuyên ngành", "Quang khắc Lithography, lắng đọng hơi CVD, khắc ăn mòn Etching.")
    ],
    "7580201": [ # Kỹ thuật xây dựng
        ("CIV101", "Sức bền Vật liệu & Cơ học Kết cấu", 4, 2, "Cơ sở ngành", "Biểu đồ nội lực mô men, lực cắt, ứng suất và chuyển vị kết cấu."),
        ("CIV201", "Kết cấu Bê tông Cốt thép", 4, 3, "Chuyên ngành", "Tính toán dầm, cột, móng, sàn theo tiêu chuẩn TCVN 5574."),
        ("CIV301", "Mô hình Thông tin Công trình (BIM Revit)", 3, 5, "Chuyên ngành", "Thiết kế 3D Revit kết cấu, phát hiện va chạm Navisworks."),
        ("CIV302", "Quản lý Dự án & Dự toán Xây dựng", 3, 6, "Chuyên ngành", "Bóc tách khối lượng, lập bảng dự toán chi phí và tiến độ thi công.")
    ],

    # --- KHỐI KINH TẾ & QUẢN LÝ ---
    "7340101": [ # Quản trị kinh doanh
        ("BA101", "Nguyên lý Quản trị học", 3, 1, "Cơ sở ngành", "Chức năng hoạch định, tổ chức bộ máy, phong cách lãnh đạo, kiểm tra."),
        ("BA201", "Quản trị Chiến lược Doanh nghiệp", 3, 3, "Chuyên ngành", "Mô hình 5 áp lực Porter, ma trận SWOT, định vị lợi thế cạnh tranh."),
        ("BA301", "Khởi sự Doanh nghiệp & Đổi mới sáng tạo", 3, 5, "Chuyên ngành", "Xây dựng mô hình kinh doanh Canvas, gọi vốn đầu tư thiên thần."),
        ("BA302", "Quản trị Rủi ro & Khủng hoảng Doanh nghiệp", 3, 6, "Chuyên ngành", "Nhận diện rủi ro tài chính, vận hành và phương án ứng phó.")
    ],
    "7340115": [ # Marketing
        ("MKT101", "Marketing Căn bản", 3, 1, "Cơ sở ngành", "Nghiên cứu thị trường, hành vi khách hàng, phối thức Marketing-Mix 4P/7P."),
        ("MKT201", "Digital Marketing & SEO/SEM", 3, 3, "Chuyên ngành", "Tối ưu hóa công cụ tìm kiếm, quảng cáo Google Ads, Meta Ads."),
        ("MKT301", "Quản trị Thương hiệu (Brand Management)", 3, 4, "Chuyên ngành", "Định vị thương hiệu, đo lường tài sản thương hiệu, chiến dịch lan tỏa."),
        ("MKT302", "Sáng tạo Nội dung & Tiếp thị Đa kênh", 3, 5, "Chuyên ngành", "Content marketing, kịch bản video ngắn TikTok, Omnichannel marketing.")
    ],
    "7340120": [ # Kinh doanh quốc tế
        ("IB101", "Môi trường Kinh doanh Toàn cầu", 3, 2, "Cơ sở ngành", "Xu hướng toàn cầu hóa, các hiệp định thương mại tự do CPTPP, EVFTA."),
        ("IB201", "Thanh toán & Tín dụng Quốc tế", 3, 3, "Chuyên ngành", "Phương thức tín dụng chứng từ L/C, nhờ thu D/A, D/P, chuyển tiền T/T."),
        ("IB301", "Đàm phán & Hợp đồng Ngoại thương", 3, 5, "Chuyên ngành", "Điều kiện Incoterms 2020, soạn thảo hợp đồng xuất nhập khẩu quốc tế.")
    ],
    "7340201": [ # Tài chính ngân hàng
        ("FIN101", "Thị trường Tài chính & Định chế", 3, 2, "Cơ sở ngành", "Thị trường tiền tệ, trái phiếu, cổ phiếu và chính sách ngân hàng trung ương."),
        ("FIN201", "Phân tích & Đầu tư Chứng khoán", 3, 3, "Chuyên ngành", "Phân tích cơ bản định giá cổ phiếu, phân tích kỹ thuật biểu đồ nến."),
        ("FIN301", "Nghiệp vụ Ngân hàng Thương mại", 3, 4, "Chuyên ngành", "Thẩm định tín dụng khách hàng doanh nghiệp, quản trị rủi ro nợ xấu."),
        ("FIN302", "Công nghệ Tài chính (Fintech) & Ngân hàng số", 3, 6, "Chuyên ngành", "Ví điện tử, công nghệ Blockchain, thanh toán Open Banking API.")
    ],
    "7340301": [ # Kế toán
        ("ACC101", "Nguyên lý Kế toán", 3, 1, "Cơ sở ngành", "Ghi chép chứng từ kế toán, định khoản kép nợ/có, lập bảng cân đối kế toán."),
        ("ACC201", "Kế toán Tài chính Doanh nghiệp 1 & 2", 4, 3, "Chuyên ngành", "Kế toán doanh thu, tài sản cố định, vốn chủ sở hữu theo chuẩn VAS/IFRS."),
        ("ACC301", "Kế toán Quản trị & Phân tích Chi phí", 3, 4, "Chuyên ngành", "Phân tích điểm hòa vốn, dự toán ngân sách và định giá sản phẩm.")
    ],
    "7340302": [ # Kiểm toán
        ("AUD101", "Kiểm toán Căn bản", 3, 2, "Cơ sở ngành", "Bằng chứng kiểm toán, tính trọng yếu và đánh giá rủi ro kiểm toán."),
        ("AUD201", "Kiểm toán Báo cáo Tài chính", 4, 4, "Chuyên ngành", "Thủ tục kiểm tra chi tiết số dư, kiểm tra tuân thủ và lập biên bản kiểm toán."),
        ("AUD301", "Hệ thống Kiểm soát Nội bộ", 3, 5, "Chuyên ngành", "Khuôn khổ COSO, nhận diện gian lận và kiểm tra tính tuân thủ quy trình.")
    ],
    "7340122": [ # TMĐT
        ("EC101", "Tổng quan Thương mại Điện tử", 3, 1, "Cơ sở ngành", "Các mô hình B2B, B2C, D2C, kinh tế nền tảng số và mạng xã hội."),
        ("EC201", "Cổng Thanh toán & Bảo mật TMĐT", 3, 3, "Chuyên ngành", "Tích hợp VNPay, Momo, Stripe, tiêu chuẩn an toàn bảo mật PCI-DSS."),
        ("EC301", "Vận hành Sàn TMĐT & Livestream Bán hàng", 3, 4, "Chuyên ngành", "Thuật toán hiển thị Shopee, TikTok Shop, quản lý kho đa kênh."),
        ("EC302", "Phân tích Dữ liệu Khách hàng TMĐT", 3, 5, "Chuyên ngành", "Google Analytics 4, tỷ lệ chuyển đổi CRO, hành trình mua sắm.")
    ],
    "7510605": [ # Logistics
        ("LOG101", "Tổng quan Chuỗi Cung ứng (SCM)", 3, 2, "Cơ sở ngành", "Mô hình SCOR, tích hợp dòng sản phẩm, dòng tiền và thông tin."),
        ("LOG201", "Quản trị Kho bãi & Trung tâm Phân phối", 3, 3, "Chuyên ngành", "Phần mềm WMS, thiết kế bố trí kho hàng, quản trị tồn kho JIT."),
        ("LOG301", "Giao nhận Vận tải Đa phương thức Quốc tế", 3, 4, "Chuyên ngành", "Vận đơn Bill of Lading, dịch vụ Freight Forwarder, thủ tục hải quan."),
        ("LOG302", "Thu mua & Quản lý Nhà cung ứng (Procurement)", 3, 5, "Chuyên ngành", "Chiến lược đấu thầu thu mua, đàm phán hợp đồng cung ứng bền vững.")
    ],
    "7340404": [ # Quản trị nhân lực
        ("HR101", "Quản trị Nguồn Nhân lực Căn bản", 3, 1, "Cơ sở ngành", "Hoạch định nhân sự, phân tích công việc, bản mô tả công việc JD."),
        ("HR201", "Đào tạo & Phát triển Nhân tài", 3, 3, "Chuyên ngành", "Quy trình đào tạo ADDIE, xây dựng khung năng lực nhân viên."),
        ("HR301", "Tiền lương & Đãi ngộ (C&B)", 3, 4, "Chuyên ngành", "Xây dựng thang bảng lương, chính sách thưởng, bảo hiểm xã hội và thuế.")
    ],
    "7380107": [ # Luật kinh tế
        ("LAW101", "Pháp luật Doanh nghiệp", 3, 2, "Cơ sở ngành", "Thủ tục thành lập, giải thể công ty cổ phần, TNHH, quyền lợi cổ đông."),
        ("LAW201", "Pháp luật Hợp đồng Thương mại", 3, 3, "Chuyên ngành", "Soạn thảo hợp đồng, điều khoản miễn trừ, xử lý vi phạm hợp đồng."),
        ("LAW301", "Giải quyết Tranh chấp Kinh doanh Thương mại", 3, 5, "Chuyên ngành", "Trọng tài thương mại VIAC, thủ tục tố tụng tòa án kinh tế.")
    ],
    "7310106": [ # Kinh tế đối ngoại
        ("EXT101", "Lý thuyết Kinh tế Quốc tế", 3, 2, "Cơ sở ngành", "Lợi thế so sánh, thuế quan, hạn ngạch và cán cân thanh toán quốc gia."),
        ("EXT201", "Đầu tư Trực tiếp Nước ngoài (FDI)", 3, 3, "Chuyên ngành", "Chính sách thu hút FDI, tập đoàn đa quốc gia và chuyển giá quốc tế."),
        ("EXT301", "Thị trường Hàng hóa & Phái sinh Quốc tế", 3, 5, "Chuyên ngành", "Giao dịch hợp đồng tương lai, hợp đồng quyền chọn hàng hóa.")
    ],
    "7810103": [ # Du lịch
        ("TOU101", "Tài nguyên & Địa lý Du lịch Việt Nam", 3, 1, "Cơ sở ngành", "Di sản văn hóa UNESCO, danh lam thắng cảnh và tuyến điểm du lịch."),
        ("TOU201", "Thiết kế & Định giá Sản phẩm Tour", 3, 3, "Chuyên ngành", "Lập lịch trình tour, tính giá vốn và chiến lược định giá bán tour."),
        ("TOU301", "Nghiệp vụ Hướng dẫn & Điều hành Tour", 3, 4, "Chuyên ngành", "Thuyết minh tuyến điểm, tâm lý du khách, xử lý tình huống khẩn cấp.")
    ],
    "7810201": [ # Khách sạn
        ("HOT101", "Tổng quan Ngành Khách sạn & Resort", 3, 1, "Cơ sở ngành", "Cơ cấu tổ chức khách sạn, tiêu chuẩn xếp hạng sao quốc tế."),
        ("HOT201", "Quản trị Tiền sảnh (Front Office)", 3, 3, "Chuyên ngành", "Quy trình check-in/out, phần mềm quản lý phòng Opera PMS."),
        ("HOT301", "Quản trị Ẩm thực & Yến tiệc (F&B)", 3, 4, "Chuyên ngành", "Nghiệp vụ bàn, quầy bar, tổ chức hội nghị và tiệc cưới chuyên nghiệp.")
    ],

    # --- KHỐI NGOẠI NGỮ & XÃ HỘI ---
    "7220201": [ # Ngôn ngữ Anh
        ("EN101", "Ngữ âm & Âm vị học tiếng Anh", 3, 1, "Cơ sở ngành", "Bảng phiên âm quốc tế IPA, trọng âm từ, nối âm và ngữ điệu câu."),
        ("EN201", "Viết Luận Học thuật (Academic Writing)", 4, 3, "Chuyên ngành", "Tư duy phản biện, cấu trúc bài luận học thuật, trích dẫn chuẩn APA."),
        ("EN301", "Biên - Phiên dịch Chuyên ngành Kinh tế", 4, 4, "Chuyên ngành", "Dịch thuật hợp đồng thương mại, báo cáo tài chính thường niên."),
        ("EN302", "Tiếng Anh Thương mại & Đàm phán Quốc tế", 3, 5, "Chuyên ngành", "Soạn email công vụ, thuyết trình dự án và đàm phán bằng tiếng Anh.")
    ],
    "7220204": [ # Ngôn ngữ Trung
        ("CN101", "Ngữ âm & Chữ Hán Căn bản", 3, 1, "Cơ sở ngành", "Quy tắc phát âm Pinyin, cấu tạo bộ thủ chữ Hán, ngữ pháp căn bản."),
        ("CN201", "Tiếng Trung Thương mại & Thư tín", 3, 3, "Chuyên ngành", "Giao dịch đàm phán thương mại, hợp đồng xuất nhập khẩu đối tác Trung."),
        ("CN301", "Biên dịch & Phiên dịch Hán - Việt", 4, 5, "Chuyên ngành", "Dịch thuật tin tức kinh tế, phiên dịch hội nghị và đàm phán.")
    ],
    "7220209": [ # Ngôn ngữ Nhật
        ("JP101", "Nhập môn Tiếng Nhật & Chữ Hán Kanji", 4, 1, "Cơ sở ngành", "Bảng chữ cái Hiragana, Katakana, quy tắc viết 500 chữ Kanji cơ bản."),
        ("JP201", "Tiếng Nhật Doanh nghiệp & Kính ngữ", 3, 3, "Chuyên ngành", "Văn hóa giao tiếp công sở Nhật, kính ngữ Sonkeigo, khiêm nhường ngữ."),
        ("JP301", "Dịch thuật Công nghệ IT Comtor", 4, 5, "Chuyên ngành", "Thuật ngữ ngành phần mềm, dịch tài liệu thiết kế đặc tả kỹ thuật.")
    ],
    "7220210": [ # Ngôn ngữ Hàn
        ("KR101", "Chữ viết Hangeul & Ngữ pháp Căn bản", 3, 1, "Cơ sở ngành", "Quy tắc biến âm, cấu trúc câu tiếng Hàn, giao tiếp hàng ngày."),
        ("KR201", "Tiếng Hàn Thương mại Doanh nghiệp", 3, 3, "Chuyên ngành", "Văn hóa doanh nghiệp Hàn Quốc, email trao đổi đối tác tập đoàn."),
        ("KR301", "Biên phiên dịch Hàn - Việt Chuyên sâu", 4, 5, "Chuyên ngành", "Dịch đuổi hội thoại, dịch thuật tài liệu kinh tế và văn hóa.")
    ],
    "7320108": [ # Quan hệ công chúng PR
        ("PR101", "Nhập môn Quan hệ Công chúng (PR)", 3, 1, "Cơ sở ngành", "Bản chất truyền thông đại chúng, phân biệt PR và quảng cáo."),
        ("PR201", "Quản trị Khủng hoảng Truyền thông", 3, 3, "Chuyên ngành", "Kỹ thuật phản hồi dư luận, tổ chức họp báo, dập tắt tin đồn xấu."),
        ("PR301", "Lập kế hoạch & Tổ chức Sự kiện (Event)", 4, 4, "Chuyên ngành", "Viết kịch bản proposal sự kiện, điều phối âm thanh ánh sáng thực tế.")
    ],
    "7320101": [ # Báo chí truyền thông
        ("JOU101", "Kỹ năng Phỏng vấn & Viết tin Báo chí", 3, 1, "Cơ sở ngành", "Cấu trúc tháp ngược, kỹ thuật khai thác nguồn tin và viết bài phóng sự."),
        ("JOU201", "Sản xuất Chương trình Podcast & Video", 4, 3, "Chuyên ngành", "Thu âm phòng thu, dựng phim Premiere/Capcut, biên tập kịch bản hình."),
        ("JOU301", "Báo chí Dữ liệu (Data Journalism)", 3, 5, "Chuyên ngành", "Trực quan hóa số liệu Infographic, phân tích dữ liệu điều tra báo chí.")
    ],
    "7210403": [ # Thiết kế đồ họa
        ("DES101", "Nguyên lý Thị giác & Nghệ thuật Chữ (Typography)", 3, 1, "Cơ sở ngành", "Bố cục thị giác, bánh xe màu sắc, tâm lý học tiếp nhận hình ảnh."),
        ("DES201", "Thiết kế Bộ Nhận diện Thương hiệu", 4, 3, "Chuyên ngành", "Thiết kế logo, cẩm nang thương hiệu Brand Guideline trên Illustrator."),
        ("DES301", "Thiết kế Giao diện UI/UX trên Figma", 3, 4, "Chuyên ngành", "Nghiên cứu người dùng, Wireframe, Prototype và hệ thống Design System.")
    ],
    "7310401": [ # Tâm lý học
        ("PSY101", "Tâm lý học Đại cương", 3, 1, "Cơ sở ngành", "Bản chất ý thức, cảm xúc, động cơ hành vi và sự hình thành nhân cách."),
        ("PSY201", "Kỹ năng Tham vấn & Trị liệu Tâm lý", 3, 3, "Chuyên ngành", "Lắng nghe chủ động, kỹ thuật thấu cảm, đạo đức nghề nghiệp tham vấn."),
        ("PSY301", "Tâm lý học Tổ chức & Nhân sự", 3, 4, "Chuyên ngành", "Động lực làm việc của nhân viên, giải tỏa căng thẳng stress công sở.")
    ],

    # --- KHỐI Y DƯỢC, SINH HỌC & KIẾN TRÚC ---
    "7720101": [ # Y khoa
        ("MED101", "Giải phẫu học Người Toàn diện", 4, 1, "Cơ sở ngành", "Cấu tạo hệ xương khớp, hệ tuần hoàn, hô hấp và thần kinh trung ương."),
        ("MED201", "Sinh lý Bệnh & Miễn dịch học Lâm sàng", 4, 3, "Cơ sở ngành", "Cơ chế sinh bệnh, phản ứng viêm, kháng thể và đáp ứng miễn dịch."),
        ("MED301", "Bệnh học Nội khoa & Thực tập Bệnh viện", 5, 5, "Chuyên ngành", "Thăm khám lâm sàng tại giường bệnh, phân tích kết quả cận lâm sàng."),
        ("MED302", "Bệnh học Ngoại khoa & Phẫu thuật Thực hành", 5, 6, "Chuyên ngành", "Nguyên tắc vô khuẩn phòng mổ, kỹ thuật khâu vết thương, phẫu thuật cơ bản.")
    ],
    "7720201": [ # Dược học
        ("PHA101", "Hóa Dược học 1 & 2", 4, 2, "Cơ sở ngành", "Cấu trúc hóa học của dược chất, mối liên quan cấu trúc và hoạt tính."),
        ("PHA201", "Công nghệ Bào chế & Sinh Dược học", 4, 4, "Chuyên ngành", "Quy trình dập viên nén, sản xuất dung dịch siro, thuốc tiêm vô trùng."),
        ("PHA301", "Dược lý & Dược Lâm sàng", 4, 5, "Chuyên ngành", "Cơ chế tác dụng thuốc, tương tác thuốc, hướng dẫn sử dụng thuốc an toàn.")
    ],
    "7720301": [ # Điều dưỡng
        ("NUR101", "Kỹ thuật Điều dưỡng Cơ bản", 3, 2, "Cơ sở ngành", "Đo dấu hiệu sinh tồn mạch nhiệt áp, tiêm truyền, băng bó và thay băng."),
        ("NUR201", "Chăm sóc Bệnh nhân Hồi sức Cấp cứu", 4, 4, "Chuyên ngành", "Cấp cứu ngừng tuần hoàn CPR, hỗ trợ thở máy, theo dõi máy Monitor."),
        ("NUR301", "Điều dưỡng Ngoại khoa & Chăm sóc Sau mổ", 3, 5, "Chuyên ngành", "Chăm sóc dẫn lưu, phục hồi chức năng sau mổ và chống loét tì đè.")
    ],
    "7420201": [ # Công nghệ sinh học
        ("BIO101", "Sinh học Phân tử & Tế bào", 3, 1, "Cơ sở ngành", "Cấu trúc axit nucleic DNA/RNA, phiên mã, dịch mã và điều hòa gen."),
        ("BIO201", "Kỹ thuật Di truyền & Công nghệ Gen", 4, 3, "Chuyên ngành", "Phản ứng PCR, điện di gel, nhân dòng plasmid và chỉnh sửa gen CRISPR."),
        ("BIO301", "Công nghệ Vi sinh & Lên men Công nghiệp", 3, 4, "Chuyên ngành", "Nuôi cấy vi sinh vật quy mô lớn, sản xuất enzym, chế phẩm sinh học.")
    ],
    "7580101": [ # Kiến trúc
        ("ARC101", "Cơ sở Tạo hình & Vẽ Mỹ thuật Không gian", 4, 1, "Cơ sở ngành", "Quy luật phối cảnh 1-2 điểm tụ, dựng hình khối, đánh bóng kiến trúc."),
        ("ARC201", "Nguyên lý Thiết kế Kiến trúc Nhà ở", 3, 3, "Chuyên ngành", "Quy hoạch không gian sống, chiếu sáng tự nhiên và thông gió vi khí hậu."),
        ("ARC301", "Đồ án Kiến trúc Công trình Công cộng", 5, 5, "Chuyên ngành", "Thiết kế tổ hợp trường học, bảo tàng, trung tâm văn hóa cộng đồng.")
    ]
}

# 40 Ngành tuyển sinh với mô tả hoàn chỉnh
MAJORS_META = [
    ("7480201", "Công nghệ thông tin", "Công nghệ & Kỹ thuật", 100, 25.5, "Đào tạo kỹ sư phát triển phần mềm, ứng dụng web, di động, an ninh mạng và quản trị hệ thống hạ tầng CNTT."),
    ("7480101", "Khoa học máy tính", "Công nghệ & Kỹ thuật", 80, 26.5, "Nghiên cứu nền tảng toán học tin học, thuật toán nâng cao, thị giác máy tính và xử lý ngôn ngữ tự nhiên."),
    ("7480103", "Kỹ thuật phần mềm", "Công nghệ & Kỹ thuật", 90, 25.0, "Quy trình thiết kế kiến trúc phần mềm quy mô lớn, kiểm thử tự động, quản lý dự án Agile/Scrum."),
    ("7480202", "An toàn thông tin", "Công nghệ & Kỹ thuật", 70, 24.8, "Phòng thủ an ninh mạng, phân tích mã độc, mật mã học, điều tra số và ứng phó sự cố tấn công mạng."),
    ("7480107", "Trí tuệ nhân tạo (AI)", "Công nghệ & Kỹ thuật", 60, 27.0, "Chuyên sâu về học sâu (Deep Learning), mạng nơ-ron nhân tạo, mô hình sinh (Generative AI) và xe tự hành."),
    ("7480108", "Khoa học dữ liệu (Data Science)", "Công nghệ & Kỹ thuật", 60, 25.8, "Phân tích dữ liệu lớn (Big Data), khai phá tri thức, mô hình hóa dự báo kinh doanh và trực quan hóa dữ liệu."),
    ("7480204", "Mạng máy tính & Truyền thông dữ liệu", "Công nghệ & Kỹ thuật", 50, 23.5, "Thiết kế hạ tầng mạng viễn thông, mạng thế hệ mới 5G/6G, điện toán biên và Internet vạn vật (IoT)."),
    ("7480104", "Hệ thống thông tin quản lý", "Công nghệ & Kỹ thuật", 70, 24.0, "Cầu nối giữa công nghệ và nghiệp vụ doanh nghiệp, thiết kế ERP, CRM và chuyển đổi số tổ chức."),
    ("7520216", "Kỹ thuật điều khiển & Tự động hóa", "Công nghệ & Kỹ thuật", 80, 24.5, "Lập trình PLC, cánh tay robot công nghiệp, hệ thống SCADA và dây chuyền nhà máy thông minh."),
    ("7520114", "Kỹ thuật cơ điện tử", "Công nghệ & Kỹ thuật", 70, 24.0, "Giao thoa giữa cơ khí chính xác, điện tử thông minh và phần mềm điều khiển thiết bị hiện đại."),
    ("7520130", "Kỹ thuật ô tô", "Công nghệ & Kỹ thuật", 85, 24.2, "Công nghệ động cơ đốt trong, xe điện EV, hệ thống truyền lực, phanh ABS, tự lái và chuẩn đoán ô tô."),
    ("7520207", "Kỹ thuật điện tử - viễn thông", "Công nghệ & Kỹ thuật", 65, 23.5, "Mạch điện tử cao tần, xử lý tín hiệu số DSP, thông tin vệ tinh và truyền sóng vô tuyến."),
    ("7520215", "Thiết kế vi mạch & Bán dẫn", "Công nghệ & Kỹ thuật", 50, 26.0, "Ngành công nghệ chiến lược quốc gia: Thiết kế vi mạch tích hợp VLSI, chip bán dẫn, ngôn ngữ Verilog/VHDL."),
    ("7580201", "Kỹ thuật xây dựng", "Công nghệ & Kỹ thuật", 60, 21.5, "Thiết kế kết cấu bê tông cốt thép, mô hình hóa BIM, quản lý thi công công trình dân dụng và công nghiệp."),

    ("7340101", "Quản trị kinh doanh", "Kinh tế & Quản lý", 120, 23.5, "Quản trị chiến lược, điều hành doanh nghiệp tổng thể, lãnh đạo và tư duy quản lý hiện đại."),
    ("7340115", "Marketing & Truyền thông số", "Kinh tế & Quản lý", 90, 25.0, "Nghiên cứu thị trường, tiếp thị kỹ thuật số Digital Marketing, SEO/SEM, mạng xã hội và thương hiệu."),
    ("7340120", "Kinh doanh quốc tế", "Kinh tế & Quản lý", 80, 25.5, "Giao thương toàn cầu, hợp đồng ngoại thương quốc tế, điều kiện Incoterms và thanh toán quốc tế."),
    ("7340201", "Tài chính - Ngân hàng", "Kinh tế & Quản lý", 100, 24.0, "Thị trường chứng khoán, quản trị ngân hàng thương mại, định giá tài sản tài chính và Fintech."),
    ("7340301", "Kế toán doanh nghiệp", "Kinh tế & Quản lý", 90, 23.0, "Lập báo cáo tài chính, hạch toán chi phí giá thành, chuẩn mực kế toán Việt Nam (VAS) và quốc tế (IFRS)."),
    ("7340302", "Kiểm toán", "Kinh tế & Quản lý", 50, 24.2, "Kiểm toán độc lập báo cáo tài chính, kiểm soát nội bộ doanh nghiệp và đạo đức nghề nghiệp kiểm toán."),
    ("7340122", "Thương mại điện tử", "Kinh tế & Quản lý", 85, 25.2, "Kinh doanh trên các sàn Shopee, TikTok Shop, Amazon, cổng thanh toán số và tối ưu trải nghiệm khách hàng."),
    ("7510605", "Logistics & Quản lý chuỗi cung ứng", "Kinh tế & Quản lý", 95, 26.0, "Vận tải đa phương thức hàng không/đường biển, quản lý kho bãi, tồn kho JIT và tối ưu mạng lưới cung ứng."),
    ("7340404", "Quản trị nhân lực", "Kinh tế & Quản lý", 60, 23.0, "Thu hút nhân tài, xây dựng văn hóa doanh nghiệp, chế độ đãi ngộ C&B, đánh giá hiệu suất KPI/OKR."),
    ("7380107", "Luật kinh tế", "Kinh tế & Quản lý", 80, 24.0, "Pháp luật doanh nghiệp, hợp đồng thương mại, giải quyết tranh chấp trọng tài kinh tế và sở hữu trí tuệ."),
    ("7310106", "Kinh tế đối ngoại", "Kinh tế & Quản lý", 70, 26.2, "Chính sách thương mại quốc tế, dòng vốn đầu tư trực tiếp FDI, tỷ giá hối đoái và kinh tế thế giới."),
    ("7810103", "Quản trị dịch vụ du lịch & lữ hành", "Kinh tế & Quản lý", 60, 22.0, "Thiết kế tour du lịch trong nước và quốc tế, hướng dẫn viên du lịch, điều hành lữ hành chuyên nghiệp."),
    ("7810201", "Quản trị khách sạn", "Kinh tế & Quản lý", 70, 22.8, "Quản lý tiền sảnh Front Office, bộ phận ẩm thực F&B, buồng phòng Housekeeping theo tiêu chuẩn 5 sao."),

    ("7220201", "Ngôn ngữ Anh", "Ngoại ngữ & Xã hội", 110, 24.5, "Thành thạo tiếng Anh học thuật C1, dịch thuật kinh tế ngoại giao, phương pháp giảng dạy tiếng Anh quốc tế."),
    ("7220204", "Ngôn ngữ Trung Quốc", "Ngoại ngữ & Xã hội", 90, 25.0, "Chuẩn đầu ra HSK 6, tiếng Trung thương mại, dịch thuật kinh tế và văn hóa giao tiếp đối tác Trung Hoa."),
    ("7220209", "Ngôn ngữ Nhật", "Ngoại ngữ & Xã hội", 80, 24.0, "Chuẩn đầu ra JLPT N2/N1, văn hóa doanh nghiệp Nhật Bản (Hourensou), thông dịch viên IT Comtor."),
    ("7220210", "Ngôn ngữ Hàn Quốc", "Ngoại ngữ & Xã hội", 80, 25.2, "Chuẩn đầu ra TOPIK 5/6, làm việc tại các tập đoàn Samsung, LG, Hyundai và giao lưu văn hóa Hallyu."),
    ("7320108", "Quan hệ công chúng (PR)", "Ngoại ngữ & Xã hội", 70, 25.8, "Xử lý khủng hoảng truyền thông, tổ chức sự kiện chuyên nghiệp, xây dựng hình ảnh đại chúng cho thương hiệu."),
    ("7320101", "Báo chí & Truyền thông đa phương tiện", "Ngoại ngữ & Xã hội", 65, 25.0, "Sáng tạo nội dung podcast, phóng sự truyền hình, kỹ xảo dựng video, báo chí điện tử hiện đại."),
    ("7210403", "Thiết kế đồ họa", "Ngoại ngữ & Xã hội", 80, 24.2, "Nhận diện thương hiệu, thiết kế bao bì, giao diện UI/UX số, minh họa hoạt hình 2D/3D chuyên nghiệp."),
    ("7310401", "Tâm lý học", "Ngoại ngữ & Xã hội", 50, 24.0, "Tham vấn tâm lý học đường, tâm lý học hành vi tổ chức, đánh giá trị liệu tâm lý cho cộng đồng."),

    ("7720101", "Y khoa (Bác sĩ đa khoa)", "Y Dược - Sinh học - Kiến trúc", 60, 27.8, "Chương trình bác sĩ y khoa 6 năm: Giải phẫu học, sinh lý bệnh, chẩn đoán hình ảnh và lâm sàng bệnh viện."),
    ("7720201", "Dược học", "Y Dược - Sinh học - Kiến trúc", 70, 25.5, "Dược sĩ đại học: Hóa dược, bào chế thuốc, dược lý học, kiểm nghiệm chất lượng và dược lâm sàng."),
    ("7720301", "Điều dưỡng", "Y Dược - Sinh học - Kiến trúc", 80, 21.0, "Chăm sóc người bệnh toàn diện, cấp cứu hồi sức, kiểm soát nhiễm khuẩn và đạo đức điều dưỡng viên."),
    ("7420201", "Công nghệ sinh học", "Y Dược - Sinh học - Kiến trúc", 50, 22.5, "Công nghệ gen, nuôi cấy mô tế bào thực vật, vi sinh vật học ứng dụng và sản xuất chế phẩm sinh học."),
    ("7580101", "Kiến trúc", "Y Dược - Sinh học - Kiến trúc", 50, 23.5, "Sáng tạo không gian kiến trúc cảnh quan, thiết kế công trình xanh bền vững và đồ án kiến trúc công cộng.")
]

# Tạo danh sách 40 ngành kèm cả Môn Đại Cương Chung và Môn Chuyên Ngành
MAJORS_40 = []
for code, name, category, quota, benchmark, desc in MAJORS_META:
    # Môn đại cương chung (6 môn) + môn chuyên ngành đặc trưng
    specific = MAJOR_SPECIFIC_SUBJECTS.get(code, [
        (f"SPE-{code[-3:]}-1", f"Cơ sở chuyên ngành {name}", 3, 3, "Cơ sở ngành", f"Kiến thức nền tảng và phương pháp luận ngành {name}."),
        (f"SPE-{code[-3:]}-2", f"Chuyên đề nâng cao ngành {name}", 4, 5, "Chuyên ngành", f"Ứng dụng thực hành chuyên sâu và giải quyết vấn đề trong ngành {name}."),
        (f"SPE-{code[-3:]}-3", f"Thực tập doanh nghiệp ngành {name}", 3, 6, "Chuyên ngành", f"Trải nghiệm môi trường làm việc thực tế và cọ xát nghiệp vụ {name}."),
        (f"SPE-{code[-3:]}-4", f"Đồ án / Khóa luận tốt nghiệp {name}", 10, 8, "Khóa luận tốt nghiệp", f"Đồ án tốt nghiệp tổng hợp kiến thức toàn khóa học {name}.")
    ])
    
    # Kết hợp đầy đủ: Đại cương chung (6 môn) + Chuyên ngành
    full_subjects = list(COMMON_GENERAL_SUBJECTS) + specific
    
    MAJORS_40.append({
        "code": code,
        "name": name,
        "category": category,
        "quota": quota,
        "benchmark_score": benchmark,
        "description": desc,
        "subjects": full_subjects
    })
