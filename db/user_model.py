# user_model.py
import mysql.connector
from mysql.connector import Error
import hashlib
from db.connect import create_connection


def connect_db():
    """Kết nối đến MySQL, trả về đối tượng connection hoặc None nếu lỗi."""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="my_scanner_db"
        )
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None


def hash_password(password: str) -> str:
    """Hàm băm mật khẩu (SHA256)."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_all_users():
    """
    Lấy tất cả user từ bảng `users`.
    Trả về danh sách các tuple (user_id, username, password_hash, email, role, is_active, created_at, ...)
    hoặc None nếu lỗi.
    """
    conn = connect_db()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"Lỗi database: {e}")
        return None
    
def get_role_user_by_id(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT role FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        data =  cursor.fetchone()[0]
        return data
    except Error as e:
        print ("Error: {e}")
        return
    finally:
        if (cursor):
            cursor.close()
        if (conn):
            conn.close()
        
        
        


def search_users_by_username(username_substring: str):
    """
    Tìm user theo username LIKE '%username_substring%'.
    Trả về danh sách tuple hoặc None nếu lỗi.
    """
    conn = connect_db()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username LIKE %s"
        param = ("%" + username_substring + "%", )
        cursor.execute(query, param)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print(f"Lỗi database: {e}")
        return None


def insert_user(username: str, email: str, password: str, role: str = "USER", is_active: int = 1):
    """
    Thêm một user mới vào bảng `users`.
    """
    conn = connect_db()
    if not conn:
        return False  # Thất bại do không kết nối

    try:
        cursor = conn.cursor()
        # Kiểm tra email đã tồn tại chưa
        cursor.execute("SELECT COUNT(*) FROM users WHERE email=%s", (email,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            conn.close()
            return "EMAIL_EXISTS"

        # Chèn user
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, email, password, role, is_active)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True  # Thành công
    except Error as e:
        print(f"Lỗi database: {e}")
        return False


def update_user(user_id: int, new_username: str, new_email: str, new_password: str = None):
    """
    Cập nhật thông tin user. Nếu new_password=None, chỉ cập nhật username, email.
    Ngược lại, cập nhật cả password_hash.
    """
    conn = connect_db()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # Kiểm tra email mới (nếu thay đổi) có bị trùng không
        cursor.execute("SELECT COUNT(*) FROM users WHERE email=%s AND user_id!=%s", (new_email, user_id))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            conn.close()
            return "EMAIL_EXISTS"

        # Thực hiện UPDATE
        if new_password:  # đổi luôn mật khẩu
            cursor.execute(
                """
                UPDATE users
                SET username=%s, email=%s, password_hash=%s
                WHERE user_id=%s
                """,
                (new_username, new_email, new_password, user_id)
            )
        else:  # chỉ đổi username, email
            cursor.execute(
                """
                UPDATE users
                SET username=%s, email=%s
                WHERE user_id=%s
                """,
                (new_username, new_email, user_id)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Lỗi database: {e}")
        return False


def delete_user(user_id: int):
    """
    Xóa user theo user_id.
    """
    conn = connect_db()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Lỗi database: {e}")
        return False
