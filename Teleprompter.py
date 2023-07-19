from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import QColor, QPainter, QGuiApplication
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class Teleprompter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.label = QLabel()
        self.label.setStyleSheet("color: dark-green; font-size: 24px; qproperty-alignment: AlignCenter; background-color: rgba(0, 0, 0, 0);")  # Updated style sheet
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.mouse_down = False
        self.offset = QPoint()

        screen = QGuiApplication.primaryScreen().geometry()
        width = screen.width() * 0.3
        height = screen.height() * 0.1
        self.label.setFixedWidth(width)
        self.label.setFixedHeight(height)
        self.label.setWordWrap(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0)  # Adjust the background opacity (0-1)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = self.frameSize()
        x = (screen.width() - window_size.width()) // 2
        self.move(x, 0)

    @pyqtSlot(str)
    def update_text(self, text):
        self.label.setText(text)
        self.label.adjustSize()  # Adjust the QLabel size to fit the text
        self.adjustSize()  # Adjust the window size to fit the QLabel
        self.center_window()  # Center the window at the top of the screen
        self.repaint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_down = True
            self.offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.mouse_down and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_down = False
            event.accept()