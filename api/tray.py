import pystray
from PIL import Image
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Window controls (traffic lights)
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create buttons with symbols
        self.close_btn = QPushButton("✕")
        self.minimize_btn = QPushButton("−")
        self.maximize_btn = QPushButton("⧉")
        
        # Set object names for specific styling
        self.close_btn.setObjectName("closeButton")
        self.minimize_btn.setObjectName("minimizeButton")
        self.maximize_btn.setObjectName("maximizeButton")
        
        for btn in [self.close_btn, self.minimize_btn, self.maximize_btn]:
            btn.setFixedSize(12, 12)
            btn.setFont(QFont('Arial', 8))  # Smaller font for symbols
            controls_layout.setAlignment(Qt.AlignTop)
            controls_layout.addWidget(btn)
        
        # Title in center
        title = QLabel("Add Knowledge")
        title.setObjectName("windowTitle")
        layout.addWidget(controls, alignment=Qt.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignCenter)
        title.setFont(QFont('Arial', 13, QFont.Bold))
        
        layout.addWidget(controls)
        layout.addWidget(title)
        layout.addStretch(1)  # For symmetry

        # In the CleanWindow class, update the stylesheet to include:
        self.setStyleSheet("""
            QWidget#background {
                background: rgba(248, 248, 248, 0.95);
                border-radius: 10px;
                border: 1px solid #E5E5E5;
            }
            
            QLabel#windowTitle {
                color: #333333;
                font-size: 13px;
            }
            
            QPushButton#addButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: medium;
            }
            
            QPushButton#addButton:hover {
                background: #0066CC;
            }
            
            /* Traffic light buttons */
            #closeButton, #minimizeButton, #maximizeButton {
                border-radius: 6px;
                border: none;
                color: transparent;
                text-align: center;
            }
            
            #closeButton { background: #FF5F57; }
            #minimizeButton { background: #FEBC2E; }
            #maximizeButton { background: #28C840; }
            
            #closeButton:hover {
                background: #FF5F57;
                color: #4D0000;
            }
            
            #minimizeButton:hover {
                background: #FEBC2E;
                color: #995700;
            }
            
            #maximizeButton:hover {
                background: #28C840;
                color: #0A3B00;
            }
        """)

class CleanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("border-radius: 10px;")

        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)

        # Background widget with rounded corners
        background = QWidget()
        background.setObjectName("background")
        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)

        # Custom title bar
        title_bar = TitleBar(self)
        title_bar.close_btn.clicked.connect(self.close)
        title_bar.minimize_btn.clicked.connect(self.showMinimized)
        title_bar.maximize_btn.clicked.connect(self.toggleMaximized)

        # Content area with centered button
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignCenter)
        
        add_btn = QPushButton("Add Knowledge")
        add_btn.setObjectName("addButton")
        add_btn.setFixedSize(200, 50)
        content_layout.addWidget(add_btn)

        # Add everything to main layout
        bg_layout.addWidget(title_bar)
        bg_layout.addWidget(content)
        layout.addWidget(background)

        # Apply styles
        self.setStyleSheet("""
            QWidget#background {
                background: rgba(248, 248, 248, 0.95);
                border-radius: 10px;
                border: 1px solid #E5E5E5;
            }
            
            QLabel#windowTitle {
                color: #333333;
                font-size: 13px;
            }
            
            QPushButton#addButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: medium;
            }
            
            QPushButton#addButton:hover {
                background: #0066CC;
            }
            
            /* Traffic light buttons */
            QPushButton {
                border-radius: 6px;
                border: none;
            }
            
            TitleBar > QWidget > QPushButton:nth-child(1) {  /* Close */
                background: #FF5F57;
            }
            
            TitleBar > QWidget > QPushButton:nth-child(2) {  /* Minimize */
                background: #FEBC2E;
            }
            
            TitleBar > QWidget > QPushButton:nth-child(3) {  /* Maximize */
                background: #28C840;
            }
            
            TitleBar > QWidget > QPushButton:hover {
                opacity: 0.8;
            }
        """)
        
        self.center()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

    def toggleMaximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = None
        
        # Create tray icon
        image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        for x in range(32):
            for y in range(32):
                if 8 <= x < 24 and 8 <= y < 24:
                    image.putpixel((x, y), (255, 255, 255, 255))

        menu = pystray.Menu(
            pystray.MenuItem("Add Knowledge", self.show_window),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.icon = pystray.Icon("CodeKnowledge", image, "Code Knowledge", menu)
        
    def show_window(self):
        if self.window is None:
            self.window = CleanWindow()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        
    def quit_app(self):
        self.icon.stop()
        self.app.quit()
        
    def run(self):
        self.icon.run_detached()
        self.app.exec()

if __name__ == '__main__':
    app = Application()
    app.run()