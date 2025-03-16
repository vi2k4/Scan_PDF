
import sys
from mysql.connector import Error

from connect import create_connection



print(sys.path)
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

print(fetch_data())

