import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QFont
from PySide6.QtCore import Qt, QFile, QTextStream
from Backend.offline import OfflineWindow
from Backend.online import OnlineWindow


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Load the style sheet
        style_file = QFile("assets/Style/style.qss")
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        self.setStyleSheet(stream.readAll())

        # Load the font file
        font_id = QFontDatabase.addApplicationFont("assets/Font/TitilliumWeb-Bold.ttf")

        if font_id != -1:
            # If the font is loaded successfully, set it as the default application font
            QApplication.instance().setFont(QFont("Titillium Web"))
        else:
            # Fallback to a default font if "Titillium Web" is not available
            QApplication.instance().setFont(QFont("Arial"))

        self.setWindowTitle("IdentiFace")
        self.setFixedSize(500, 200)

        # Set Window Icon
        icon_path = "assets/Icons/favicon-black.png"  # Replace with the actual path to your icon file
        self.setWindowIcon(QIcon(icon_path))

        # Center the window on the screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        layout = QVBoxLayout()

        # Logo QLabel
        logo_label = QLabel(alignment=Qt.AlignCenter)  # Center the logo within the QLabel
        pixmap = QPixmap("assets/Icons/logo.png")
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

        # Buttons
        button_layout = QHBoxLayout()

        online_button = QPushButton("Online")
        online_button.clicked.connect(self.open_online_window)
        button_layout.addWidget(online_button)

        offline_button = QPushButton("Offline")
        offline_button.clicked.connect(self.open_offline_window)
        button_layout.addWidget(offline_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_online_window(self):
        self.online_window = OnlineWindow()
        self.online_window.show()
        self.hide()

    def open_offline_window(self):
        self.offline_window = OfflineWindow()
        self.offline_window.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec())
