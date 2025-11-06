import json


def kiem_tra_va_tang_count(id, db_file="db/data.json"):
    """
    Kiểm tra active và count trước khi tăng count.
    - Nếu active = false → trả về False và thông báo "tài khoản chưa được kích hoạt"
    - Nếu active = true và count > limit → trả về False, chuyển active về false, thông báo "kí tự đã đến giới hạn"
    - Nếu active = true và count <= limit → trả về True, tăng count lên 1
    
    Args:
        id: ID của đơn hàng cần kiểm tra
        db_file: Đường dẫn đến file database JSON
        
    Returns:
        tuple: (bool, str) - (True/False, thông báo)
            - True: đã tăng count lên 1 thành công
            - False: không thể tăng count (tài khoản chưa kích hoạt hoặc đã đến giới hạn)
    """
    try:
        # Đọc database
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Tìm id trong database
        found = False
        for item in data:
            if item.get("id") == id:
                found = True
                
                # Kiểm tra active trước
                active = item.get("active", False)
                if not active:
                    message = "tài khoản chưa được kích hoạt"
                    print(f"❌ {message}")
                    return False, message
                
                # Lấy giá trị count và limit
                count = item.get("count", 0)
                limit = item.get("limit", 0)
                
                # Kiểm tra count có vượt quá limit không
                if count > limit:
                    # Chuyển active về false
                    item["active"] = False
                    
                    # Ghi lại vào file
                    with open(db_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    message = "kí tự đã đến giới hạn"
                    print(f"❌ {message}. Đã chuyển active về false.")
                    return False, message
                
                # Nếu chưa vượt giới hạn, tăng count lên 1
                item["count"] = count + 1
                
                # Ghi lại vào file
                with open(db_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                message = f"✅ Đã tăng count từ {count} lên {count + 1}. Limit: {limit}"
                print(f"✅ {message}")
                return True, message
        
        if not found:
            message = f"❌ Không tìm thấy id: {id} trong database"
            print(message)
            return False, message
            
    except FileNotFoundError:
        message = f"❌ Không tìm thấy file database: {db_file}"
        print(message)
        return False, message
    except json.JSONDecodeError as e:
        message = f"❌ Lỗi khi đọc file JSON: {e}"
        print(message)
        return False, message
    except Exception as e:
        message = f"❌ Lỗi khi kiểm tra count: {e}"
        print(message)
        return False, message


if __name__ == "__main__":
    # Test hàm kiểm tra count
    print("📝 Ví dụ sử dụng:")
    print("result, message = kiem_tra_va_tang_count(id='0093650001')")
    print("\n" + "="*50)
    
    # Test với id có sẵn
    result, message = kiem_tra_va_tang_count(id="4721170002")
    print(f"\nKết quả: {result}")
    print(f"Thông báo: {message}")

