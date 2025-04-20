import mysql.connector
from db.connect import create_connection  # đảm bảo hàm get_connection đã có trong connect.py

def insert_document(user_id, title, original_file_path, status, created_at):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO documents (user_id, title, original_file_path, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, title, original_file_path, status, created_at))
        conn.commit()
        cursor.close()
        conn.close()
        print("Đã lưu thông tin tài liệu PDF vào cơ sở dữ liệu.")
    except mysql.connector.Error as err:
        print("Lỗi khi lưu thông tin PDF:", err)
