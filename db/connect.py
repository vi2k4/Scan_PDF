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

# Gọi hàm để tránh cảnh báo của Pylance
if __name__ == "__main__":
    users = fetch_data()
    print(users)
