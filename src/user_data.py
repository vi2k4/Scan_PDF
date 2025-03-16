# session_manager.py

current_user_id = None

def login(user_id):
    global current_user_id
    current_user_id = user_id
    print(f"Đăng nhập user_id = {current_user_id}")

def logout():
    global current_user_id
    print(f"User {current_user_id} đã đăng xuất.")
    current_user_id = None

def is_logged_in():
    return current_user_id is not None
