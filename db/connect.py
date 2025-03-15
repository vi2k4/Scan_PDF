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
