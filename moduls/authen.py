import json


def doc_cost_tu_config(config_file="config/pay_ment.json"):
    """
    Đọc giá trị COST từ file config (định dạng JSON)
    
    Args:
        config_file: Đường dẫn đến file config
        
    Returns:
        float: Giá trị cost, None nếu không tìm thấy hoặc lỗi
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        # Lấy giá trị COST từ JSON
        cost_value = config_data.get("COST")
        if cost_value is None:
            print(f"❌ Không tìm thấy COST trong file config")
            return None
        
        # Xử lý giá trị COST (có thể là string hoặc number)
        if isinstance(cost_value, str):
            # Loại bỏ dấu chấm ngăn cách hàng nghìn và chuyển sang float
            cost_str = cost_value.replace('.', '').replace(',', '.')
            try:
                return float(cost_str)
            except ValueError:
                print(f"❌ Không thể parse giá trị COST: {cost_value}")
                return None
        else:
            # Nếu đã là số thì trả về trực tiếp
            return float(cost_value)
            
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file config: {config_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi parse JSON config: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi khi đọc file config: {e}")
        return None


def kiem_tra_va_active_token(id, token, cost, db_file="db/data.json", config_file="config/pay_ment.json"):
    """
    Kiểm tra token và cost tương ứng với id trong database và so sánh cost với giá trị trong config,
    cập nhật active thành true nếu khớp
    
    Args:
        id: ID của đơn hàng
        token: Token xác thực
        cost: Chi phí đơn hàng để so sánh với cost trong file config
        db_file: Đường dẫn đến file database JSON
        config_file: Đường dẫn đến file config chứa cost
        
    Returns:
        bool: True nếu token và cost khớp và đã cập nhật active, False nếu không khớp hoặc lỗi
    """
    try:
        # Đọc cost từ config
        config_cost = doc_cost_tu_config(config_file)
        if config_cost is None:
            return False
        
        # So sánh cost với giá trị trong config
        try:
            # Chuyển cost về float để so sánh (xử lý cả string và number)
            cost_value = float(cost)
            if abs(cost_value - config_cost) > 0.01:  # Cho phép sai số nhỏ do float
                print(f"❌ Cost không khớp! Cost truyền vào: {cost_value}, Cost trong config: {config_cost}")
                return False
        except (ValueError, TypeError):
            print(f"❌ Cost không hợp lệ: {cost}")
            return False
        
        # Đọc database
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Tìm id trong database
        found = False
        for item in data:
            if item.get("id") == id:
                found = True
                # Kiểm tra token có khớp không
                if item.get("token") == token:
                    # Cập nhật active thành true
                    item["active"] = True
                    # Ghi lại vào file
                    with open(db_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"✅ Token và cost khớp! Đã cập nhật active = true cho id: {id}")
                    return True
                else:
                    print(f"❌ Token không khớp với id: {id}")
                    return False
        
        if not found:
            print(f"❌ Không tìm thấy id: {id} trong database")
            return False
            
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file database: {db_file}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Lỗi định dạng JSON trong file: {db_file}")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra token: {e}")
        return False


if __name__ == "__main__":
    # Test hàm xác thực
    # Ví dụ: kiem_tra_va_active_token(id="0093650001", token="8204b2ba8867f52ac8c1f15a2ca11117ce038719bf37ff5e5bccb6013651a6cb", cost=200000)
    print("⚠️ Hàm kiem_tra_va_active_token() yêu cầu id, token và cost làm tham số")
    print("📝 Ví dụ: kiem_tra_va_active_token(id='0093650001', token='8204b2ba8867f52ac8c1f15a2ca11117ce038719bf37ff5e5bccb6013651a6cb', cost=200000)")

