# session_manager.py

current_user_id = None

def set_current_user(user_id):
    global current_user_id
    current_user_id = user_id
    print(f"DEBUG: current_user_id đã được set là {current_user_id}")  # Thêm dòng debug này


def get_current_user():
    return current_user_id