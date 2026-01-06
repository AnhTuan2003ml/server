"""
Module xử lý thêm count cho tài khoản với cơ chế verify
"""
import json
import os
import sys
import uuid
from datetime import datetime

# Import db_lock để đảm bảo xử lý tuần tự
# Thêm thư mục gốc vào path để import utils
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from utils.db_lock import with_db_lock


@with_db_lock
def prepare_add_count(id):
    """
    Hàm chuẩn bị request tăng count cho tài khoản theo id
    Chỉ tạo pending request, chưa thực sự tăng count

    Args:
        id (str): ID của tài khoản cần tăng count

    Returns:
        tuple: (success: bool, message: str, data: dict)
            - success: True nếu thành công, False nếu có lỗi
            - message: Thông báo kết quả
            - data: Dữ liệu trả về (bao gồm request_id để verify)

    Logic:
        1. Tìm id trong db/data.json
        2. Kiểm tra active:
           - Nếu false → trả về mã lỗi và báo tài khoản bị khoá
           - Nếu true → tiếp tục:
             3. Kiểm tra count > limit:
                - Nếu đúng → báo tài khoản bị hết lượt
                - Nếu count <= limit → tạo pending request
    """

@with_db_lock
def execute_add_count(request_id):
    """
    Hàm thực hiện tăng count thực sự sau khi verify thành công

    Args:
        request_id (str): ID của pending request

    Returns:
        tuple: (success: bool, message: str, data: dict)
    """
    # Đường dẫn đến các file
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    pending_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'pending_requests.json')
    temp_count_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'temp_count.json')

    try:
        # Đọc pending_requests.json
        if not os.path.exists(pending_path):
            return False, "File pending_requests.json không tồn tại", {}

        with open(pending_path, 'r', encoding='utf-8') as f:
            pending_requests = json.load(f)

        # Kiểm tra request_id có tồn tại không
        if request_id not in pending_requests:
            return False, f"Không tìm thấy request với ID: {request_id}", {}

        pending_request = pending_requests[request_id]

        # Kiểm tra trạng thái
        if pending_request.get('status') != 'pending':
            return False, f"Request đã được xử lý với trạng thái: {pending_request.get('status')}", {}

        account_id = pending_request['id']

        # Đọc file data.json
        if not os.path.exists(db_path):
            return False, "File db/data.json không tồn tại", {}

        with open(db_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        # Tìm và cập nhật tài khoản
        found_index = None
        found_item = None

        for index, item in enumerate(data_list):
            if isinstance(item, dict) and item.get('id') == account_id:
                found_index = index
                found_item = item
                break

        if found_index is None:
            return False, f"Không tìm thấy tài khoản với id: {account_id}", {}

        # Kiểm tra lại trạng thái active và limit (để đảm bảo không bị thay đổi)
        if not found_item.get('active', False):
            return False, "Tài khoản bị khoá", {
                "error_code": "ACCOUNT_LOCKED",
                "id": account_id,
                "count": found_item.get('count', 0),
                "limit": found_item.get('limit', 0),
                "active": False
            }

        count = found_item.get('count', 0)
        limit = found_item.get('limit', 0)

        if count >= limit:
            return False, "Tài khoản đã đạt giới hạn", {
                "error_code": "ACCOUNT_LIMIT_EXCEEDED",
                "id": account_id,
                "count": count,
                "limit": limit
            }

        # Tăng count lên 1
        found_item['count'] = count + 1

        # Cập nhật lại vào data_list
        data_list[found_index] = found_item

        # Ghi lại file data.json
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

        # Cập nhật trạng thái pending request thành completed
        pending_request['status'] = 'completed'
        pending_request['completed_at'] = datetime.now().isoformat()
        pending_requests[request_id] = pending_request

        # Ghi lại file pending_requests.json
        with open(pending_path, 'w', encoding='utf-8') as f:
            json.dump(pending_requests, f, ensure_ascii=False, indent=2)

        # Reset count tạm trong file temp_count.json - xóa id khỏi file
        if os.path.exists(temp_count_path):
            try:
                with open(temp_count_path, 'r', encoding='utf-8') as f:
                    temp_count_data = json.load(f)
                    if isinstance(temp_count_data, dict) and account_id in temp_count_data:
                        # Xóa id khỏi file temp_count.json
                        del temp_count_data[account_id]

                        # Lưu lại file (nếu file rỗng thì vẫn lưu dict rỗng)
                        with open(temp_count_path, 'w', encoding='utf-8') as f:
                            json.dump(temp_count_data, f, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, Exception):
                # Nếu có lỗi khi đọc/ghi file temp_count, không ảnh hưởng đến kết quả chính
                pass

        # Trả về kết quả thành công
        return True, f"Đã tăng count thành công. Count hiện tại: {found_item['count']}", {
            "request_id": request_id,
            "id": account_id,
            "count": found_item['count'],
            "limit": limit,
            "active": True,
            "status": "completed"
        }

    except json.JSONDecodeError as e:
        return False, f"Lỗi đọc file JSON: {str(e)}", {}

    except Exception as e:
        return False, f"Lỗi không xác định: {str(e)}", {}


def cancel_pending_request(request_id):
    """
    Hàm hủy pending request khi verify thất bại

    Args:
        request_id (str): ID của pending request

    Returns:
        tuple: (success: bool, message: str, data: dict)
    """
    pending_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'pending_requests.json')

    try:
        # Đọc pending_requests.json
        if not os.path.exists(pending_path):
            return False, "File pending_requests.json không tồn tại", {}

        with open(pending_path, 'r', encoding='utf-8') as f:
            pending_requests = json.load(f)

        # Kiểm tra request_id có tồn tại không
        if request_id not in pending_requests:
            return False, f"Không tìm thấy request với ID: {request_id}", {}

        pending_request = pending_requests[request_id]

        # Kiểm tra trạng thái
        if pending_request.get('status') != 'pending':
            return False, f"Request đã được xử lý với trạng thái: {pending_request.get('status')}", {}

        # Cập nhật trạng thái thành cancelled
        pending_request['status'] = 'cancelled'
        pending_request['cancelled_at'] = datetime.now().isoformat()
        pending_requests[request_id] = pending_request

        # Ghi lại file
        with open(pending_path, 'w', encoding='utf-8') as f:
            json.dump(pending_requests, f, ensure_ascii=False, indent=2)

        return True, f"Đã hủy request {request_id}", {
            "request_id": request_id,
            "status": "cancelled"
        }

    except json.JSONDecodeError as e:
        return False, f"Lỗi đọc file JSON: {str(e)}", {}

    except Exception as e:
        return False, f"Lỗi không xác định: {str(e)}", {}


# Hàm cũ để tương thích ngược (sẽ được sử dụng trong verify API)
def add_count(id):
    """
    Hàm cũ - được giữ lại để tương thích ngược
    Bây giờ sẽ gọi prepare_add_count thay vì thực hiện ngay
    """
    return prepare_add_count(id)
def prepare_add_count(id):
    """
    Hàm chuẩn bị request tăng count - chỉ kiểm tra và tạo pending request
    """
    # Đường dẫn đến các file
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'data.json')
    pending_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'pending_requests.json')

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
            return False, "Tài khoản bị hết lượt", {
                "error_code": "ACCOUNT_LIMIT_EXCEEDED",
                "id": id,
                "count": count,
                "limit": limit
            }

        # Đọc pending_requests.json
        pending_requests = {}
        if os.path.exists(pending_path):
            try:
                with open(pending_path, 'r', encoding='utf-8') as f:
                    pending_requests = json.load(f)
            except json.JSONDecodeError:
                pending_requests = {}

        # Đếm số lượng request pending cho account này
        pending_count = 0
        for req_id, req_data in pending_requests.items():
            if (isinstance(req_data, dict) and
                req_data.get('id') == id and
                req_data.get('status') == 'pending'):
                pending_count += 1

        # Kiểm tra tổng count + pending_count có vượt quá limit không
        total_used = count + pending_count
        if total_used >= limit:
            return False, f"Tài khoản đã đạt giới hạn sử dụng. Count hiện tại: {count}, Pending requests: {pending_count}, Limit: {limit}", {
                "error_code": "ACCOUNT_LIMIT_REACHED",
                "id": id,
                "count": count,
                "pending_count": pending_count,
                "limit": limit,
                "total_used": total_used
            }

        # Tạo request ID duy nhất
        request_id = str(uuid.uuid4())

        # Tạo pending request
        pending_requests[request_id] = {
            "id": id,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "count": count,
            "limit": limit
        }

        # Ghi lại file pending_requests.json
        with open(pending_path, 'w', encoding='utf-8') as f:
            json.dump(pending_requests, f, ensure_ascii=False, indent=2)

        # Trả về kết quả thành công với request_id
        return True, f"Đã tạo request tăng count. Vui lòng verify với request_id: {request_id}", {
            "request_id": request_id,
            "id": id,
            "count": count,
            "limit": limit,
            "active": True,
            "status": "pending"
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

