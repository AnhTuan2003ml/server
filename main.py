"""
Main entry point cho Payment API Service
Flask API đơn giản để tạo QR code thanh toán
"""

import sys
import socket
import json
import base64
import os
from flask import Flask, jsonify, Response, request, send_from_directory

# Tạo Flask app
app = Flask(__name__)

# Import hàm xử lý từ qr_code module
try:
    from apis import qr_code
    print("✅ Đã import module QR Code")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.qr_code: {e}")
    sys.exit(1)

# Import hàm xử lý từ authentication module
try:
    from apis import authencation
    print("✅ Đã import module Authentication")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.authencation: {e}")
    sys.exit(1)

# Import hàm xử lý từ add_count module
try:
    from apis import add_count
    print("✅ Đã import module Add Count")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.add_count: {e}")
    sys.exit(1)

# Import hàm xử lý từ check module
try:
    from apis import check
    print("✅ Đã import module Check")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.check: {e}")
    sys.exit(1)

# Import hàm xử lý từ creat_otp module
try:
    from apis import creat_otp
    print("✅ Đã import module Create OTP")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.creat_otp: {e}")
    sys.exit(1)

# Import hàm xử lý từ check_login module
try:
    from apis import check_login
    print("✅ Đã import module Check Login")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.check_login: {e}")
    sys.exit(1)

# Import hàm xử lý từ config_api module
try:
    from apis import config_api
    print("✅ Đã import module Config API")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.config_api: {e}")
    sys.exit(1)

# Import hàm xử lý từ session_manager module
try:
    from apis import session_manager
    print("✅ Đã import module Session Manager")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.session_manager: {e}")
    sys.exit(1)

# Import hàm xử lý từ user module
try:
    from apis import user as user_api
    print("✅ Đã import module User API")
except ImportError as e:
    print(f"❌ Lỗi khi import apis.user: {e}")
    # Không exit vì có thể chưa có module này


def lay_ip_local():
    """Lấy địa chỉ IP local của máy"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def doc_token(token_file="config/mytoken.txt"):
    """
    Đọc token từ file config
    
    Args:
        token_file: Đường dẫn đến file token
        
    Returns:
        str: Token từ file (hoặc None nếu có lỗi)
    """
    try:
        with open(token_file, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file token: {token_file}")
        return None
    except Exception as e:
        print(f"❌ Lỗi khi đọc file token: {e}")
        return None


def xac_thuc_token(token):
    """
    Xác thực token từ request với token trong file config
    
    Args:
        token: Token từ request
        
    Returns:
        bool: True nếu token hợp lệ, False nếu không hợp lệ
    """
    valid_token = doc_token()
    if not valid_token:
        return False
    return token == valid_token


def in_thong_tin_api(port, local_ip):
    """In thông tin các API endpoints"""
    print("="*60)
    print("🚀 API Service đã sẵn sàng!")
    print("="*60)
    print(f"📍 Local: http://localhost:{port}")
    print(f"📍 Mạng nội bộ: http://{local_ip}:{port}")
    print("="*60)
    print("📋 Available Endpoints:")
    print(f"   • GET  http://localhost:{port}/qr              - Tạo QR code thanh toán")
    print(f"       Query: ?sl=<số_lượng> (optional) - Số lượng để tính toán số tiền")
    print(f"              ?format=json (optional) - Trả về JSON với id và qr_code base64")
    print(f"       Header: X-QR-ID chứa id khi trả về image")
    print(f"   • GET  http://localhost:{port}/admin           - Giao diện đăng nhập admin")
    print(f"   • POST http://localhost:{port}/authentication  - API authentication (hiển thị thông tin nhận được)")
    print(f"   • POST http://localhost:{port}/add_count       - Tăng count cho tài khoản theo id")
    print(f"   • POST http://localhost:{port}/creat_otp      - Tạo và gửi mã OTP qua email")
    print(f"   • POST http://localhost:{port}/check_login    - Kiểm tra mã OTP để đăng nhập (trả về session token)")
    print(f"   • GET  http://localhost:{port}/dashboard      - Trang dashboard quản lý hệ thống")
    print(f"   • POST http://localhost:{port}/verify_session - Kiểm tra session token có hợp lệ không")
    print(f"   • POST http://localhost:{port}/logout         - Đăng xuất (xóa session)")
    print(f"   • GET  http://localhost:{port}/users           - Lấy danh sách users từ db/data.json")
    print(f"   • GET  http://localhost:{port}/users/search    - Tìm kiếm user theo ID (query: ?id=<user_id>)")
    print(f"   • GET  http://localhost:{port}/config          - Lấy danh sách tất cả config")
    print(f"   • GET  http://localhost:{port}/config/<name>   - Lấy config theo tên file")
    print(f"   • GET  http://localhost:{port}/config/<name>/fields - Lấy danh sách các trường")
    print(f"   • GET  http://localhost:{port}/config/<name>/<field> - Lấy một trường cụ thể")
    print(f"   • PUT  http://localhost:{port}/config/<name>   - Cập nhật toàn bộ config")
    print(f"   • PUT  http://localhost:{port}/config/<name>/<field> - Cập nhật một trường")
    print("="*60)
    print(f"💡 Truy cập từ mạng nội bộ: http://{local_ip}:{port}/qr")
    print(f"💡 API authentication: http://{local_ip}:{port}/authentication")
    print("="*60)


@app.route('/qr', methods=['GET'])
def qr_code_endpoint():
    """
    API endpoint tự động tạo id/token, tạo QR code và trả về ảnh QR
    
    Query Parameters:
        - sl (optional): Số lượng để tính toán số tiền trong QR code
        - format (optional): Định dạng trả về. 'json' để nhận JSON với id và qr_code base64 (mặc định), 'image' để nhận ảnh PNG với id trong header X-QR-ID
    
    Returns:
        - 200: JSON với id và qr_code base64 (mặc định) hoặc Ảnh QR code (image/png) nếu format=image
        - 400: Request không hợp lệ (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        GET /qr                    # Trả về JSON với id và qr_code base64
        GET /qr?sl=50              # Trả về JSON với id và qr_code base64
        GET /qr?format=image       # Trả về ảnh PNG với id trong header X-QR-ID
        GET /qr?sl=50&format=json  # Trả về JSON với id và qr_code base64
    """
    # Lấy tham số sl từ query parameter (nếu có)
    sl_param = request.args.get('sl')
    sl = None
    if sl_param:
        try:
            sl = int(sl_param)
        except ValueError:
            response = jsonify({
                "success": False,
                "status_code": 400,
                "message": f"Tham số 'sl' phải là số nguyên, nhận được: {sl_param}"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, 400
    
    # Lấy tham số format từ query parameter (nếu có, mặc định là 'json' để luôn có ID trong response)
    format_param = request.args.get('format', 'json').lower()
    
    # Gọi hàm xử lý từ module qr_code với tham số sl
    success, result, error_message = qr_code.xu_ly_qr_code(sl=sl)
    
    if not success:
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": error_message
        })
        # Thêm CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500
    
    # Lấy dữ liệu từ kết quả
    id = result['id']
    qr_bytes = result['qr_bytes']
    
    # Nếu format=json, trả về JSON với id và qr_code base64
    if format_param == 'json':
        qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
        response = jsonify({
            "success": True,
            "status_code": 200,
            "id": id,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "sl": sl
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    
    # Trả về ảnh QR code với id trong header
    return Response(
        qr_bytes,
        mimetype='image/png',
        headers={
            'Content-Disposition': f'inline; filename=qr_{id}.png',
            'X-QR-ID': id,  # Thêm id vào header
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Expose-Headers': 'X-QR-ID'  # Cho phép client đọc header này
        }
    )


@app.route('/authentication', methods=['POST'])
def authentication_endpoint():
    """
    API endpoint authentication nhận request từ SePay và xử lý thanh toán
    Không yêu cầu chứng thực/token
    
    Body JSON format:
    {
        "id": 92704,
        "gateway": "Vietcombank",
        "transactionDate": "2023-03-25 14:02:37",
        "accountNumber": "0123499999",
        "code": null,
        "content": "chuyen tien mua iphone",      // id_sl (20 ký tự đầu là id, phần còn lại là sl)
        "transferType": "in",
        "transferAmount": 2277000,                // Số tiền thanh toán
        "accumulated": 19077000,
        "subAccount": null,
        "referenceCode": "MBVCB.3278907687",
        "description": ""
    }
    
    Returns:
        - 200: Request đã được xử lý thành công (JSON)
        - 400: Request không hợp lệ (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        POST /authentication
        Body: {"content": "...", "transferAmount": 2277000, ...}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request từ SePay!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất content và transferAmount từ JSON body
    content = json_data.get('content')
    transfer_amount = json_data.get('transferAmount')
    
    # Kiểm tra các trường bắt buộc
    if content is None:
        print("❌ Thiếu trường 'content' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'content' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    if transfer_amount is None:
        print("❌ Thiếu trường 'transferAmount' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'transferAmount' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # In thông tin trích xuất được
    print(f"\n📤 Trích xuất thông tin:")
    print(f"   • content (gốc): {content}")
    print(f"   • transferAmount: {transfer_amount}")
    
    # Parse content để lấy id_sl (nếu có .CT thì lấy phần trước .CT)
    id_sl = authencation.parse_content(content)
    print(f"   • id_sl (sau parse): {id_sl}")
    
    # Gọi hàm xử lý thanh toán từ module authentication
    print(f"\n🔄 Đang xử lý thanh toán...")
    success, message, data = authencation.xu_ly_thanh_toan(
        id_sl=id_sl,
        pay_ment=transfer_amount
    )
    
    print(f"📊 Kết quả: {message}")
    if data:
        print(f"📋 Dữ liệu: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    print("="*60 + "\n")
    
    # Trả về response
    if success:
        response = jsonify({
            "success": True,
            "status_code": 200,
            "message": message,
            "data": data
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    else:
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": message,
            "data": data
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 500


@app.route('/add_count', methods=['POST'])
def add_count_endpoint():
    """
    API endpoint để tăng count cho tài khoản theo id
    
    Body JSON format:
    {
        "id": "id0c0nUPf3rjZwzpA3yD"  // ID của tài khoản cần tăng count
    }
    
    Returns:
        - 200: Tăng count thành công (JSON)
        - 400: Request không hợp lệ (JSON)
        - 500: Lỗi server hoặc tài khoản bị khoá/hết lượt (JSON)
    
    Example:
        POST /add_count
        Body: {"id": "id0c0nUPf3rjZwzpA3yD"}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request add_count!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất id từ JSON body
    id = json_data.get('id')
    
    # Kiểm tra trường bắt buộc
    if id is None:
        print("❌ Thiếu trường 'id' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'id' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra id có phải là string không
    if not isinstance(id, str):
        print(f"❌ Trường 'id' phải là chuỗi, nhận được: {type(id).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'id' phải là chuỗi, nhận được: {type(id).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # In thông tin trích xuất được
    print(f"\n📤 Trích xuất thông tin:")
    print(f"   • id: {id}")
    
    # Gọi hàm xử lý từ module add_count
    print(f"\n🔄 Đang xử lý tăng count...")
    success, message, data = add_count.add_count(id)
    
    print(f"📊 Kết quả: {message}")
    if data:
        print(f"📋 Dữ liệu: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    print("="*60 + "\n")
    
    # Trả về response
    if success:
        response = jsonify({
            "success": True,
            "status_code": 200,
            "message": message,
            "data": data
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    else:
        # Xác định mã trạng thái HTTP dựa trên error_code
        status_code = 500
        if data and isinstance(data, dict):
            error_code = data.get('error_code')
            if error_code == 'ACCOUNT_LOCKED' or error_code == 'ACCOUNT_LIMIT_EXCEEDED':
                status_code = 400
        
        response = jsonify({
            "success": False,
            "status_code": status_code,
            "message": message,
            "data": data
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, status_code


@app.route('/admin', methods=['GET'])
def admin_endpoint():
    """
    API endpoint để hiển thị giao diện đăng nhập admin
    
    Returns:
        - 200: Trả về file HTML login.html
        - 404: Không tìm thấy file
    """
    try:
        # Đường dẫn đến file login.html
        page_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page')
        login_file = os.path.join(page_dir, 'login.html')
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(login_file):
            response = jsonify({
                "success": False,
                "status_code": 404,
                "message": "Không tìm thấy file login.html"
            })
            return response, 404
        
        # Đọc và trả về nội dung HTML
        with open(login_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return Response(html_content, mimetype='text/html'), 200
    except Exception as e:
        print(f"❌ Lỗi khi đọc file login.html: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        return response, 500


@app.route('/page/<path:filename>')
def serve_page_files(filename):
    """
    Serve static files từ thư mục page (CSS, JS, images, etc.)
    
    Args:
        filename: Tên file hoặc đường dẫn file trong thư mục page
        
    Returns:
        - 200: File được tìm thấy và trả về
        - 404: File không tồn tại
    """
    try:
        page_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page')
        file_path = os.path.join(page_dir, filename)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f"⚠️ File không tồn tại: {filename}")
            response = jsonify({
                "success": False,
                "status_code": 404,
                "message": f"File không tồn tại: {filename}"
            })
            return response, 404
        
        # Xác định MIME type dựa trên extension
        mimetype = None
        if filename.endswith('.css'):
            mimetype = 'text/css'
        elif filename.endswith('.js'):
            mimetype = 'application/javascript'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        
        return send_from_directory(page_dir, filename, mimetype=mimetype)
    except Exception as e:
        print(f"❌ Lỗi khi serve file từ page: {e}")
        response = jsonify({
            "success": False,
            "status_code": 404,
            "message": "File không tồn tại"
        })
        return response, 404


@app.route('/check', methods=['POST'])
def check_endpoint():
    """
    API endpoint để kiểm tra trạng thái tài khoản theo id
    
    Body JSON format:
    {
        "id": "id0c0nUPf3rjZwzpA3yD"  // ID của tài khoản cần kiểm tra
    }
    
    Returns:
        - 200: Thành công - ID tồn tại và active = true
        - 300: Tài khoản bị khóa - ID tồn tại nhưng active = false
        - 404: Không tồn tại - ID không có trong hệ thống
        - 400: Request không hợp lệ
        - 500: Lỗi server
        
    Response body (chỉ chứa):
        {
            "id": "string",
            "count": number,
            "limit": number,
            "message": "string"
        }
    
    Example:
        POST /check
        Body: {"id": "id0c0nUPf3rjZwzpA3yD"}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request check!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất id từ JSON body
    id = json_data.get('id')
    
    # Kiểm tra trường bắt buộc
    if id is None:
        print("❌ Thiếu trường 'id' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'id' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra id có phải là string không
    if not isinstance(id, str):
        print(f"❌ Trường 'id' phải là chuỗi, nhận được: {type(id).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'id' phải là chuỗi, nhận được: {type(id).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # In thông tin trích xuất được
    print(f"\n📤 Trích xuất thông tin:")
    print(f"   • id: {id}")
    
    # Gọi hàm check từ module check
    status_code, data = check.check(id)
    
    # Thêm status_code vào data
    data['status_code'] = status_code
    
    # In kết quả ra console
    print(f"\n📥 Kết quả:")
    print(f"   • status_code: {status_code}")
    if data:
        print(f"   • data: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("="*60 + "\n")
    
    # Trả về response với status code và data (chứa id, count, limit, message, status_code)
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, status_code


@app.route('/creat_otp', methods=['POST'])
def creat_otp_endpoint():
    """
    API endpoint để tạo và gửi mã OTP qua email
    
    Body JSON format:
    {
        "email": "user@example.com"  // Email cần gửi OTP
    }
    
    Returns:
        - 200: Thành công - OTP đã được gửi
        - 400: Request không hợp lệ hoặc email không hợp lệ
        - 500: Lỗi server
    
    Response body:
        {
            "success": bool,
            "status_code": number,
            "message": "string"
        }
    
    Example:
        POST /creat_otp
        Body: {"email": "user@example.com"}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request creat_otp!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất email từ JSON body
    email = json_data.get('email')
    
    # Kiểm tra trường bắt buộc
    if email is None:
        print("❌ Thiếu trường 'email' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'email' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra email có phải là string không
    if not isinstance(email, str):
        print(f"❌ Trường 'email' phải là chuỗi, nhận được: {type(email).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'email' phải là chuỗi, nhận được: {type(email).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # In thông tin trích xuất được
    print(f"\n📤 Trích xuất thông tin:")
    print(f"   • email: {email}")
    
    try:
        # Gọi hàm creat_otp từ module creat_otp
        success, message = creat_otp.creat_otp(email)
        
        # Xác định status code dựa trên kết quả
        if success:
            status_code = 200
            response_data = {
                "success": True,
                "status_code": status_code,
                "message": message
            }
        else:
            # Kiểm tra loại lỗi để xác định status code phù hợp
            if "không hợp lệ" in message.lower() or "mail không đúng" in message.lower():
                status_code = 400
            else:
                status_code = 500
            response_data = {
                "success": False,
                "status_code": status_code,
                "message": message
            }
        
        # In kết quả ra console
        print(f"\n📥 Kết quả:")
        print(f"   • success: {success}")
        print(f"   • status_code: {status_code}")
        print(f"   • message: {message}")
        print("="*60 + "\n")
        
        # Trả về response
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý creat_otp: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 500


@app.route('/check_login', methods=['POST'])
def check_login_endpoint():
    """
    API endpoint để kiểm tra mã OTP và đăng nhập
    
    Body JSON format:
    {
        "email": "user@example.com",  // Email của người dùng
        "otp_code": "123456"           // Mã OTP nhận được
    }
    
    Returns:
        - 200: Thành công - Đăng nhập thành công
        - 400: Request không hợp lệ hoặc mã OTP không đúng
        - 500: Lỗi server
    
    Response body:
        {
            "success": bool,
            "status_code": number,
            "message": "string"
        }
    
    Example:
        POST /check_login
        Body: {"email": "user@example.com", "otp_code": "123456"}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request check_login!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất email và otp_code từ JSON body
    email = json_data.get('email')
    otp_code = json_data.get('otp_code')
    
    # Kiểm tra trường bắt buộc
    if email is None:
        print("❌ Thiếu trường 'email' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'email' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    if otp_code is None:
        print("❌ Thiếu trường 'otp_code' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'otp_code' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra email và otp_code có phải là string không
    if not isinstance(email, str):
        print(f"❌ Trường 'email' phải là chuỗi, nhận được: {type(email).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'email' phải là chuỗi, nhận được: {type(email).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    if not isinstance(otp_code, str):
        print(f"❌ Trường 'otp_code' phải là chuỗi, nhận được: {type(otp_code).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'otp_code' phải là chuỗi, nhận được: {type(otp_code).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # In thông tin trích xuất được
    print(f"\n📤 Trích xuất thông tin:")
    print(f"   • email: {email}")
    print(f"   • otp_code: {otp_code}")
    
    try:
        # Gọi hàm check_login từ module check_login
        success, message = check_login.check_login(email, otp_code)
        
        # Xác định status code dựa trên kết quả
        if success:
            status_code = 200
        else:
            # Kiểm tra loại lỗi để xác định status code phù hợp
            if "không hợp lệ" in message.lower() or "không đúng" in message.lower():
                status_code = 400
            else:
                status_code = 500
        
        response_data = {
            "success": success,
            "status_code": status_code,
            "message": message
        }
        
        # In kết quả ra console
        print(f"\n📥 Kết quả:")
        print(f"   • success: {success}")
        print(f"   • status_code: {status_code}")
        print(f"   • message: {message}")
        print("="*60 + "\n")
        
        # Nếu login thành công, tạo session và trả về token (chỉ JSON, không trả về HTML)
        if success:
            # Tạo session token với thời hạn 2 ngày
            session_token = session_manager.create_session(email)
            
            if session_token:
                # Thêm token vào response data
                response_data["session_token"] = session_token
                response_data["email"] = email.strip().lower()
                print(f"✅ Đã tạo session token cho email: {email}")
            else:
                print(f"⚠️ Không thể tạo session token cho email: {email}")
        
        # Trả về JSON response (cả thành công và thất bại)
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý check_login: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 500


@app.route('/verify_session', methods=['POST'])
def verify_session_endpoint():
    """
    API endpoint để kiểm tra session token có hợp lệ không
    
    Body JSON format:
    {
        "session_token": "token_string"  // Session token cần kiểm tra
    }
    
    Returns:
        - 200: Thành công - Session hợp lệ
        - 400: Request không hợp lệ hoặc token không hợp lệ
        - 401: Session đã hết hạn
        - 500: Lỗi server
    
    Response body:
        {
            "success": bool,
            "status_code": number,
            "message": "string",
            "email": "string" (nếu hợp lệ)
        }
    
    Example:
        POST /verify_session
        Body: {"session_token": "abc123..."}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request verify_session!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất session_token từ JSON body
    session_token = json_data.get('session_token')
    
    # Kiểm tra trường bắt buộc
    if session_token is None:
        print("❌ Thiếu trường 'session_token' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'session_token' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra session_token có phải là string không
    if not isinstance(session_token, str):
        print(f"❌ Trường 'session_token' phải là chuỗi, nhận được: {type(session_token).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'session_token' phải là chuỗi, nhận được: {type(session_token).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    try:
        # Gọi hàm verify_session từ module session_manager
        is_valid, email, message = session_manager.verify_session(session_token)
        
        # Xác định status code dựa trên kết quả
        if is_valid:
            status_code = 200
            response_data = {
                "success": True,
                "status_code": status_code,
                "message": message,
                "email": email
            }
        else:
            # Kiểm tra loại lỗi để xác định status code phù hợp
            if "hết hạn" in message.lower():
                status_code = 401
            elif "không hợp lệ" in message.lower() or "không được để trống" in message.lower():
                status_code = 400
            else:
                status_code = 500
            
            response_data = {
                "success": False,
                "status_code": status_code,
                "message": message
            }
        
        # In kết quả ra console
        print(f"\n📥 Kết quả:")
        print(f"   • success: {is_valid}")
        print(f"   • status_code: {status_code}")
        print(f"   • message: {message}")
        if email:
            print(f"   • email: {email}")
        print("="*60 + "\n")
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý verify_session: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 500


@app.route('/logout', methods=['POST'])
def logout_endpoint():
    """
    API endpoint để đăng xuất (xóa session)
    
    Body JSON format:
    {
        "session_token": "token_string"  // Session token cần xóa
    }
    
    Returns:
        - 200: Thành công - Đã xóa session
        - 400: Request không hợp lệ
        - 500: Lỗi server
    
    Response body:
        {
            "success": bool,
            "status_code": number,
            "message": "string"
        }
    
    Example:
        POST /logout
        Body: {"session_token": "abc123..."}
    """
    # Lấy JSON body từ request
    json_data = request.get_json(silent=True)
    
    # Print nội dung request ra console
    print("\n" + "="*60)
    print("✅ Nhận được request logout!")
    print("="*60)
    print(f"📋 Method: {request.method}")
    print(f"📋 URL: {request.url}")
    
    if json_data:
        print(f"📋 JSON Body:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    
    # Kiểm tra JSON body có tồn tại không
    if not json_data:
        print("❌ Không có JSON body trong request")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Request phải chứa JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Trích xuất session_token từ JSON body
    session_token = json_data.get('session_token')
    
    # Kiểm tra trường bắt buộc
    if session_token is None:
        print("❌ Thiếu trường 'session_token' trong JSON body")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": "Thiếu trường 'session_token' trong JSON body"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    # Kiểm tra session_token có phải là string không
    if not isinstance(session_token, str):
        print(f"❌ Trường 'session_token' phải là chuỗi, nhận được: {type(session_token).__name__}")
        response = jsonify({
            "success": False,
            "status_code": 400,
            "message": f"Trường 'session_token' phải là chuỗi, nhận được: {type(session_token).__name__}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 400
    
    try:
        # Gọi hàm delete_session từ module session_manager
        success = session_manager.delete_session(session_token)
        
        if success:
            status_code = 200
            message = "Đã đăng xuất thành công"
        else:
            status_code = 400
            message = "Session không tồn tại hoặc đã bị xóa"
        
        # In kết quả ra console
        print(f"\n📥 Kết quả:")
        print(f"   • success: {success}")
        print(f"   • status_code: {status_code}")
        print(f"   • message: {message}")
        print("="*60 + "\n")
        
        response_data = {
            "success": success,
            "status_code": status_code,
            "message": message
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý logout: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 500


@app.route('/dashboard', methods=['GET'])
def dashboard_endpoint():
    """
    API endpoint để trả về trang dashboard HTML
    Kiểm tra session token từ query parameter hoặc từ localStorage (client-side)
    
    Query parameters:
        - token (optional): Session token để inject vào HTML
    
    Returns:
        - 200: Thành công - HTML dashboard
        - 500: Lỗi server
    
    Example:
        GET /dashboard
        GET /dashboard?token=abc123...
    """
    try:
        # Lấy token từ query parameter (nếu có)
        token = request.args.get('token')
        
        # Đường dẫn đến file dashboad.html
        page_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page')
        dashboard_file = os.path.join(page_dir, 'dashboad.html')
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(dashboard_file):
            print(f"❌ Không tìm thấy file dashboard: {dashboard_file}")
            response = jsonify({
                "success": False,
                "status_code": 500,
                "message": "Không tìm thấy file dashboard"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        # Đọc và trả về nội dung HTML
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Đọc URL từ api.txt và thay thế localhost trong HTML
        try:
            api_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api.txt')
            if os.path.exists(api_txt_path):
                with open(api_txt_path, 'r', encoding='utf-8') as api_file:
                    api_url = api_file.read().strip()
                    if api_url:
                        # Loại bỏ dấu / ở cuối nếu có
                        api_url = api_url.rstrip('/')
                        # Thay thế localhost:5000 bằng URL từ api.txt
                        html_content = html_content.replace('http://localhost:5000', api_url)
                        html_content = html_content.replace("const BASE_URL = 'http://localhost:5000';", f"const BASE_URL = '{api_url}';")
                        print(f"✅ Đã inject URL từ api.txt: {api_url}")
                    else:
                        print("⚠️ File api.txt rỗng, sử dụng localhost")
            else:
                print("⚠️ Không tìm thấy file api.txt, sử dụng localhost")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc api.txt: {e}, sử dụng localhost")
        
        # Nếu có token từ query parameter, inject vào localStorage
        if token:
            script_inject = f"""
            <script>
                // Lưu session token vào localStorage khi trang load
                if (typeof(Storage) !== 'undefined') {{
                    localStorage.setItem('session_token', '{token}');
                    console.log('✅ Đã lưu session token vào localStorage từ URL');
                }}
            </script>
            """
            # Chèn script vào trước thẻ </head> hoặc </body>
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', script_inject + '</head>')
            elif '</body>' in html_content:
                html_content = html_content.replace('</body>', script_inject + '</body>')
            else:
                # Nếu không tìm thấy, chèn vào đầu body
                html_content = html_content.replace('<body>', '<body>' + script_inject)
            print(f"✅ Đã inject session token vào HTML")
        
        print(f"✅ Đã đọc file dashboard thành công")
        response = Response(html_content, mimetype='text/html', status=200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý dashboard: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/api_url', methods=['GET'])
def api_url_endpoint():
    """
    API endpoint trả về URL từ file api.txt
    
    Returns:
        - 200: Thành công - URL từ api.txt (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        GET /api_url
    """
    try:
        api_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api.txt')
        if os.path.exists(api_txt_path):
            with open(api_txt_path, 'r', encoding='utf-8') as api_file:
                api_url = api_file.read().strip()
                if api_url:
                    # Loại bỏ dấu / ở cuối nếu có
                    api_url = api_url.rstrip('/')
                    response = jsonify({
                        "success": True,
                        "status_code": 200,
                        "url": api_url
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    response.headers.add('Access-Control-Allow-Methods', 'GET')
                    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                    return response, 200
                else:
                    # Nếu file rỗng, trả về localhost
                    response = jsonify({
                        "success": True,
                        "status_code": 200,
                        "url": "http://localhost:5000"
                    })
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    response.headers.add('Access-Control-Allow-Methods', 'GET')
                    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                    return response, 200
        else:
            # Nếu không tìm thấy file, trả về localhost
            response = jsonify({
                "success": True,
                "status_code": 200,
                "url": "http://localhost:5000"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, 200
    except Exception as e:
        print(f"❌ Lỗi khi đọc api.txt: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}",
            "url": "http://localhost:5000"  # Fallback về localhost
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500


@app.route('/users', methods=['GET', 'POST'])
def users_endpoint():
    """
    API endpoint để lấy danh sách users hoặc tạo user mới
    
    GET: Lấy danh sách users từ db/data.json
    POST: Tạo user mới
    
    Body JSON (POST):
    {
        "limit": 100,
        "active": true
    }
    
    Returns:
        GET:
        - 200: Thành công - Danh sách users (JSON)
        - 500: Lỗi server (JSON)
        
        POST:
        - 201: Thành công - User đã được tạo (JSON)
        - 400: Request không hợp lệ (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        GET /users
        POST /users
        Body: {"limit": 100, "active": true}
    """
    try:
        if request.method == 'GET':
            success, data, status_code, message = user_api.handle_get_users()
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data.get("users", [])
                response_data["count"] = data.get("count", 0)
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
        
        elif request.method == 'POST':
            # Lấy dữ liệu từ request body
            if not request.is_json:
                response = jsonify({
                    "success": False,
                    "status_code": 400,
                    "message": "Request body phải là JSON"
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                return response, 400
            
            json_data = request.get_json()
            limit = json_data.get('limit')
            active = json_data.get('active', True)  # Mặc định là True
            
            success, data, status_code, message = user_api.handle_create_user(limit, active)
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý users: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}",
            "data": [] if request.method == 'GET' else None
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500


@app.route('/users', methods=['OPTIONS'])
def users_options_endpoint():
    """Handle CORS preflight requests for /users"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response, 200


@app.route('/users/search', methods=['GET'])
def users_search_endpoint():
    """
    API endpoint để tìm kiếm user theo ID (có thể là một phần của ID)
    
    Query parameters:
        - id: ID hoặc một phần ID của user cần tìm
    
    Returns:
        - 200: Thành công - User(s) tìm thấy (JSON)
        - 400: Request không hợp lệ (JSON)
        - 404: Không tìm thấy user (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        GET /users/search?id=hxPyj6t9OYSnpmL20ixm
        GET /users/search?id=hxPyj6t9
    """
    try:
        # Lấy query parameter id
        user_id = request.args.get('id')
        
        if not user_id:
            response = jsonify({
                "success": False,
                "status_code": 400,
                "message": "Thiếu query parameter 'id'"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, 400
        
        success, data, status_code, message = user_api.handle_search_user(user_id)
        
        response_data = {
            "success": success,
            "status_code": status_code,
            "message": message
        }
        
        if data:
            # Nếu có trường "user" (1 user), thêm vào data
            if "user" in data:
                response_data["data"] = [data["user"]]
                response_data["count"] = 1
            # Nếu có trường "users" (nhiều users), thêm vào data
            elif "users" in data:
                response_data["data"] = data["users"]
                response_data["count"] = data["count"]
            else:
                response_data["data"] = []
                response_data["count"] = 0
        else:
            response_data["data"] = []
            response_data["count"] = 0
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm kiếm user: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}",
            "data": []
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500


@app.route('/users/<user_id>', methods=['DELETE', 'PUT'])
def user_manage_endpoint(user_id):
    """
    API endpoint để xóa hoặc cập nhật user
    
    DELETE: Xóa user theo ID
    PUT: Cập nhật user theo ID
    
    Body JSON (PUT):
    {
        "limit": 100,
        "active": true,
        "count": 5
    }
    
    Returns:
        - 200: Thành công (JSON)
        - 400: Request không hợp lệ (JSON)
        - 404: User không tồn tại (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        DELETE /users/hxPyj6t9OYSnpmL20ixm
        PUT /users/hxPyj6t9OYSnpmL20ixm
        Body: {"limit": 200, "active": false}
    """
    try:
        if request.method == 'DELETE':
            success, data, status_code, message = user_api.handle_delete_user(user_id)
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
        
        elif request.method == 'PUT':
            # Lấy dữ liệu từ request body
            if not request.is_json:
                response = jsonify({
                    "success": False,
                    "status_code": 400,
                    "message": "Request body phải là JSON"
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                return response, 400
            
            fields_dict = request.get_json()
            
            success, data, status_code, message = user_api.handle_update_user(user_id, fields_dict)
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý user: {e}")
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500


@app.route('/users/<user_id>', methods=['OPTIONS'])
def user_options_endpoint(user_id):
    """Handle CORS preflight requests"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, DELETE, PUT, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response, 200


@app.route('/config/pay_ment', methods=['GET', 'PUT'])
def config_pay_ment_endpoint():
    """
    API endpoint quản lý config pay_ment.json
    
    GET: Lấy toàn bộ config của pay_ment.json
    PUT: Cập nhật toàn bộ config của pay_ment.json
    
    Body JSON (PUT):
    {
        "config": {
            "BNK": "value1",
            "STK": "value2",
            "UN": "value3",
            "COST": "value4",
            "LIMIT": 0
        }
    }
    
    Returns:
        - 200: Thành công (JSON)
        - 400: Request không hợp lệ (JSON)
        - 404: File không tồn tại (JSON)
        - 500: Lỗi server (JSON)
    
    Example:
        GET /config/pay_ment
        PUT /config/pay_ment
        Body: {"config": {"BNK": "VCB", "STK": "123456", "UN": "user", "COST": "1000", "LIMIT": 100}}
    """
    try:
        file_name = 'pay_ment'
        
        if request.method == 'GET':
            success, data, status_code, message = config_api.handle_get_config(file_name)
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
        
        elif request.method == 'PUT':
            json_data = request.get_json(silent=True)
            
            if not json_data:
                response = jsonify({
                    "success": False,
                    "status_code": 400,
                    "message": "Request phải chứa JSON body"
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                return response, 400
            
            # Nếu có trường "config" thì dùng nó, nếu không thì dùng toàn bộ body
            config_dict = json_data.get('config', json_data)
            
            success, data, status_code, message = config_api.handle_set_config(file_name, config_dict)
            
            response_data = {
                "success": success,
                "status_code": status_code,
                "message": message
            }
            if data:
                response_data["data"] = data
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, status_code
            
    except Exception as e:
        response = jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Lỗi server: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 500


def main():
    """
    Main function để khởi động Flask API service
    """
    port = 5000
    local_ip = lay_ip_local()
    
    # In thông tin API
    in_thong_tin_api(port, local_ip)
    
    print("\n🚀 Đang khởi động Flask server...")
    print("="*60)
    
    try:
        # Chạy Flask app trên 0.0.0.0 để có thể truy cập từ mạng nội bộ
        # debug=True: hiển thị error messages đẹp và bật chế độ debug
        # use_reloader=True: tự động reload khi code thay đổi (chế độ debug)
        # threaded=True: cho phép xử lý nhiều requests đồng thời
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng server...")
        print("✅ Đã dừng server")
    except Exception as e:
        print(f"\n❌ Lỗi khi chạy server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
