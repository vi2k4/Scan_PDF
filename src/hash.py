from cryptography.fernet import Fernet

# Tạo một khóa bí mật duy nhất (chạy 1 lần và lưu lại)
def generate_key():
    return Fernet.generate_key()

key = b"ljlJeB1u3Yyh8tYYYAObAevf5-nbv5qZz0_sPihFll8="


# Hàm mã hóa mật khẩu
def encrypt_password(password: str) -> str:
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()

# Hàm giải mã mật khẩu
def decrypt_password(encrypted_password: str) -> str:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()

