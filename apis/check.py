"""
Module kiểm tra trạng thái tài khoản theo id
"""
import json
import os
import sys

# Import db_lock để đảm bảo xử lý tuần tự
# Thêm thư mục gốc vào path để import utils
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from utils.db_lock import with_db_lock


@with_db_lock
def check(id):
    """
    Hàm kiểm tra id có tồn tại và active là true hay false
    
    Args:
        id (str): ID của tài khoản cần kiểm tra
        
    Returns:
        tuple: (status_code: int, data: dict)
            - status_code: HTTP status code (200: thành công, 300: bị khóa, 404: không tồn tại, 500: lỗi server)
            - data: Dữ liệu trả về, luôn chứa:
                - id: ID của tài khoản
                - count: Số lần đã sử dụng (hoặc 0 nếu không tìm thấy id)
                - limit: Giới hạn sử dụng (hoặc 0 nếu không tìm thấy id)
                - message: Thông báo kết quả
    
    Logic:
        1. Tìm id trong db/data.json
        2. Nếu không tìm thấy id → trả về 404 với message "Chưa mua thành công", count=0, limit=0
        3. Nếu tìm thấy id nhưng active = false → trả về 300 với message "Tài khoản bị khóa", kèm count và limit
        4. Nếu tìm thấy id và active = true → trả về 200 với message "Thành công", kèm count và limit
    """
    # Đường dẫn đến file data.json
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    
    try:
        # Đọc file data.json
        if not os.path.exists(db_path):
            return 500, {
                "id": id,
                "count": 0,
                "limit": 0,
                "message": "File db/data.json không tồn tại"
            }
        
        with open(db_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        # Kiểm tra data_list có phải là list không
        if not isinstance(data_list, list):
            return 500, {
                "id": id,
                "count": 0,
                "limit": 0,
                "message": "Dữ liệu trong db/data.json không hợp lệ"
            }
        
        # Tìm object có id trùng khớp
        found_item = None
        
        for item in data_list:
            if isinstance(item, dict) and item.get('id') == id:
                found_item = item
                break
        
        # Nếu không tìm thấy id
        if found_item is None:
            return 404, {
                "id": id,
                "count": 0,
                "limit": 0,
                "message": "Chưa mua thành công"
            }
        
        # Lấy count và limit từ found_item
        count = found_item.get('count', 0)
        limit = found_item.get('limit', 0)
        
        # Kiểm tra active
        active = found_item.get('active', False)
        
        if not active:
            return 300, {
                "id": id,
                "count": count,
                "limit": limit,
                "message": "Tài khoản bị khóa"
            }
        
        # Nếu id tồn tại và active = true → thành công
        return 200, {
            "id": id,
            "count": count,
            "limit": limit,
            "message": "Thành công"
        }
    
    except json.JSONDecodeError as e:
        return 500, {
            "id": id,
            "count": 0,
            "limit": 0,
            "message": f"Lỗi đọc file JSON: {str(e)}"
        }
    
    except Exception as e:
        return 500, {
            "id": id,
            "count": 0,
            "limit": 0,
            "message": f"Lỗi không xác định: {str(e)}"
        }

