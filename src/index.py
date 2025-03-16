import sys
import os

# Thêm thư mục gốc (PYTHON) vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connect import fetch_data , registedUser, check_email_exists
print(sys.path)
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
import user_data



def set_current_user(user_id):
    user_data.current_user_id = user_id


def center_window(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move(  
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )


def show_message(title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()


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
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; border-radius: 10px; }
            QLabel { font-size: 14px; font-weight: bold; color: #333; }
            QLineEdit { font-size: 14px; padding: 5px; border: 1px solid #ccc; border-radius: 5px; background-color: white; }
            QLineEdit:focus { border: 1px solid #0078d7; background-color: #e6f2ff; }
            QPushButton { font-size: 14px; background-color: #0078d7; color: white; border-radius: 5px; padding: 8px; }
            QPushButton:hover { background-color: #005cbf; }
        """)
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

        if not is_valid_email(email):
            QtWidgets.QMessageBox.warning(None, "Lỗi", "Email không hợp lệ hoặc không tồn tại!")
            return False
        

        if check_email_exists(email):
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Email này đã được sử dụng!")
            return False

        password = fields["Mật khẩu"]
        re_password = fields["Nhập lại mật khẩu"]

        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return False

        if password != re_password:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Mật khẩu nhập lại không khớp!")
            return False

        return True

   
    def addUser(self):
        if not self.check_input():
            return  

        self.user_info["email"] = self.email_input.text().strip()
        self.user_info["username"] = self.username_input.text().strip()
        self.user_info["password_hash"] = self.password_input.text()  # Cần hash mật khẩu

        print("Đăng ký thành công!")
        show_message("Thành công", "Đăng kí thành công!")
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
        self.forget_pass.mousePressEvent = self.openForgotPasswordDialog 

        self.sign_in = QtWidgets.QLabel(parent=self.centralwidget)
        self.sign_in.setGeometry(QtCore.QRect(660, 280, 40, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.sign_in.setFont(font)
        self.sign_in.setAutoFillBackground(False)
        self.sign_in.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.sign_in.setOpenExternalLinks(True)
        self.sign_in.setObjectName("sign_in")
        self.sign_in.mousePressEvent = self.openSignInDialog  

    

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



    



    def checkAccout(self):
        try:
            print("Hàm checkAccout được gọi!") 
            email = self.login_email.text().strip()
            password = self.password.text().strip()

            if not email or not password: 
                show_message("Lỗi", "Vui lòng nhập email và mật khẩu!")
                return

            try:
                list = fetch_data()
                if list is None:
                    raise Exception("Không lấy được dữ liệu từ database!")
                print("Dữ liệu lấy từ DB:", list)
            except Exception as e:
                print(f"Lỗi khi truy vấn dữ liệu: {e}")
                show_message("Lỗi", f"Lỗi khi truy vấn dữ liệu: {e}")
                return 

            found = False
            for user in list:
                stored_email = user[3]  
                stored_password = user[2] 

                if stored_email == email and stored_password == password:
                    found = True

                    user_data.current_user_id = user[0]
                    print(user_data.current_user_id)
                    set_current_user(user[0])  # Lưu ID
                    break  
            
            if found:
                show_message("Thành công", "Đăng nhập thành công!")

                # Dùng sys.executable để đảm bảo chạy đúng Python
                subprocess.Popen([sys.executable, "menu.py"])

                MainWindow.hide()
                # QtWidgets.QApplication.quit()
            else:
                show_message("Lỗi", "Email hoặc mật khẩu không chính xác!")

        except Exception as e:
            print(f"Lỗi xảy ra: {e}") 
            show_message("Lỗi", f"Có lỗi xảy ra: {e}")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_submit.setText(_translate("MainWindow", "LOGIN"))
        self.email_lb.setText(_translate("MainWindow", "Email :"))
        self.pass_lb.setText(_translate("MainWindow", "Mật khẩu :"))
        self.tilte_lb.setText(_translate("MainWindow", "Welcome To My App"))
        self.forget_pass.setText(_translate("MainWindow", "Quên mật khẩu ?"))
        self.sign_in.setText(_translate("MainWindow", "Sign in"))

    def openForgotPasswordDialog(self, event):
        dialog = ForgotPasswordDialog()
        dialog.exec()

    def openSignInDialog(self, event):
        dialog = SignInDialog()
        dialog.exec()


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
