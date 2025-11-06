"""
Module quản lý session đăng nhập
Quản lý session với thời hạn 2 ngày
"""
import json
import os
import secrets
import time
from datetime import datetime, timedelta


# Thời hạn session: 2 ngày (tính bằng giây)
SESSION_DURATION = 2 * 24 * 60 * 60  # 2 ngày = 172800 giây

# Đường dẫn file lưu session
SESSION_FILE = "db/sessions.json"


def get_session_file_path():
    """
    Lấy đường dẫn tuyệt đối của file session
    
    Returns:
        str: Đường dẫn tuyệt đối đến file sessions.json
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, SESSION_FILE)


def load_sessions():
    """
    Đọc tất cả sessions từ file
    
    Returns:
        dict: Dictionary chứa tất cả sessions, key là token, value là session info
    """
    try:
        session_path = get_session_file_path()
        
        # Tạo thư mục db nếu chưa tồn tại
        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(session_path):
            return {}
        
        # Đọc file
        with open(session_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Lỗi khi đọc sessions: {e}")
        return {}


def save_sessions(sessions):
    """
    Lưu sessions vào file
    
    Args:
        sessions: Dictionary chứa tất cả sessions
    """
    try:
        session_path = get_session_file_path()
        
        # Tạo thư mục db nếu chưa tồn tại
        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        
        # Ghi file
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi khi lưu sessions: {e}")


def create_session(email):
    """
    Tạo session mới cho email
    
    Args:
        email: Email của người dùng
    
    Returns:
        str: Session token
    """
    try:
        # Tạo token ngẫu nhiên
        token = secrets.token_urlsafe(32)
        
        # Thời gian hiện tại và thời gian hết hạn
        current_time = time.time()
        expires_at = current_time + SESSION_DURATION
        
        # Tạo session info
        session_info = {
            "email": email.strip().lower(),
            "created_at": current_time,
            "expires_at": expires_at
        }
        
        # Load sessions hiện tại
        sessions = load_sessions()
        
        # Thêm session mới
        sessions[token] = session_info
        
        # Xóa các session hết hạn trước khi lưu
        clean_expired_sessions(sessions)
        
        # Lưu lại
        save_sessions(sessions)
        
        print(f"✅ Đã tạo session cho email: {email}")
        return token
        
    except Exception as e:
        print(f"Lỗi khi tạo session: {e}")
        return None


def verify_session(token):
    """
    Kiểm tra session token có hợp lệ không
    
    Args:
        token: Session token cần kiểm tra
    
    Returns:
        tuple: (is_valid: bool, email: str or None, message: str)
    """
    try:
        if not token:
            return False, None, "Token không được để trống"
        
        # Load sessions
        sessions = load_sessions()
        
        # Kiểm tra token có tồn tại không
        if token not in sessions:
            return False, None, "Token không hợp lệ"
        
        session_info = sessions[token]
        
        # Kiểm tra thời gian hết hạn
        current_time = time.time()
        expires_at = session_info.get("expires_at", 0)
        
        if current_time > expires_at:
            # Xóa session hết hạn
            del sessions[token]
            save_sessions(sessions)
            return False, None, "Session đã hết hạn"
        
        # Session hợp lệ
        email = session_info.get("email")
        return True, email, "Session hợp lệ"
        
    except Exception as e:
        print(f"Lỗi khi verify session: {e}")
        return False, None, f"Lỗi khi kiểm tra session: {str(e)}"


def delete_session(token):
    """
    Xóa session
    
    Args:
        token: Session token cần xóa
    
    Returns:
        bool: True nếu xóa thành công, False nếu có lỗi
    """
    try:
        sessions = load_sessions()
        
        if token in sessions:
            del sessions[token]
            save_sessions(sessions)
            print(f"✅ Đã xóa session: {token[:20]}...")
            return True
        
        return False
    except Exception as e:
        print(f"Lỗi khi xóa session: {e}")
        return False


def clean_expired_sessions(sessions=None):
    """
    Xóa tất cả các session đã hết hạn
    
    Args:
        sessions: Dictionary sessions (nếu None thì sẽ load từ file)
    
    Returns:
        int: Số lượng session đã xóa
    """
    try:
        if sessions is None:
            sessions = load_sessions()
        
        current_time = time.time()
        expired_tokens = []
        
        for token, session_info in sessions.items():
            expires_at = session_info.get("expires_at", 0)
            if current_time > expires_at:
                expired_tokens.append(token)
        
        # Xóa các session hết hạn
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            save_sessions(sessions)
            print(f"✅ Đã xóa {len(expired_tokens)} session hết hạn")
        
        return len(expired_tokens)
    except Exception as e:
        print(f"Lỗi khi clean expired sessions: {e}")
        return 0


def get_session_info(token):
    """
    Lấy thông tin session
    
    Args:
        token: Session token
    
    Returns:
        dict: Thông tin session hoặc None nếu không tìm thấy
    """
    try:
        sessions = load_sessions()
        
        if token in sessions:
            session_info = sessions[token].copy()
            # Chuyển đổi timestamp sang datetime string để dễ đọc
            if "created_at" in session_info:
                session_info["created_at_str"] = datetime.fromtimestamp(session_info["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
            if "expires_at" in session_info:
                session_info["expires_at_str"] = datetime.fromtimestamp(session_info["expires_at"]).strftime("%Y-%m-%d %H:%M:%S")
            return session_info
        
        return None
    except Exception as e:
        print(f"Lỗi khi lấy session info: {e}")
        return None

