"""
Module xử lý API cho config
Cung cấp các hàm xử lý request/response cho các endpoint config
"""

from apis.config import (
    list_configs,
    get_config,
    get_field,
    set_field,
    set_config,
    update_fields,
    has_field,
    get_all_fields
)


def handle_list_configs():
    """
    Xử lý request lấy danh sách tất cả config
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        configs = list_configs()
        return True, {
            "configs": configs,
            "count": len(configs)
        }, 200, "Lấy danh sách config thành công"
    except Exception as e:
        return False, None, 500, f"Lỗi khi lấy danh sách config: {str(e)}"


def handle_get_config(file_name):
    """
    Xử lý request lấy toàn bộ config của một file
    
    Args:
        file_name: Tên file config (không có đuôi .json)
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        config_data = get_config(file_name)
        return True, {
            "file_name": file_name,
            "config": config_data
        }, 200, f"Lấy config '{file_name}' thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi lấy config: {str(e)}"


def handle_get_field(file_name, field_name):
    """
    Xử lý request lấy một trường cụ thể từ config
    
    Args:
        file_name: Tên file config (không có đuôi .json)
        field_name: Tên trường cần lấy
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        if not has_field(file_name, field_name):
            return False, None, 404, f"Trường '{field_name}' không tồn tại trong config '{file_name}'"
        
        field_value = get_field(file_name, field_name)
        return True, {
            "file_name": file_name,
            "field_name": field_name,
            "value": field_value
        }, 200, f"Lấy trường '{field_name}' thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi lấy trường: {str(e)}"


def handle_set_field(file_name, field_name, value):
    """
    Xử lý request cập nhật một trường trong config
    
    Args:
        file_name: Tên file config (không có đuôi .json)
        field_name: Tên trường cần cập nhật
        value: Giá trị mới
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        set_field(file_name, field_name, value)
        updated_value = get_field(file_name, field_name)
        return True, {
            "file_name": file_name,
            "field_name": field_name,
            "value": updated_value
        }, 200, f"Cập nhật trường '{field_name}' thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi cập nhật trường: {str(e)}"


def handle_set_config(file_name, config_dict):
    """
    Xử lý request cập nhật toàn bộ config
    
    Args:
        file_name: Tên file config (không có đuôi .json)
        config_dict: Dictionary chứa toàn bộ config mới
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        if not isinstance(config_dict, dict):
            return False, None, 400, "Config phải là một dictionary"
        
        set_config(file_name, config_dict)
        updated_config = get_config(file_name)
        return True, {
            "file_name": file_name,
            "config": updated_config
        }, 200, f"Cập nhật config '{file_name}' thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi cập nhật config: {str(e)}"


def handle_update_fields(file_name, fields_dict):
    """
    Xử lý request cập nhật nhiều trường cùng lúc
    
    Args:
        file_name: Tên file config (không có đuôi .json)
        fields_dict: Dictionary chứa các trường cần cập nhật
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        if not isinstance(fields_dict, dict):
            return False, None, 400, "Fields phải là một dictionary"
        
        update_fields(file_name, **fields_dict)
        updated_config = get_config(file_name)
        return True, {
            "file_name": file_name,
            "updated_fields": list(fields_dict.keys()),
            "config": updated_config
        }, 200, f"Cập nhật các trường thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi cập nhật các trường: {str(e)}"


def handle_get_all_fields(file_name):
    """
    Xử lý request lấy danh sách tất cả các trường trong config
    
    Args:
        file_name: Tên file config (không có đuôi .json)
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int, message: str)
    """
    try:
        fields = get_all_fields(file_name)
        config_data = get_config(file_name)
        return True, {
            "file_name": file_name,
            "fields": fields,
            "config": config_data
        }, 200, f"Lấy danh sách trường thành công"
    except FileNotFoundError as e:
        return False, None, 404, str(e)
    except Exception as e:
        return False, None, 500, f"Lỗi khi lấy danh sách trường: {str(e)}"

