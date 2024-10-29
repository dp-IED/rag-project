from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class CleanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Knowledge")
        self.setMinimumSize(800, 500)
        
        # Remove default window frame for custom one
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout with rounded white background
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom window chrome (title bar area)
        chrome = QWidget()
        chrome.setObjectName("chrome")
        chrome_layout = QHBoxLayout(chrome)
        title = QLabel("Code Knowledge")
        title.setObjectName("title")
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.close)
        chrome_layout.addWidget(title)
        chrome_layout.addStretch()
        chrome_layout.addWidget(close_btn)
        
        layout.addWidget(chrome)
        
        # Content area
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        
        # Big friendly button
        add_btn = QPushButton("Add Knowledge")
        add_btn.setObjectName("bigButton")
        content_layout.addWidget(add_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(content)

        # Apply custom styles
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
            QWidget#chrome {
                background: #f8f8f8;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px;
            }
            QLabel#title {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton#closeButton {
                border: none;
                font-size: 18px;
                color: #666;
            }
            QPushButton#closeButton:hover {
                color: #000;
            }
            QWidget#content {
                background: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                padding: 20px;
            }
            QPushButton#bigButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 15px 30px;
                font-size: 16px;
            }
            QPushButton#bigButton:hover {
                background: #0066CC;
            }
        """)
        
        # Center on screen
        self.center()
        
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)

app = QApplication([])
window = CleanWindow()
window.show()
app.exec()