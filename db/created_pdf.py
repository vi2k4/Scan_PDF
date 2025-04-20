import mysql.connector
from db.connect import create_connection  # Đảm bảo hàm create_connection đã có trong connect.py

def insert_document(user_id, title, original_file_path, converted_file_path, status, created_at):
    try:
        conn = create_connection()
        if conn is None:
            print("ERROR: Không thể kết nối cơ sở dữ liệu.")
            return
        
        cursor = conn.cursor()
        query = """
            INSERT INTO documents (user_id, title, original_file_path, converted_file_path, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, title, original_file_path, converted_file_path, status, created_at))
        conn.commit()
        print("Đã lưu thông tin tài liệu PDF vào cơ sở dữ liệu.")
    except mysql.connector.Error as err:
        print("Lỗi khi lưu thông tin PDF:", err)
        raise  # Ném lại lỗi để caller có thể xử lý
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()