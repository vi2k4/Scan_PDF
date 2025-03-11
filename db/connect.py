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
    connection = create_connection()
    data_list = []  # Tạo danh sách để lưu dữ liệu

    if connection:
        try:
            cursor = connection.cursor()  # Không dùng dictionary=True
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            # Lưu dữ liệu vào danh sách (chỉ lấy giá trị, không lấy tên cột)
            data_list = [list(row) for row in results]

        except Error as e:
            print(f"Lỗi truy vấn: {e}")
        finally:
            cursor.close()
            connection.close()
            print("Đã đóng kết nối.")

    return data_list

# Gọi hàm và kiểm tra kết quả
users_data = fetch_data()
for user in users_data:
    print(user)  # Chỉ hiển thị danh sách các giá trị

