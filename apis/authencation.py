"""
Module xử lý xác thực và tính toán thanh toán
"""
import json
import os
import sys
from datetime import datetime

# Import db_lock để đảm bảo xử lý tuần tự
# Thêm thư mục gốc vào path để import utils
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from utils.db_lock import with_db_lock


def doc_config(config_file="config/pay_ment.json"):
    """
    Đọc thông tin từ file config (định dạng JSON)
    
    Args:
        config_file: Đường dẫn đến file config
        
    Returns:
        dict: Dictionary chứa thông tin từ config, {} nếu lỗi
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file config: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi parse JSON config: {e}")
        return {}
    except Exception as e:
        print(f"❌ Lỗi khi đọc file config: {e}")
        return {}


def parse_cost(cost_value):
    """
    Parse giá trị COST từ string hoặc number
    
    Args:
        cost_value: Giá trị COST (có thể là string "200.000" hoặc number)
        
    Returns:
        float: Giá trị cost đã parse, None nếu lỗi
    """
    try:
        if isinstance(cost_value, str):
            # Loại bỏ dấu chấm ngăn cách hàng nghìn và chuyển sang float
            cost_str = cost_value.replace('.', '').replace(',', '.')
            return float(cost_str)
        else:
            return float(cost_value)
    except (ValueError, TypeError):
        print(f"❌ Không thể parse giá trị COST: {cost_value}")
        return None


def parse_content(content):
    """
    Parse content để lấy id_sl
    
    Logic:
    - Tìm đoạn text giữa "AUTO" và "END" trong content
    - Nếu không tìm thấy AUTO hoặc END: Giữ nguyên content
    
    Args:
        content: Chuỗi content từ request SePay
        
    Returns:
        str: id_sl đã được parse (đoạn text giữa AUTO và END)
    
    Example:
        Input: "MBVCB.11605994255.405978 AUTOid0c0nUPf3rjZwzpA3yD-50END tu 1015360468..."
        Output: "id0c0nUPf3rjZwzpA3yD-50"
        
        Input: "AUTOtest1234567890123450END"
        Output: "test1234567890123450"
    """
    try:
        if not content:
            return content
        
        content_str = str(content).strip()
        
        # Kiểm tra nếu content chứa "AUTO" và "END"
        if "AUTO" in content_str and "END" in content_str:
            # Tìm vị trí của AUTO và END
            auto_index = content_str.find("AUTO")
            end_index = content_str.find("END", auto_index)  # Tìm END sau AUTO
            
            if auto_index != -1 and end_index != -1:
                # Lấy đoạn text giữa AUTO và END
                id_sl = content_str[auto_index + len("AUTO"):end_index].strip()
                print(f"📝 Parse content: Tìm thấy AUTO...END, lấy đoạn giữa: {id_sl}")
                return id_sl
            else:
                # Không tìm thấy cả AUTO và END, giữ nguyên content
                print(f"⚠️ Parse content: Không tìm thấy AUTO hoặc END, giữ nguyên content")
                return content_str
        else:
            # Không có AUTO hoặc END, giữ nguyên content
            print(f"⚠️ Parse content: Không tìm thấy AUTO hoặc END, giữ nguyên content")
            return content_str
            
    except Exception as e:
        print(f"❌ Lỗi khi parse content: {e}")
        return content


def doc_data_json(db_file="db/data.json"):
    """
    Đọc dữ liệu từ file data.json
    (Không cần lock riêng vì sẽ được lock ở hàm gọi)
    
    Args:
        db_file: Đường dẫn đến file data.json
        
    Returns:
        list: Danh sách các object trong data.json, [] nếu file không tồn tại hoặc lỗi
    """
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi parse JSON trong file data.json: {e}")
        return []
    except Exception as e:
        print(f"❌ Lỗi khi đọc file data.json: {e}")
        return []


def luu_data_json(data, db_file="db/data.json"):
    """
    Lưu dữ liệu vào file data.json
    
    Args:
        data: Danh sách các object cần lưu
        db_file: Đường dẫn đến file data.json
        
    Returns:
        bool: True nếu lưu thành công, False nếu lỗi
    """
    try:
        # Tạo thư mục db nếu chưa tồn tại
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        with open(db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lưu file data.json: {e}")
        return False


@with_db_lock
def xu_ly_thanh_toan(id_sl, pay_ment, config_file="config/pay_ment.json", db_file="db/data.json"):
    """
    Xử lý tính toán thanh toán và tạo đối tượng trong data.json
    
    Logic:
    - Tách id_sl: 
      + Nếu có dấu "-": phần trước dấu "-" là id, phần sau là sl (format: {id}-{sl})
      + Nếu không có dấu "-": 20 ký tự đầu là id, phần còn lại là sl (format: {id}{sl})
    - Tính toán: COST * (sl/LIMIT)
    - So sánh với pay_ment
    - Nếu đúng: tạo object với id, limit=sl, count=0, active=true
    - Nếu sai: limit = pay_ment/COST
    
    Args:
        id_sl: Chuỗi kết hợp id và sl
            - Format 1: "{id}-{sl}" (ví dụ: "id0c0nUPf3rjZwzpA3yD-50")
            - Format 2: "{id}{sl}" (ví dụ: "id0c0nUPf3rjZwzpA3yD50" - 20 ký tự đầu là id)
        pay_ment: Số tiền thanh toán thực tế
        config_file: Đường dẫn đến file config chứa COST và LIMIT
        db_file: Đường dẫn đến file data.json
        
    Returns:
        tuple: (success: bool, message: str, data: dict)
            - success: True nếu thành công, False nếu lỗi
            - message: Thông báo kết quả
            - data: Object đã tạo (nếu thành công)
    """
    try:
        # Chuyển id_sl sang string nếu chưa phải
        id_sl_str = str(id_sl).strip()
        
        # Kiểm tra độ dài id_sl
        if len(id_sl_str) < 20:
            return False, f"id_sl phải có ít nhất 20 ký tự, hiện tại có {len(id_sl_str)} ký tự", None
        
        # Tách id_sl: 
        # - Nếu có dấu "-": phần trước dấu "-" là id, phần sau là sl
        # - Nếu không có dấu "-": 20 ký tự đầu là id, phần còn lại là sl
        if "-" in id_sl_str:
            # Format: {id}-{sl}
            parts = id_sl_str.split("-", 1)  # Tách tại dấu "-" đầu tiên
            id = parts[0].strip()
            sl_str = parts[1].strip() if len(parts) > 1 else ""
            
            # Kiểm tra id phải có ít nhất 20 ký tự
            if len(id) < 20:
                return False, f"id phải có ít nhất 20 ký tự, hiện tại có {len(id)} ký tự", None
        else:
            # Format: {id}{sl} (20 ký tự đầu là id, phần còn lại là sl)
            id = id_sl_str[:20]
            sl_str = id_sl_str[20:]
        
        # Kiểm tra sl không rỗng
        if not sl_str:
            return False, "Phần sl không được rỗng", None
        
        # Đọc config
        config = doc_config(config_file)
        if not config:
            return False, "Không thể đọc file config", None
        
        # Lấy COST và LIMIT từ config
        cost_value = config.get("COST")
        limit_value = config.get("LIMIT")
        
        if cost_value is None:
            return False, "Không tìm thấy COST trong config", None
        if limit_value is None:
            return False, "Không tìm thấy LIMIT trong config", None
        
        # Parse COST
        cost = parse_cost(cost_value)
        if cost is None:
            return False, f"Không thể parse COST: {cost_value}", None
        
        # Chuyển LIMIT sang số
        try:
            limit = float(limit_value)
        except (ValueError, TypeError):
            return False, f"LIMIT không hợp lệ: {limit_value}", None
        
        # Chuyển sl và pay_ment sang số
        try:
            sl_num = float(sl_str)
            pay_ment_num = float(pay_ment)
        except (ValueError, TypeError):
            return False, f"sl hoặc pay_ment không hợp lệ: sl={sl_str}, pay_ment={pay_ment}", None
        
        # Tính toán: COST * (sl/LIMIT)
        expected_amount = cost * (sl_num / limit)
        
        # So sánh với pay_ment (cho phép sai số nhỏ do float)
        epsilon = 0.01
        is_match = abs(expected_amount - pay_ment_num) <= epsilon
        
        # Đọc data.json hiện tại
        data_list = doc_data_json(db_file)
        
        # Kiểm tra xem id đã tồn tại chưa
        existing_index = None
        for i, item in enumerate(data_list):
            if item.get("id") == id:
                existing_index = i
                break
        
        # Lấy thời gian hiện tại (ISO format)
        current_time = datetime.now().isoformat()
        
        # Tạo object mới
        if is_match:
            # Nếu đúng: limit = sl, count = 0, active = true
            new_object = {
                "id": id,
                "limit": int(sl_num) if sl_num.is_integer() else sl_num,
                "count": 0,
                "active": True,
                "created_at": current_time
            }
            message = f"✅ Tính toán đúng! Đã tạo object với limit={sl_num}"
        else:
            # Nếu sai: limit = pay_ment/COST
            calculated_limit = pay_ment_num / cost
            new_object = {
                "id": id,
                "limit": int(calculated_limit) if calculated_limit.is_integer() else round(calculated_limit, 2),
                "count": 0,
                "active": True,
                "created_at": current_time
            }
            message = f"⚠️ Tính toán không khớp! Expected: {expected_amount}, Received: {pay_ment_num}. Đã tạo object với limit={pay_ment_num}/COST={calculated_limit}"
        
        # Cập nhật hoặc thêm mới vào data_list
        if existing_index is not None:
            # Cập nhật object đã tồn tại - giữ nguyên created_at nếu có, nếu không thì thêm mới
            existing_object = data_list[existing_index]
            if "created_at" not in existing_object:
                new_object["created_at"] = current_time
            else:
                new_object["created_at"] = existing_object["created_at"]
            # Thêm updated_at để theo dõi thời gian cập nhật
            new_object["updated_at"] = current_time
            data_list[existing_index] = new_object
        else:
            # Thêm object mới
            data_list.append(new_object)
        
        # Lưu vào file
        if luu_data_json(data_list, db_file):
            return True, message, new_object
        else:
            return False, "Không thể lưu vào file data.json", None
            
    except Exception as e:
        error_msg = f"❌ Lỗi khi xử lý thanh toán: {e}"
        return False, error_msg, None


if __name__ == "__main__":
    # Test hàm parse_content
    print("📝 Test hàm parse_content()")
    print("=" * 60)
    
    # Test case 1: Content có AUTO và END với sl
    print("\nTest 1: Content có AUTO...END với sl")
    content_1 = "MBVCB.11605994255.405978 AUTOid0c0nUPf3rjZwzpA3yD-50END tu 1015360468 HOANG NGOC HIEP toi 0966549624 HOANG NGOC HIEP tai MB- Ma GD ACSP/ br40597"
    result_1 = parse_content(content_1)
    print(f"Content gốc: {content_1}")
    print(f"id_sl (sau parse): {result_1}")
    print(f"Expected: id0c0nUPf3rjZwzpA3yD-50")
    
    # Test case 2: Content có AUTO và END không có sl
    print("\nTest 2: Content có AUTO...END không có sl")
    content_2 = "MBVCB AUTOtest1234567890123450END chuyen tien"
    result_2 = parse_content(content_2)
    print(f"Content gốc: {content_2}")
    print(f"id_sl (sau parse): {result_2}")
    print(f"Expected: test1234567890123450")
    
    # Test case 3: Content chỉ có AUTO, không có END
    print("\nTest 3: Content chỉ có AUTO, không có END")
    content_3 = "AUTOtest1234567890123450 chuyen tien"
    result_3 = parse_content(content_3)
    print(f"Content gốc: {content_3}")
    print(f"id_sl (sau parse): {result_3}")
    print(f"Expected: AUTOtest1234567890123450 chuyen tien (giữ nguyên)")
    
    # Test case 4: Content không có AUTO và END
    print("\nTest 4: Content không có AUTO và END")
    content_4 = "test1234567890123450"  # id_sl thông thường
    result_4 = parse_content(content_4)
    print(f"Content gốc: {content_4}")
    print(f"id_sl (sau parse): {result_4}")
    print(f"Expected: test1234567890123450 (giữ nguyên)")
    
    # Test case 5: Content rỗng
    print("\nTest 5: Content rỗng")
    content_5 = ""
    result_5 = parse_content(content_5)
    print(f"Content gốc: '{content_5}'")
    print(f"id_sl (sau parse): '{result_5}'")
    
    # Test case 6: Content có nhiều AUTO và END
    print("\nTest 6: Content có nhiều AUTO và END (lấy cái đầu tiên)")
    content_6 = "AUTOfirst1234567890123450END AUTOsecond1234567890123450END"
    result_6 = parse_content(content_6)
    print(f"Content gốc: {content_6}")
    print(f"id_sl (sau parse): {result_6}")
    print(f"Expected: first1234567890123450")
    
    print("\n" + "=" * 60)
    print("📝 Test hàm xu_ly_thanh_toan()")
    print("=" * 60)
    
    # Test case 1: Format có dấu "-" (AUTO{id}-{sl}END)
    print("\nTest 1: Format có dấu '-' (AUTO{id}-{sl}END)")
    id_sl_1 = "id0c0nUPf3rjZwzpA3yD-50"  # Format: {id}-{sl}
    result = xu_ly_thanh_toan(id_sl=id_sl_1, pay_ment=100000)
    print(f"id_sl: {id_sl_1}")
    print(f"id: id0c0nUPf3rjZwzpA3yD, sl: 50")
    print(f"Result: {result}")
    
    # Test case 2: Format không có dấu "-" (AUTO{id}{sl}END hoặc {id}{sl})
    print("\nTest 2: Format không có dấu '-' (20 ký tự đầu là id, phần còn lại là sl)")
    id_sl_2 = "test1234567890123450"  # 20 ký tự đầu là id, "50" là sl
    result = xu_ly_thanh_toan(id_sl=id_sl_2, pay_ment=100000)
    print(f"id_sl: {id_sl_2}")
    print(f"id: {id_sl_2[:20]}, sl: {id_sl_2[20:]}")
    print(f"Result: {result}")
    
    # Test case 3: id_sl quá ngắn
    print("\nTest 3: id_sl quá ngắn (phải có ít nhất 20 ký tự)")
    id_sl_3 = "short123"  # Chỉ có 8 ký tự
    result = xu_ly_thanh_toan(id_sl=id_sl_3, pay_ment=100000)
    print(f"id_sl: {id_sl_3}")
    print(f"Result: {result}")
    
    # Test case 4: Format có dấu "-" nhưng id quá ngắn
    print("\nTest 4: Format có dấu '-' nhưng id quá ngắn")
    id_sl_4 = "short123-50"  # id chỉ có 8 ký tự
    result = xu_ly_thanh_toan(id_sl=id_sl_4, pay_ment=100000)
    print(f"id_sl: {id_sl_4}")
    print(f"Result: {result}")

