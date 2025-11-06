"""
Module xử lý API cho users
Cung cấp các hàm xử lý request/response cho các endpoint users
"""

import json
import os
import sys

# Thêm thư mục gốc vào path để import utils
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from utils.db_lock import with_db_lock
from apis.qr_code import doc_data_json, luu_data_json


def get_users():
    """
    Lấy danh sách tất cả users từ db/data.json
    
    Returns:
        list: Danh sách users
    """
    return doc_data_json("db/data.json")


@with_db_lock
def delete_user(user_id):
    """
    Xóa user theo ID
    
    Args:
        user_id: ID của user cần xóa
    
    Returns:
        tuple: (success: bool, message: str, data: dict)
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    
    try:
        # Đọc file data.json
        if not os.path.exists(db_path):
            return False, "File db/data.json không tồn tại", None
        
        users = doc_data_json(db_path)
        
        # Kiểm tra users có phải là list không
        if not isinstance(users, list):
            return False, "Dữ liệu trong db/data.json không hợp lệ", None
        
        # Tìm user có id trùng khớp
        found_index = None
        found_user = None
        
        for index, user in enumerate(users):
            if isinstance(user, dict) and user.get('id') == user_id:
                found_index = index
                found_user = user
                break
        
        # Nếu không tìm thấy user
        if found_index is None:
            return False, f"Không tìm thấy user với id: {user_id}", None
        
        # Xóa user khỏi danh sách
        users.pop(found_index)
        
        # Lưu lại file
        if luu_data_json(users, db_path):
            return True, f"Đã xóa user thành công", found_user
        else:
            return False, "Lỗi khi lưu file", None
            
    except Exception as e:
        return False, f"Lỗi khi xóa user: {str(e)}", None


@with_db_lock
def update_user(user_id, **fields):
    """
    Cập nhật thông tin user
    
    Args:
        user_id: ID của user cần cập nhật
        **fields: Các trường cần cập nhật (limit, active, count, ...)
    
    Returns:
        tuple: (success: bool, message: str, data: dict)
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    
    try:
        # Đọc file data.json
        if not os.path.exists(db_path):
            return False, "File db/data.json không tồn tại", None
        
        users = doc_data_json(db_path)
        
        # Kiểm tra users có phải là list không
        if not isinstance(users, list):
            return False, "Dữ liệu trong db/data.json không hợp lệ", None
        
        # Tìm user có id trùng khớp
        found_index = None
        
        for index, user in enumerate(users):
            if isinstance(user, dict) and user.get('id') == user_id:
                found_index = index
                break
        
        # Nếu không tìm thấy user
        if found_index is None:
            return False, f"Không tìm thấy user với id: {user_id}", None
        
        # Cập nhật các trường
        updated_fields = []
        for field, value in fields.items():
            if field in users[found_index]:
                users[found_index][field] = value
                updated_fields.append(field)
        
        # Lưu lại file
        if luu_data_json(users, db_path):
            return True, f"Đã cập nhật user thành công", users[found_index]
        else:
            return False, "Lỗi khi lưu file", None
            
    except Exception as e:
        return False, f"Lỗi khi cập nhật user: {str(e)}", None


# Handler functions cho API endpoints
def handle_get_users():
    """
    Xử lý request lấy danh sách users
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        users = get_users()
        return True, {
            "users": users,
            "count": len(users)
        }, 200, "Lấy danh sách users thành công"
    except Exception as e:
        return False, None, 500, f"Lỗi khi lấy danh sách users: {str(e)}"


def handle_delete_user(user_id):
    """
    Xử lý request xóa user
    
    Args:
        user_id: ID của user cần xóa
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    if not user_id:
        return False, None, 400, "user_id là bắt buộc"
    
    success, message, data = delete_user(user_id)
    
    if success:
        return True, {
            "deleted_user": data
        }, 200, message
    else:
        status_code = 404 if "Không tìm thấy" in message else 500
        return False, None, status_code, message


def handle_update_user(user_id, fields_dict):
    """
    Xử lý request cập nhật user
    
    Args:
        user_id: ID của user cần cập nhật
        fields_dict: Dictionary chứa các trường cần cập nhật
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    if not user_id:
        return False, None, 400, "user_id là bắt buộc"
    
    if not isinstance(fields_dict, dict) or not fields_dict:
        return False, None, 400, "fields phải là một dictionary không rỗng"
    
    success, message, data = update_user(user_id, **fields_dict)
    
    if success:
        return True, {
            "updated_user": data
        }, 200, message
    else:
        status_code = 404 if "Không tìm thấy" in message else 500
        return False, None, status_code, message


def search_user(user_id):
    """
    Tìm kiếm user theo ID
    
    Args:
        user_id: ID của user cần tìm (có thể là một phần của ID)
    
    Returns:
        tuple: (success: bool, message: str, data: dict or list)
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    
    try:
        # Đọc file data.json
        if not os.path.exists(db_path):
            return False, "File db/data.json không tồn tại", None
        
        users = doc_data_json(db_path)
        
        # Kiểm tra users có phải là list không
        if not isinstance(users, list):
            return False, "Dữ liệu trong db/data.json không hợp lệ", None
        
        # Tìm user có id chứa chuỗi tìm kiếm (case-insensitive)
        if not user_id:
            return False, "user_id không được để trống", None
        
        user_id_lower = user_id.lower()
        found_users = []
        
        for user in users:
            if isinstance(user, dict):
                user_id_in_db = str(user.get('id', '')).lower()
                if user_id_lower in user_id_in_db:
                    found_users.append(user)
        
        if not found_users:
            return False, f"Không tìm thấy user nào với id chứa: {user_id}", None
        
        # Nếu chỉ tìm thấy 1 user, trả về object
        if len(found_users) == 1:
            return True, "Tìm thấy user", found_users[0]
        else:
            return True, f"Tìm thấy {len(found_users)} users", found_users
            
    except Exception as e:
        return False, f"Lỗi khi tìm kiếm user: {str(e)}", None


def handle_search_user(user_id):
    """
    Xử lý request tìm kiếm user
    
    Args:
        user_id: ID của user cần tìm (có thể là một phần của ID)
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    if not user_id:
        return False, None, 400, "user_id là bắt buộc"
    
    success, message, data = search_user(user_id)
    
    if success:
        # Nếu data là dict (1 user), trả về trong trường "user"
        # Nếu data là list (nhiều users), trả về trong trường "users"
        if isinstance(data, dict):
            return True, {
                "user": data,
                "count": 1
            }, 200, message
        else:
            return True, {
                "users": data,
                "count": len(data)
            }, 200, message
    else:
        status_code = 404 if "Không tìm thấy" in message else 500
        return False, None, status_code, message

