"""
Module quản lý các file config trong thư mục config/
Hỗ trợ đọc, ghi và chỉnh sửa các trường thông tin trong các file config
"""

import json
import os
from pathlib import Path


# Đường dẫn đến thư mục config
CONFIG_DIR = Path(__file__).parent.parent / "config"


def _get_config_path(file_name):
    """
    Lấy đường dẫn đầy đủ đến file config
    
    Args:
        file_name: Tên file config (có thể có hoặc không có đuôi .json)
    
    Returns:
        Path object đến file config
    
    Raises:
        ValueError: Nếu file_name không hợp lệ
    """
    if not file_name:
        raise ValueError("Tên file không được để trống")
    
    # Thêm đuôi .json nếu chưa có
    if not file_name.endswith('.json'):
        file_name = file_name + '.json'
    
    config_path = CONFIG_DIR / file_name
    
    # Kiểm tra file có tồn tại không
    if not config_path.exists():
        raise FileNotFoundError(f"File config '{file_name}' không tồn tại")
    
    return config_path


def list_configs():
    """
    Liệt kê tất cả các file config có sẵn
    
    Returns:
        list: Danh sách tên các file config (không có đuôi .json)
    """
    if not CONFIG_DIR.exists():
        return []
    
    configs = []
    for file in CONFIG_DIR.glob("*.json"):
        configs.append(file.stem)  # Lấy tên file không có đuôi
    
    return configs


def get_config(file_name):
    """
    Lấy toàn bộ nội dung của file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
    
    Returns:
        dict: Nội dung của file config dưới dạng dictionary
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
    
    Example:
        >>> config = get_config("mail")
        >>> print(config)
        {'sender': 'hoangngochiep62@gmail.com', 'password': '...', 'receiver': '...'}
    """
    config_path = _get_config_path(file_name)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"File '{file_name}' không phải JSON hợp lệ: {str(e)}", e.doc, e.pos)


def get_field(file_name, field_name):
    """
    Lấy giá trị của một trường cụ thể trong file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
        field_name: Tên trường cần lấy (ví dụ: "sender", "STK")
    
    Returns:
        Giá trị của trường (có thể là str, int, float, bool, dict, list, None)
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        KeyError: Nếu trường không tồn tại trong config
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
    
    Example:
        >>> sender = get_field("mail", "sender")
        >>> print(sender)
        'hoangngochiep62@gmail.com'
    """
    config_data = get_config(file_name)
    
    if field_name not in config_data:
        available_fields = ', '.join(config_data.keys())
        raise KeyError(f"Trường '{field_name}' không tồn tại trong '{file_name}'. Các trường có sẵn: {available_fields}")
    
    return config_data[field_name]


def set_field(file_name, field_name, value):
    """
    Cập nhật giá trị của một trường trong file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
        field_name: Tên trường cần cập nhật (ví dụ: "sender", "STK")
        value: Giá trị mới (có thể là str, int, float, bool, dict, list, None)
    
    Returns:
        dict: Toàn bộ config sau khi cập nhật
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
        IOError: Nếu không thể ghi file
    
    Example:
        >>> set_field("mail", "sender", "newemail@gmail.com")
        {'sender': 'newemail@gmail.com', 'password': '...', 'receiver': '...'}
    """
    config_path = _get_config_path(file_name)
    
    # Đọc config hiện tại
    config_data = get_config(file_name)
    
    # Cập nhật trường
    config_data[field_name] = value
    
    # Ghi lại file
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return config_data
    except IOError as e:
        raise IOError(f"Không thể ghi file '{file_name}': {str(e)}")


def set_config(file_name, config_dict):
    """
    Cập nhật toàn bộ nội dung của file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
        config_dict: Dictionary chứa toàn bộ config mới
    
    Returns:
        dict: Config đã được cập nhật
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        TypeError: Nếu config_dict không phải dictionary
        IOError: Nếu không thể ghi file
    
    Example:
        >>> new_config = {
        ...     "sender": "new@email.com",
        ...     "password": "newpass",
        ...     "receiver": "receiver@email.com"
        ... }
        >>> set_config("mail", new_config)
        {'sender': 'new@email.com', 'password': 'newpass', 'receiver': 'receiver@email.com'}
    """
    if not isinstance(config_dict, dict):
        raise TypeError(f"config_dict phải là dictionary, nhận được: {type(config_dict).__name__}")
    
    config_path = _get_config_path(file_name)
    
    # Ghi lại file
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)
        return config_dict
    except IOError as e:
        raise IOError(f"Không thể ghi file '{file_name}': {str(e)}")


def update_fields(file_name, **fields):
    """
    Cập nhật nhiều trường cùng lúc trong file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
        **fields: Các trường cần cập nhật dưới dạng keyword arguments
    
    Returns:
        dict: Toàn bộ config sau khi cập nhật
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
        IOError: Nếu không thể ghi file
    
    Example:
        >>> update_fields("mail", sender="new@email.com", receiver="receiver@email.com")
        {'sender': 'new@email.com', 'password': '...', 'receiver': 'receiver@email.com'}
    """
    config_path = _get_config_path(file_name)
    
    # Đọc config hiện tại
    config_data = get_config(file_name)
    
    # Cập nhật các trường
    config_data.update(fields)
    
    # Ghi lại file
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return config_data
    except IOError as e:
        raise IOError(f"Không thể ghi file '{file_name}': {str(e)}")


def has_field(file_name, field_name):
    """
    Kiểm tra xem một trường có tồn tại trong file config không
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
        field_name: Tên trường cần kiểm tra
    
    Returns:
        bool: True nếu trường tồn tại, False nếu không
    
    Example:
        >>> has_field("mail", "sender")
        True
        >>> has_field("mail", "nonexistent")
        False
    """
    try:
        config_data = get_config(file_name)
        return field_name in config_data
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def get_all_fields(file_name):
    """
    Lấy danh sách tất cả các trường trong file config
    
    Args:
        file_name: Tên file config (ví dụ: "mail", "pay_ment")
    
    Returns:
        list: Danh sách tên các trường
    
    Example:
        >>> fields = get_all_fields("mail")
        >>> print(fields)
        ['sender', 'password', 'receiver']
    """
    config_data = get_config(file_name)
    return list(config_data.keys())


# Ví dụ sử dụng (có thể test bằng cách chạy file này)
if __name__ == "__main__":
    import sys
    # Đặt encoding UTF-8 cho Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("="*60)
    print("Test module config.py")
    print("="*60)
    
    # Liệt kê các file config
    print("\n1. Danh sach cac file config:")
    configs = list_configs()
    for cfg in configs:
        print(f"   - {cfg}")
    
    # Đọc config mail
    print("\n2. Doc config mail:")
    try:
        mail_config = get_config("mail")
        print(f"   {json.dumps(mail_config, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   Loi: {e}")
    
    # Đọc một trường cụ thể
    print("\n3. Doc truong 'sender' tu mail:")
    try:
        sender = get_field("mail", "sender")
        print(f"   sender: {sender}")
    except Exception as e:
        print(f"   Loi: {e}")
    
    # Kiểm tra trường có tồn tại không
    print("\n4. Kiem tra truong 'sender' co ton tai:")
    print(f"   {has_field('mail', 'sender')}")
    
    # Lấy danh sách tất cả các trường
    print("\n5. Danh sach cac truong trong mail:")
    try:
        fields = get_all_fields("mail")
        print(f"   {fields}")
    except Exception as e:
        print(f"   Loi: {e}")
    
    print("\n" + "="*60)

