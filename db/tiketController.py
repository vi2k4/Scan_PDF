import datetime
import mysql.connector
from mysql.connector import Error
from db.connect import create_connection

# --- Lấy danh sách phản hồi của user ---
def fetch_data_tiket_replies(user_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tickets WHERE user_id = %s", (user_id,))
        data_list = cursor.fetchall()
        return data_list
    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Đã đóng kết nối.")

# --- Lấy tất cả ticket ---
def fetch_data_tiket():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tickets")
        data_list = cursor.fetchall()
        return data_list
    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Đã đóng kết nối.")
            
def ticket_reply(ticket_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM ticket_replies WHERE ticket_id = %s", (ticket_id,))
        data = cursor.fetchall()
        return data
    except Error as e:
        print("Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

# --- Tạo ticket mới ---
def create_tiket(user_id, title, content):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tickets (user_id, title, description, status, created_at) VALUES (%s, %s, %s, %s, %s)",
            (user_id, title, content, "Chờ phản hồi", datetime.datetime.now())
        )
        connection.commit()
        return True
    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Đã đóng kết nối.")

# --- Tạo phản hồi cho ticket ---
def create_tiket_replies(ticket_id, user_id, content):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ticket_replies (ticket_id, user_id, content, created_at) VALUES (%s, %s, %s, %s)",
            (ticket_id, user_id, content, datetime.datetime.now())
        )
        connection.commit()

        # Cập nhật trạng thái ticket
        cursor.execute("""
            UPDATE tickets
            SET status = %s
            WHERE ticket_id = %s
        """, ("Đã phản hồi", ticket_id))
        connection.commit()
        return True
    except Error as e:
        print(f"Lỗi truy vấn: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Đã đóng kết nối.")

# --- Xóa ticket (có kiểm tra quyền) ---
def delete_ticket(ticket_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Kiểm tra phản hồi
        cursor.execute("SELECT * FROM ticket_replies WHERE ticket_id = %s", (ticket_id,))
        replies = cursor.fetchall()
        if replies:
            print("Không thể xóa ticket đã có phản hồi!")
            return False

        # Chỉ xóa nếu trạng thái là 'Chờ phản hồi'
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s AND status = 'Chờ phản hồi'", (ticket_id,))
        ticket = cursor.fetchone()
        if ticket:
            cursor.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))
            conn.commit()
            print("Ticket đã được xóa!")
            return True
        else:
            print("Ticket không tồn tại hoặc không thể xóa vì đã được xử lý.")
            return False
    except Error as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Xóa reply (chỉ admin) ---
def delete_ticket_reply(ticket_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_replies WHERE ticket_id = %s", (ticket_id,))
        reply = cursor.fetchone()
        if not reply:
            print("Reply không tồn tại.")
            return False
        # if user_id != "1":
        #     print("Chỉ admin mới có quyền xóa reply!")
        #     return False

        cursor.execute("DELETE FROM ticket_replies WHERE ticket_id = %s", (ticket_id,))
        conn.commit()
        print("Reply đã được xóa!")
        return True
    except Error as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Sửa ticket (chỉ khi chưa phản hồi) ---
def update_ticket(ticket_id, title, description, status):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if status != "Chờ phản hồi":
            print("Ticket đã được phản hồi nên không thể sửa.")
            return False

        sql = """
            UPDATE tickets
            SET title = %s, description = %s, status = %s, created_at = %s
            WHERE ticket_id = %s
        """
        values = (title, description, status, datetime.datetime.now(), ticket_id)
        cursor.execute(sql, values)
        conn.commit()
        print("Ticket đã được cập nhật thành công!")
        return True
    except Error as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Sửa reply (chỉ nội dung và thời gian) ---
def update_ticket_reply(ticket_id, user_id, content):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE ticket_replies
            SET content = %s, created_at = %s
            WHERE user_id = %s AND ticket_id = %s
        """
        values = (content, datetime.datetime.now(), user_id, ticket_id)
        cursor.execute(sql, values)
        conn.commit()
        print("Reply ticket đã được cập nhật thành công!")
        return True
    except Error as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
