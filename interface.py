from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Video")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.register_button = QPushButton("Register User")
        self.register_button.clicked.connect(self.register_user)

        self.check_users_button = QPushButton("Check Registered Users")
        self.check_users_button.clicked.connect(self.check_users)

        self.delete_user_button = QPushButton("Delete User")
        self.delete_user_button.clicked.connect(self.delete_user)

        self.search_user_button = QPushButton("Search User")
        self.search_user_button.clicked.connect(self.search_user)

        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.check_users_button)
        self.layout.addWidget(self.delete_user_button)
        self.layout.addWidget(self.search_user_button)

    def register_user(self):
        # Add your user registration logic here
        pass

    def check_users(self):
        # Add your logic to check registered users here
        pass

    def delete_user(self):
        # Add your user deletion logic here
        pass

    def search_user(self):
        # Add your user search logic here
        pass

def main():
    app = QApplication([])
    gui = ServerGUI()
    gui.show()
    app.exec_()

if __name__ == "__main__":
    main()