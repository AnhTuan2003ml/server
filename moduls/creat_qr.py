import json
import requests


def doc_config(config_file="config/pay_ment.json"):
    """
    Đọc thông tin từ file config (định dạng JSON)
    
    Args:
        config_file: Đường dẫn đến file config
        
    Returns:
        dict: Dictionary chứa thông tin từ config
    """
    config_data = {}
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file config: {config_file}")
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi parse JSON config: {e}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file config: {e}")
    
    return config_data


def tao_add_info(id, token):
    """
    Tạo nội dung add_info từ id và token cho QR code
    
    Args:
        id: ID của đơn hàng
        token: Token xác thực
        
    Returns:
        str: Nội dung add_info dạng id-token
    """
    add_info = f"{id}-{token}"
    return add_info


def xu_ly_amount(cost_str):
    """
    Xử lý chuỗi số tiền từ config (loại bỏ dấu chấm và khoảng trắng)
    
    Args:
        cost_str: Chuỗi số tiền từ config (ví dụ: "200.000")
        
    Returns:
        int: Số tiền dạng số nguyên
    """
    # Loại bỏ dấu chấm phân cách hàng nghìn và khoảng trắng
    cost_str = cost_str.replace(".", "").replace(" ", "")
    amount = int(cost_str) if cost_str.isdigit() else 0
    return amount


def tao_qr_code(id, token, config_file="config/pay_ment.json", output_file="qr_vietqr.png"):
    """
    Tải QR code thanh toán VietQR từ API VietQR.io
    
    Args:
        id: ID của đơn hàng
        token: Token xác thực
        config_file: Đường dẫn đến file config
        output_file: Tên file QR code đầu ra
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    # Đọc thông tin từ config
    config_data = doc_config(config_file)
    
    # Kiểm tra config có đầy đủ không
    if not config_data:
        print("❌ Không đọc được thông tin từ config")
        return False
    
    # Lấy thông tin từ config
    bank_code = config_data.get("BNK", "").upper()  # Chuyển thành chữ hoa
    account_no = config_data.get("STK", "")
    account_name = config_data.get("UN", "")
    cost_str = config_data.get("COST", "0")
    
    # Kiểm tra thông tin có đầy đủ không
    if not all([bank_code, account_no, account_name]):
        print("❌ Thiếu thông tin trong config (BNK, STK, hoặc UN)")
        return False
    
    # Kiểm tra id và token
    if not id or not token:
        print("❌ Thiếu id hoặc token")
        return False
    
    # Xử lý số tiền
    amount = xu_ly_amount(cost_str)
    
    # Tạo add_info từ id và token
    add_info = tao_add_info(id, token)
    
    # Tạo link chuẩn VietQR
    url = f"https://img.vietqr.io/image/{bank_code}-{account_no}-compact.png?amount={amount}&addInfo={add_info}&accountName={account_name}"
    
    try:
        # Tải ảnh QR từ VietQR.io
        response = requests.get(url)
        
        if response.status_code == 200:
            # Lưu ảnh vào file
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            # In thông tin
            print("✅ QR thanh toán VietQR đã được tải:", output_file)
            print(f"📋 Thông tin: {bank_code} - {account_no} - {account_name} - {amount:,}đ")
            print(f"📝 Nội dung: {add_info}")
            
            return True
        else:
            print(f"❌ Không tải được QR từ VietQR.io (Status code: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi tải QR code: {e}")
        return False


if __name__ == "__main__":
    # Chạy hàm chính khi file được gọi trực tiếp
    tao_qr_code(id="0093650001", token="8204b2ba8867f52ac8c1f15a2ca11117ce038719bf37ff5e5bccb6013651a6cb")
    print("⚠️ Hàm tao_qr_code() yêu cầu id và token làm tham số")
    print("📝 Ví dụ: tao_qr_code(id='12345', token='abc123def456')")
