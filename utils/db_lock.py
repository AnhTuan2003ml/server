"""
Module quản lý lock cho database operations
Đảm bảo các request được xử lý tuần tự để tránh race condition
"""
import threading
from functools import wraps

# Tạo một lock toàn cục cho database operations
db_lock = threading.Lock()


def with_db_lock(func):
    """
    Decorator để đảm bảo function chỉ được thực thi khi có lock
    
    Usage:
        @with_db_lock
        def my_function():
            # Code xử lý database
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Chờ để lấy lock
        db_lock.acquire()
        try:
            # Thực thi function
            return func(*args, **kwargs)
        finally:
            # Luôn giải phóng lock
            db_lock.release()
    
    return wrapper

