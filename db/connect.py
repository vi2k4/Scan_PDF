import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='my_scanner_db',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Kết nối thành công!")
            return connection
    except Error as e:
        print(f"Lỗi kết nối: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Đã đóng kết nối.")


def fetch_data():
    cursor = None
    connection = create_connection()
    data_list = []  # Khởi tạo trước

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users")
            data_list = cursor.fetchall()

        except Error as e:
            print(f"Lỗi truy vấn: {e}")
        finally:
            if cursor:
                cursor.close()
            connection.close()
            print("Đã đóng kết nối.")

    return data_list


def registedUser(user):
    connection = create_connection()
    if not connection:
        print("Không thể kết nối database.")
    try:
        cursor = connection.cursor()
        sql = """INSERT INTO users (username, password_hash, email, created_at)
         VALUES (%s, %s, %s, NOW())"""

        values = (user["username"], user["password_hash"], user["email"])

        cursor.execute(sql, values)
        connection.commit()
        print("Đăng ký thành công!")
        return True

    except Error as e:
        print(f"Lỗi truy vấn: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Đã đóng kết nối.")


def check_email_exists(email):
    connection = create_connection()
    if not connection:
        print("Không thể kết nối database.")
        return False 

    try:
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM users WHERE email = %s"
        cursor.execute(sql, (email,))
        count = cursor.fetchone()[0]
        return count > 0  # Trả về True nếu email tồn tại, ngược lại False

    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Đã đóng kết nối.")

def update_user_password(email, new_password_hash):
    connection = create_connection()
    if not connection:
        print("Không thể kết nối database.")
        return False

    try:
        cursor = connection.cursor()
        sql = "UPDATE users SET password_hash = %s WHERE email = %s"
        values = (new_password_hash, email)
        cursor.execute(sql, values)
        connection.commit()

        if cursor.rowcount > 0:
            print("Cập nhật mật khẩu thành công!")
            return True
        else:
            print("Không tìm thấy người dùng với email này.")
            return False

    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Đã đóng kết nối.")