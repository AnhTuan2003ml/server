"""
Module tạo và gửi mã OTP qua email
"""
import json
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def doc_config_mail(config_file="config/mail.json"):
    """
    Đọc thông tin email từ file config
    """
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config_file)
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        print(f"Lỗi khi đọc config mail: {e}")
        return {}


def tao_ma_otp(length=6):
    """
    Tạo mã OTP ngẫu nhiên
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def gui_email_otp(sender, password, receiver, otp_code):
    """
    Gửi email chứa mã OTP
    """
    try:
        # Tạo message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Mã OTP xác thực"
        
        # Nội dung email
        body = f"""
        <html>
        <body>
            <h2>Mã OTP xác thực của bạn</h2>
            <p>Mã OTP của bạn là: <strong style="font-size: 24px; color: #0066cc;">{otp_code}</strong></p>
            <p>Mã này có hiệu lực trong thời gian ngắn. Vui lòng không chia sẻ mã này với ai.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Đây là email tự động, vui lòng không trả lời.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # Kết nối SMTP server (Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        
        # Gửi email
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "lỗi"
    except smtplib.SMTPException as e:
        return False, "lỗi"
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False, "lỗi"


def kiem_tra_email(email):
    """
    Kiểm tra định dạng email có hợp lệ không
    """
    if not email or not isinstance(email, str):
        return False
    
    # Kiểm tra cơ bản định dạng email
    if '@' not in email or '.' not in email.split('@')[1]:
        return False
    
    # Kiểm tra độ dài
    if len(email) < 5 or len(email) > 254:
        return False
    
    return True


def luu_otp_vao_file(email, otp_code, otp_file="db/otp.txt"):
    """
    Lưu mã OTP vào file txt
    
    Args:
        email: Email của người dùng
        otp_code: Mã OTP cần lưu
        otp_file: Đường dẫn file để lưu OTP
        
    Returns:
        bool: True nếu lưu thành công, False nếu có lỗi
    """
    try:
        # Lấy đường dẫn tuyệt đối của file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        otp_path = os.path.join(base_dir, otp_file)
        
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(otp_path), exist_ok=True)
        
        # Đọc dữ liệu hiện có (nếu có)
        otp_data = {}
        if os.path.exists(otp_path):
            try:
                with open(otp_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        otp_data = json.loads(content)
            except (json.JSONDecodeError, Exception):
                # Nếu file không hợp lệ, tạo mới
                otp_data = {}
        
        # Lưu OTP với timestamp
        otp_data[email.lower()] = {
            "otp": otp_code,
            "timestamp": datetime.now().isoformat()
        }
        
        # Ghi vào file
        with open(otp_path, 'w', encoding='utf-8') as f:
            json.dump(otp_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Lỗi khi lưu OTP vào file: {e}")
        return False


def creat_otp(email):
    """
    Hàm chính tạo và gửi OTP
    
    Args:
        email: Email cần gửi OTP
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Kiểm tra email có hợp lệ không
        if not kiem_tra_email(email):
            return False, "không hợp lệ"
        
        # Đọc config mail
        mail_config = doc_config_mail()
        if not mail_config:
            return False, "lỗi"
        
        # Lấy thông tin từ config
        receiver = mail_config.get("receiver", "").strip().lower()
        sender = mail_config.get("sender", "").strip()
        password = mail_config.get("password", "").strip()
        
        # Kiểm tra email đầu vào có khớp với receiver không
        email_input = email.strip().lower()
        if email_input != receiver:
            return False, "mail không đúng"
        
        # Kiểm tra có đủ thông tin để gửi email không
        if not sender or not password or not receiver:
            return False, "lỗi"
        
        # Tạo mã OTP
        otp_code = tao_ma_otp(6)
        
        # Lưu OTP vào file txt
        if not luu_otp_vao_file(email_input, otp_code):
            return False, "lỗi khi lưu OTP"
        
        # Gửi email
        success, error_msg = gui_email_otp(sender, password, receiver, otp_code)
        
        if success:
            return True, f"Đã gửi mã OTP đến {receiver}"
        else:
            return False, error_msg
            
    except Exception as e:
        print(f"Lỗi trong creat_otp: {e}")
        return False, "lỗi"

