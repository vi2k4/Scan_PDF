import sys
import os

import user_data

# Thêm thư mục gốc (PYTHON) vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connect import fetch_data , registedUser, check_email_exists, update_user_password
# print(sys.path)
# from db.userController import fetch_data


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QMessageBox
import subprocess
import smtplib
from email_validator import validate_email, EmailNotValidError
from hash import encrypt_password, decrypt_password




def show_message(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.exec()

def center_window(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move(  
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )


def openForgotPasswordDialog():
        dialog = ForgotPasswordDialog()
        dialog.exec()

def openSignInDialog():
        dialog = SignInDialog()
        dialog.exec()
    
def openChangePassDialog(email , otp):
        dialog = ChangePasswordDialog(email, otp)
        dialog.exec()


class ForgotPasswordDialog(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quên mật khẩu")
        self.setGeometry(700, 400, 300, 200)
        center_window(self)
        self.otp_code = None

        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Nhập email để lấy lại mật khẩu:")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Nhập email của bạn...")
        self.submit_btn = QtWidgets.QPushButton("Gửi yêu cầu")
        
        layout.addWidget(label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.submit_btn)

        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; border-radius: 10px; }
            QLabel { font-size: 14px; font-weight: bold; color: #333; }
            QLineEdit { font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px; background-color: white; }
            QLineEdit:focus { border: 1px solid #0078d7; background-color: #e6f2ff; }
            QPushButton { font-size: 14px; background-color: #0078d7; color: white; border-radius: 5px; padding: 8px; }
            QPushButton:hover { background-color: #005cbf; }
        """)

        self.setLayout(layout)
        self.submit_btn.clicked.connect(self.send_verification_code)

    def send_verification_code(self):
        email = self.email_input.text().strip()

        if not self.is_valid_email(email):
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return

        self.otp_code = str(random.randint(100000, 999999))

        # Gửi email
        if self.send_email(email, self.otp_code):
            QtWidgets.QMessageBox.information(self, "Thành công", "Mã xác nhận đã được gửi! Vui lòng kiểm tra email.")
            openChangePassDialog(email = email, otp = self.otp_code)
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không thể gửi email. Vui lòng thử lại sau!")

    def is_valid_email(self, email):
        try:
            validate_email(email, check_deliverability=True)
            return True
        except EmailNotValidError:
            return False

    def send_email(self, recipient_email, otp_code):
        try:
            sender_email = "vhuynh414@gmail.com"  # Thay bằng email của bạn
            sender_password = "yqlr rgtl eadv acdx"      # Thay bằng mật khẩu ứng dụng của bạn

            # Cấu hình SMTP
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # Tạo nội dung email
            subject = "Mã xác nhận khôi phục mật khẩu"
            body = f"Mã xác nhận của bạn là: {otp_code}\nVui lòng không chia sẻ mã này với ai!"

            # Tạo email
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            # Gửi email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Lỗi gửi email: {e}")
            return False
        
class ChangePasswordDialog(QtWidgets.QDialog):
    def __init__(self, email = None, otp = None):
        super().__init__()
        self.email = email
        self.sentOTP = otp

        self.setWindowTitle("Đổi mật khẩu")
        self.setFixedSize(400, 400)

        # ========== Main Layout ==========
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ========== Tiêu đề ==========
        title_label = QtWidgets.QLabel("Đổi mật khẩu")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        # ========== Form layout ==========
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(15)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        self.email_input.setText(self.email)


        self.otp_input = QtWidgets.QLineEdit()
        self.otp_input.setPlaceholderText("Nhập mã OTP")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu mới")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.re_password_input = QtWidgets.QLineEdit()
        self.re_password_input.setPlaceholderText("Nhập lại mật khẩu")
        self.re_password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("OTP:", self.otp_input)
        form_layout.addRow("Mật khẩu:", self.password_input)
        form_layout.addRow("Xác nhận:", self.re_password_input)

        main_layout.addLayout(form_layout)

        # ========== Nút Submit ==========
        self.submit_btn = QtWidgets.QPushButton("Đổi mật khẩu")
        self.submit_btn.setFixedHeight(40)
        self.submit_btn.setStyleSheet("font-weight: bold;")
        self.submit_btn.clicked.connect(self.changePassword)
        main_layout.addWidget(self.submit_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # ========== Gán layout chính ==========
        self.setLayout(main_layout)

    def checkInput(self):
        fields = {
            "Email": self.email_input.text().strip(),
            "OTP": self.otp_input.text().strip(),
            "Mật khẩu": self.password_input.text().strip(),
            "Nhập lại mật khẩu": self.re_password_input.text().strip(),
        }

        # Kiểm tra xem có trường nào trống không
        for field_name, value in fields.items():
            if not value:
                QtWidgets.QMessageBox.warning(self, "Lỗi", f"{field_name} không được để trống!")
                return False


        if len(fields["Mật khẩu"]) < 6:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return False

        if fields["Mật khẩu"] != fields["Nhập lại mật khẩu"]:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu nhập lại không khớp!")
            return False
        
        if fields["OTP"] != self.sentOTP:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "OTP không chính xác")
            return False
        
        return True

    def changePassword(self):
        if not self.checkInput():
            return

        e = self.email_input.text()
        p = self.password_input.text()
        hashP = encrypt_password(p)
        if update_user_password(e,hashP):
          QtWidgets.QMessageBox.information(self,"Thành công", "Đổi mật khẩu thành công")
          self.close()




class SignInDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.user_info = {
            "username": "",
            "password_hash": "",
            "email": "",
            "role": "",
            "is_active": None
        }

        self.setWindowTitle("Đăng ký tài khoản")
        self.setGeometry(500, 250, 400, 300)

        main_layout = QtWidgets.QHBoxLayout()
        container = QtWidgets.QVBoxLayout()

        container.addWidget(QtWidgets.QLabel("Nhập thông tin đăng ký:", alignment=QtCore.Qt.AlignmentFlag.AlignCenter))

        form_layout = QtWidgets.QFormLayout()
        self.username_input = QtWidgets.QLineEdit()
        self.email_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.re_password_input = QtWidgets.QLineEdit()
        self.re_password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Re-enter Password:", self.re_password_input)

        container.addLayout(form_layout)
        self.submit_btn = QtWidgets.QPushButton("Đăng ký")
        self.submit_btn.setFixedWidth(400)

        self.submit_btn.clicked.connect(self.addUser)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addStretch()
        container.addLayout(btn_layout)

        main_layout.addStretch()
        main_layout.addLayout(container)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def check_input(self):
        fields = {
            "Tên người dùng": self.username_input.text().strip(),
            "Email": self.email_input.text().strip(),
            "Mật khẩu": self.password_input.text().strip(),
            "Nhập lại mật khẩu": self.re_password_input.text().strip(),
        }

        # Kiểm tra xem có trường nào trống không
        for field_name, value in fields.items():
            if not value:
                QtWidgets.QMessageBox.warning(self, "Lỗi", f"{field_name} không được để trống!")
                return False

        email = fields["Email"]
        def is_valid_email(email):
            try:
                validate_email(email, check_deliverability=False)  # Chỉ kiểm tra cú pháp email
                return True
            except EmailNotValidError:
                return False
        if check_email_exists(email): 
            QtWidgets.QMessageBox.warning(None, "Lỗi", "Email này đã được sử dụng!")
            return False


        if not is_valid_email(email):
            QtWidgets.QMessageBox.warning(None, "Lỗi", "Email không hợp lệ hoặc không tồn tại!")
            return False
        
        password = fields["Mật khẩu"]
        re_password = fields["Nhập lại mật khẩu"]

        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return False

        if password != re_password:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu nhập lại không khớp!")
            return False
        QtWidgets.QMessageBox.information(self,"Thành công", "Đăng kí tài khoản thành công")
        return True

   
    def addUser(self):
        if not self.check_input():
            return  

        # Hash mật khẩu
        passAfterCrypt = encrypt_password(self.password_input.text()) 

        self.user_info["email"] = self.email_input.text().strip()
        self.user_info["username"] = self.username_input.text().strip()
        self.user_info["password_hash"] = passAfterCrypt 

        registedUser(self.user_info)
        self.accept()



class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(907, 493)
        MainWindow.setTabletTracking(False)
        MainWindow.setAcceptDrops(False)
        MainWindow.setAutoFillBackground(False)

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")

        self.btn_submit = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_submit.setGeometry(QtCore.QRect(700, 340, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btn_submit.setFont(font)
        self.btn_submit.setObjectName("btn_submit")
        self.btn_submit.clicked.connect(self.checkAccout)


        self.email_lb = QtWidgets.QLabel(parent=self.centralwidget)
        self.email_lb.setGeometry(QtCore.QRect(560, 190, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.email_lb.setFont(font)
        self.email_lb.setObjectName("email_lb")
        self.pass_lb = QtWidgets.QLabel(parent=self.centralwidget)
        self.pass_lb.setGeometry(QtCore.QRect(560, 250, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pass_lb.setFont(font)
        self.pass_lb.setObjectName("pass_lb")
        self.tilte_lb = QtWidgets.QLabel(parent=self.centralwidget)
        self.tilte_lb.setGeometry(QtCore.QRect(550, 40, 321, 51))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.tilte_lb.setFont(font)
        self.tilte_lb.setObjectName("tilte_lb")
        self.login_email = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.login_email.setGeometry(QtCore.QRect(660, 180, 181, 31))
        self.login_email.setText("")
        self.login_email.setObjectName("login_email")
        self.password = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.password.setGeometry(QtCore.QRect(660, 240, 181, 31))
        self.password.setObjectName("password")
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.forget_pass = QtWidgets.QLabel(parent=self.centralwidget)
        self.forget_pass.setGeometry(QtCore.QRect(750, 280, 70, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.forget_pass.setFont(font)
        self.forget_pass.setObjectName("forget_pass")
        self.forget_pass.mousePressEvent = lambda event: openForgotPasswordDialog()

        self.sign_in = QtWidgets.QLabel(parent=self.centralwidget)
        self.sign_in.setGeometry(QtCore.QRect(660, 280, 40, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.sign_in.setFont(font)
        self.sign_in.setAutoFillBackground(False)
        self.sign_in.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.sign_in.setOpenExternalLinks(True)
        self.sign_in.setObjectName("sign_in")
        self.sign_in.mousePressEvent = lambda event: openSignInDialog()

    

        self.graphicsView = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 500, 493 ))
        self.graphicsView.setObjectName("graphicsView")

        # 🔥 Ẩn thanh cuộn (Cú pháp đúng cho PyQt6)
        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Tạo scene và thêm ảnh vào graphicsView
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)


        # Load ảnh vào QPixmap
        pixmap = QtGui.QPixmap("img/1.jpg")  
        transform = QTransform().rotate(-90)  
        pixmap = pixmap.transformed(transform, QtCore.Qt.TransformationMode.SmoothTransformation)

        # Resize ảnh về 500x493
        pixmap = pixmap.scaled(500, 493, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

        if not pixmap.isNull():
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            item.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
            self.scene.addItem(item)
            self.graphicsView.setSceneRect(item.boundingRect())

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 907, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()




    def checkAccout(self):
        try:
            print("Hàm checkAccout được gọi!") 
            email = self.login_email.text().strip()
            password = self.password.text().strip()

            if not email or not password: 
                self.show_message("Lỗi", "Vui lòng nhập email và mật khẩu!")
                return

            key = b"ljlJeB1u3Yyh8tYYYAObAevf5-nbv5qZz0_sPihFll8="
            list = fetch_data()
            found = False
            for user in list:
                stored_email = user[3]
                stored_password = user[2]
                real_password = decrypt_password( stored_password)
                if stored_email == email and real_password == password:
                    found = True
                    user_data.set_current_user(user[0])
                    break

            if found:
                self.show_message("Thành công", "Đăng nhập thành công!")
                subprocess.Popen([sys.executable, "src/menu.py", str(user_data.get_current_user())])
                MainWindow.hide()
            else:
                self.show_message("Lỗi", "Email hoặc mật khẩu không chính xác!")

        except Exception as e:
            print(f"Lỗi xảy ra: {e}") 
            self.show_message("Lỗi", f"Có lỗi xảy ra: {e}")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_submit.setText(_translate("MainWindow", "LOGIN"))
        self.email_lb.setText(_translate("MainWindow", "Email :"))
        self.pass_lb.setText(_translate("MainWindow", "Mật khẩu :"))
        self.tilte_lb.setText(_translate("MainWindow", "Welcome To My App"))
        self.forget_pass.setText(_translate("MainWindow", "Quên mật khẩu ?"))
        self.sign_in.setText(_translate("MainWindow", "Sign in"))

   





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    
    # 🔥 Đặt style sau khi setup UI
    MainWindow.setStyleSheet("""
        QLineEdit {
            color: black;
            border: 2px solid gray;  
            border-radius: 5px;
            padding: 5px;
            font-weight : bold;
        }
        QPushButton {
            background-color: lightgray;
            border-radius: 5px;
            padding: 5px;
            font-weight : bold;
        }
                             
        QPushButton:hover {
            background-color: #0078d7;
        }
        QLabel {
            font-weight : bold;
        }

        QLabel#forget_pass {
            color: red;  
            font-weight: bold; 
            text-decoration : underline
        }
                             
        QLabel#sign_in {
            color: blue;  
            font-weight: bold;
            text-decoration : underline
                             
        }
    """)


  
    MainWindow.show()
    sys.exit(app.exec())
