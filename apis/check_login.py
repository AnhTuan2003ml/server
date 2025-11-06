"""
Module kiểm tra mã OTP để đăng nhập
"""
import json
import os


def doc_otp_tu_file(email, otp_file="db/otp.txt"):
    """
    Đọc mã OTP từ file txt
    
    Args:
        email: Email của người dùng
        otp_file: Đường dẫn file chứa OTP
        
    Returns:
        str: Mã OTP nếu tìm thấy, None nếu không tìm thấy hoặc có lỗi
    """
    try:
        # Lấy đường dẫn tuyệt đối của file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        otp_path = os.path.join(base_dir, otp_file)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(otp_path):
            return None
        
        # Đọc file
        with open(otp_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return None
            
            otp_data = json.loads(content)
            
            # Tìm OTP theo email (chuyển về lowercase để so sánh)
            email_lower = email.strip().lower()
            if email_lower in otp_data:
                return otp_data[email_lower].get("otp")
            
            return None
            
    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"Lỗi khi đọc OTP từ file: {e}")
        return None


def xoa_otp_sau_khi_dung(email, otp_file="db/otp.txt"):
    """
    Xóa mã OTP sau khi đã sử dụng thành công
    
    Args:
        email: Email của người dùng
        otp_file: Đường dẫn file chứa OTP
        
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi
    """
    try:
        # Lấy đường dẫn tuyệt đối của file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        otp_path = os.path.join(base_dir, otp_file)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(otp_path):
            return True  # Không có gì để xóa
        
        # Đọc file
        with open(otp_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return True
            
            otp_data = json.loads(content)
            
            # Xóa OTP của email này
            email_lower = email.strip().lower()
            if email_lower in otp_data:
                del otp_data[email_lower]
            
            # Ghi lại file
            with open(otp_path, 'w', encoding='utf-8') as f:
                json.dump(otp_data, f, ensure_ascii=False, indent=2)
            
            return True
            
    except Exception as e:
        print(f"Lỗi khi xóa OTP: {e}")
        return False


def check_login(email, otp_code):
    """
    Kiểm tra mã OTP để đăng nhập
    
    Args:
        email: Email của người dùng
        otp_code: Mã OTP nhận được từ người dùng
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Kiểm tra đầu vào
        if not email or not isinstance(email, str):
            return False, "Email không hợp lệ"
        
        if not otp_code or not isinstance(otp_code, str):
            return False, "Mã OTP không hợp lệ"
        
        # Chuẩn hóa email và OTP
        email = email.strip().lower()
        otp_code = otp_code.strip()
        
        # Đọc OTP từ file
        stored_otp = doc_otp_tu_file(email)
        
        if stored_otp is None:
            return False, "Không tìm thấy mã OTP. Vui lòng yêu cầu mã mới."
        
        # So sánh OTP
        if stored_otp == otp_code:
            # Xóa OTP sau khi sử dụng thành công
            xoa_otp_sau_khi_dung(email)
            return True, "Đăng nhập thành công"
        else:
            return False, "Mã OTP không đúng"
            
    except Exception as e:
        print(f"Lỗi trong check_login: {e}")
        return False, "Lỗi khi kiểm tra đăng nhập"

