"""
Module xử lý thêm count cho tài khoản
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
def add_count(id):
    """
    Hàm được gọi để tăng count cho tài khoản theo id
    
    Args:
        id (str): ID của tài khoản cần tăng count
        
    Returns:
        tuple: (success: bool, message: str, data: dict)
            - success: True nếu thành công, False nếu có lỗi
            - message: Thông báo kết quả
            - data: Dữ liệu trả về (nếu có)
    
    Logic:
        1. Tìm id trong db/data.json
        2. Kiểm tra active:
           - Nếu false → trả về mã lỗi và báo tài khoản bị khoá
           - Nếu true → tiếp tục:
             3. Kiểm tra count > limit:
                - Nếu đúng → báo tài khoản bị hết lượt và xoá đối tượng đó
                - Nếu count <= limit → tăng count lên 1
    """
    # Đường dẫn đến file data.json
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    
    try:
        # Đọc file data.json
        if not os.path.exists(db_path):
            return False, "File db/data.json không tồn tại", {
                "id": id,
                "count": 0,
                "limit": 0
            }
        
        with open(db_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        # Kiểm tra data_list có phải là list không
        if not isinstance(data_list, list):
            return False, "Dữ liệu trong db/data.json không hợp lệ", {
                "id": id,
                "count": 0,
                "limit": 0
            }
        
        # Tìm object có id trùng khớp
        found_index = None
        found_item = None
        
        for index, item in enumerate(data_list):
            if isinstance(item, dict) and item.get('id') == id:
                found_index = index
                found_item = item
                break
        
        # Nếu không tìm thấy id
        if found_index is None:
            return False, f"Không tìm thấy tài khoản với id: {id}", {
                "id": id,
                "count": 0,
                "limit": 0
            }
        
        # Lấy count và limit từ found_item
        count = found_item.get('count', 0)
        limit = found_item.get('limit', 0)
        
        # Kiểm tra active
        if not found_item.get('active', False):
            return False, "Tài khoản bị khoá", {
                "error_code": "ACCOUNT_LOCKED",
                "id": id,
                "count": count,
                "limit": limit,
                "active": False
            }
        
        # Kiểm tra count > limit
        if count > limit:
            # Xoá đối tượng đó khỏi danh sách
            data_list.pop(found_index)
            
            # Ghi lại file
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            
            return False, "Tài khoản bị hết lượt và đã được xóa", {
                "error_code": "ACCOUNT_LIMIT_EXCEEDED",
                "id": id,
                "count": count,
                "limit": limit
            }
        
        # Nếu count <= limit, tăng count lên 1
        found_item['count'] = count + 1
        
        # Cập nhật lại vào data_list
        data_list[found_index] = found_item
        
        # Ghi lại file
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        # Reset count tạm trong file temp_count.json - xóa id khỏi file
        temp_count_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'temp_count.json')
        if os.path.exists(temp_count_path):
            try:
                with open(temp_count_path, 'r', encoding='utf-8') as f:
                    temp_count_data = json.load(f)
                    if isinstance(temp_count_data, dict) and id in temp_count_data:
                        # Xóa id khỏi file temp_count.json
                        del temp_count_data[id]
                        
                        # Lưu lại file (nếu file rỗng thì vẫn lưu dict rỗng)
                        with open(temp_count_path, 'w', encoding='utf-8') as f:
                            json.dump(temp_count_data, f, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, Exception):
                # Nếu có lỗi khi đọc/ghi file temp_count, không ảnh hưởng đến kết quả chính
                pass
        
        # Trả về kết quả thành công
        return True, f"Đã tăng count thành công. Count hiện tại: {found_item['count']}", {
            "id": id,
            "count": found_item['count'],
            "limit": limit,
            "active": True
        }
    
    except json.JSONDecodeError as e:
        return False, f"Lỗi đọc file JSON: {str(e)}", {
            "id": id,
            "count": 0,
            "limit": 0
        }
    
    except Exception as e:
        return False, f"Lỗi không xác định: {str(e)}", {
            "id": id,
            "count": 0,
            "limit": 0
        }

