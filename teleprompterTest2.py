import sys
import threading
import time
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class TransparentBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.label = QLabel()
        self.label.setStyleSheet("color: white")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.mouse_down = False
        self.offset = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0)  # Adjust the background opacity (0-1)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

    def update_text(self, text):
        self.label.setText(text)

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

def some_function():
    return "New text from function"

def update_text_in_window(window):
    time.sleep(5)
    new_text = some_function()
    while new_text != "exit()":
        formatted_text = f"<b>{new_text}</b> is now <i>updated</i>"
        window.update_text(formatted_text)
        new_text = input("new text:")

def create_window_with_transparent_background(text):
    app = QApplication(sys.argv)
    window = TransparentBackground()
    formatted_text = f"<b>{text}</b> is the <i>initial</i> text"
    window.update_text(formatted_text)

    # Run the update_text_in_window function in a separate thread
    update_thread = threading.Thread(target=update_text_in_window, args=(window,))
    update_thread.start()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    text = "Sample text"
    create_window_with_transparent_background(text)