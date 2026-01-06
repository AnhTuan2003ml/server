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
                - count: Số lần đã sử dụng thực tế trong database (hoặc 0 nếu không tìm thấy id)
                - temp_count: Số lần check đã được gọi (cộng dồn trong db/temp_count.json)
                - total_temp_count: Tổng count tạm (count + temp_count) để so sánh với limit
                - limit: Giới hạn sử dụng (hoặc 0 nếu không tìm thấy id)
                - message: Thông báo kết quả
                - error: (tùy chọn) Lỗi nếu total_temp_count > limit
    
    Logic:
        1. Tìm id trong db/data.json
        2. Nếu không tìm thấy id → trả về 404 với message "Chưa mua thành công", count=0, limit=0
        3. Nếu tìm thấy id nhưng active = false → trả về 300 với message "Tài khoản bị khóa", kèm count và limit
        4. Nếu tìm thấy id và active = true:
           - Đọc/tạo file db/temp_count.json để lưu count tạm
           - Nếu id chưa có trong temp_count.json (lần đầu khởi tạo):
             * temp_count = 0 (không tăng), count giữ nguyên
           - Nếu id đã có trong temp_count.json (từ lần thứ 2 trở đi):
             * Tăng count tạm của id lên 1 (cộng dồn)
           - Lưu temp_count vào file temp_count.json
           - Tính total_temp_count = count (thực tế) + temp_count (đã cộng dồn)
           - So sánh total_temp_count với limit
           - Nếu total_temp_count > limit → trả về message "Tài khoản đã hết lượt"
           - Nếu total_temp_count <= limit → trả về message "Thành công"
    
    Lưu ý: - Nếu count = 0: temp_count luôn = 0 (reset về 0 để tránh tích lũy không cần thiết)
           - Lần đầu gọi check(id) (khi count > 0): temp_count = 0, count giữ nguyên
           - Từ lần thứ 2 trở đi (khi count > 0): temp_count tăng dần mỗi lần check được gọi
           - Khi add_count được gọi (count thực tế được tăng), count tạm sẽ được reset về 0
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
        found_index = -1
        
        for index, item in enumerate(data_list):
            if isinstance(item, dict) and item.get('id') == id:
                found_item = item
                found_index = index
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
        
        # Đường dẫn đến file temp_count.json
        temp_count_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'temp_count.json')
        
        # Đọc hoặc tạo file temp_count.json
        temp_count_data = {}
        if os.path.exists(temp_count_path):
            try:
                with open(temp_count_path, 'r', encoding='utf-8') as f:
                    temp_count_data = json.load(f)
                    if not isinstance(temp_count_data, dict):
                        temp_count_data = {}
            except (json.JSONDecodeError, Exception):
                temp_count_data = {}
        
        # Kiểm tra xem id đã có trong temp_count_data chưa (khởi tạo hay không)
        is_initializing = id not in temp_count_data
        
        # Lấy count tạm hiện tại của id (mặc định là 0)
        current_temp_count = temp_count_data.get(id, 0)
        
        # Nếu count = 0, reset temp_count về 0 (không tích lũy khi count = 0)
        if count == 0:
            new_temp_count = 0
            temp_count_data[id] = new_temp_count
        # Nếu là lần đầu: temp_count = 0 (không tăng), count giữ nguyên
        elif is_initializing:
            new_temp_count = 0
            temp_count_data[id] = new_temp_count
        # Nếu không phải lần đầu: tăng count tạm lên 1 (cộng dồn)
        else:
            new_temp_count = current_temp_count + 1
            temp_count_data[id] = new_temp_count
        
        # Lưu lại file temp_count.json
        try:
            with open(temp_count_path, 'w', encoding='utf-8') as f:
                json.dump(temp_count_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return 500, {
                "id": id,
                "count": count,
                "limit": limit,
                "message": f"Lỗi ghi file temp_count.json: {str(e)}"
            }
        
        # Tính tổng count tạm = count thực tế + count tạm đã cộng dồn
        total_temp_count = count + new_temp_count
        
        # Kiểm tra tổng count tạm > limit
        if total_temp_count > limit:
            # Trả về lỗi vì đã vượt quá limit
            return 200, {
                "id": id,
                "count": count,  # Count thực tế trong database
                "temp_count": new_temp_count,  # Count tạm đã cộng dồn
                "total_temp_count": total_temp_count,  # Tổng count tạm (count + temp_count)
                "limit": limit,
                "message": "Tài khoản đã hết lượt",
                "error": "Vượt quá giới hạn sử dụng"
            }
        
        # Nếu tổng count tạm <= limit → thành công
        return 200, {
            "id": id,
            "count": count,  # Count thực tế trong database
            "temp_count": new_temp_count,  # Count tạm đã cộng dồn
            "total_temp_count": total_temp_count,  # Tổng count tạm (count + temp_count)
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

