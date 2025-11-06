"""
Module xử lý QR Code
Tự động tạo ID (20 ký tự ngẫu nhiên) và tạo QR code thanh toán VietQR
"""
import json
import random
import requests
from urllib.parse import quote


def doc_config(config_file="config/pay_ment.json"):
    """
    Đọc thông tin từ file config (định dạng JSON)
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


def doc_data_json(db_file="db/data.json"):
    """Đọc dữ liệu từ file data.json"""
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"❌ Lỗi khi đọc file data.json: {e}")
        return []


def luu_data_json(data, db_file="db/data.json"):
    """Lưu dữ liệu vào file data.json"""
    try:
        with open(db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lưu file data.json: {e}")
        return False


def tao_id():
    """
    Tự động tạo ID ngẫu nhiên (20 ký tự)
    
    Returns:
        str: ID ngẫu nhiên 20 ký tự
    """
    # Tạo ID ngẫu nhiên 20 ký tự (chữ và số)
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = ''.join(random.choice(characters) for _ in range(20))
    
    return id


def xu_ly_amount(cost_str, sl=None, limit=None):
    """
    Xử lý chuỗi số tiền từ config (loại bỏ dấu chấm và khoảng trắng)
    
    Args:
        cost_str: Chuỗi số tiền từ config
        sl: Số lượng (nếu có)
        limit: Giới hạn ban đầu (mặc định 100)
    
    Returns:
        int: Số tiền đã xử lý
    """
    cost_str = cost_str.replace(".", "").replace(" ", "")
    base_amount = int(cost_str) if cost_str.isdigit() else 0
    
    # Nếu có số lượng, tính amount = cost_str * (sl/limit)
    if sl is not None and limit is not None and limit > 0:
        amount = int(base_amount * (sl / limit))
    else:
        amount = base_amount
    
    return amount


def tao_qr_code_bytes(id, config_file="config/pay_ment.json", sl=None, limit=None):
    """
    Tải QR code thanh toán VietQR từ API VietQR.io và trả về bytes
    
    Args:
        id: ID của đơn hàng (20 ký tự ngẫu nhiên)
        config_file: Đường dẫn đến file config
        sl: Số lượng (nếu có)
        limit: Giới hạn ban đầu (mặc định 100)
        
    Returns:
        tuple: (success, qr_bytes, error_message)
    """
    # Đọc thông tin từ config
    config_data = doc_config(config_file)
    
    # Kiểm tra config có đầy đủ không
    if not config_data:
        return False, None, "Không đọc được thông tin từ config"
    
    # Lấy thông tin từ config
    bank_code = config_data.get("BNK", "").upper()
    account_no = config_data.get("STK", "")
    account_name = config_data.get("UN", "")
    cost_str = config_data.get("COST", "0")
    
    # Kiểm tra thông tin có đầy đủ không
    if not all([bank_code, account_no, account_name]):
        return False, None, "Thiếu thông tin trong config (BNK, STK, hoặc UN)"
    
    # Kiểm tra id
    if not id:
        return False, None, "Thiếu id"
    
    # Xử lý số tiền: amount = cost_str * (sl/limit) nếu có sl và limit
    amount = xu_ly_amount(cost_str, sl=sl, limit=limit)
    
    # Tạo add_info từ id và sl (chỉ thêm sl nếu không phải None)
    if sl is not None:  
        add_info = f"AUTO{id}-{sl}END"
    else:
        add_info = f"AUTO{id}END"
    
    # URL encode add_info để đảm bảo ký tự đặc biệt không bị bỏ đi (giữ nguyên ký tự -)
    add_info_encoded = quote(add_info, safe='-')
    
    # Tạo link chuẩn VietQR
    url = f"https://img.vietqr.io/image/{bank_code}-{account_no}-compact.png?amount={amount}&addInfo={add_info_encoded}&accountName={account_name}"
    
    try:
        # Tải ảnh QR từ VietQR.io
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return True, response.content, None
        else:
            return False, None, f"Không tải được QR từ VietQR.io (Status code: {response.status_code})"
            
    except Exception as e:
        return False, None, f"Lỗi khi tải QR code: {e}"


def xu_ly_qr_code(sl=None):
    """
    Xử lý tạo QR code tự động:
    1. Tạo ID ngẫu nhiên (20 ký tự)
    2. Tạo QR code từ VietQR.io
    3. Trả về QR code bytes
    
    Args:
        sl: Số lượng (nếu có). Khi có sl:
            - amount = cost_str * (sl/limit) với limit mặc định là 100
    
    Returns:
        tuple: (success, result_dict, error_message)
        result_dict: {
            'id': str,
            'qr_bytes': bytes
        }
    """
    try:
        # Tạo ID ngẫu nhiên (20 ký tự)
        id = tao_id()
        
        # Giới hạn ban đầu để tính toán amount (mặc định 100)
        limit_for_calculation = 100
        
        # Tạo QR code với sl và limit để tính toán amount
        success, qr_bytes, error_message = tao_qr_code_bytes(id, sl=sl, limit=limit_for_calculation)
        
        if not success:
            return False, None, error_message
        
        # Trả về kết quả
        result = {
            'id': id,
            'qr_bytes': qr_bytes
        }
        
        # Tính toán add_info để hiển thị
        add_info_display = f"{id}-{sl}" if sl is not None else f"{id}"
        
        print(f"✅ Đã tạo QR code thành công!")
        print(f"   ID: {id}")
        if sl is not None:
            print(f"   Số lượng (sl): {sl}")
        print(f"   Nội dung chuyển tiền (addInfo): {add_info_display}")
        
        return True, result, None
        
    except Exception as e:
        return False, None, f"Lỗi khi xử lý QR code: {e}"

