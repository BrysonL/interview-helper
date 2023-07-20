from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import QColor, QPainter, QGuiApplication
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
import sys


class Teleprompter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        
        self.app = QApplication(sys.argv)
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() // 2 - self.width() // 2, 0, self.width(), self.height())  # Move window to the top center of the screen

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.label = QLabel()
        self.label.setStyleSheet(
            "color: dark-green; font-size: 24px; qproperty-alignment: AlignCenter; background-color: rgba(0, 0, 0, 0);"
        )  # Updated style sheet
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

        self.show()
        self.update_text("Hello world!")

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

    def start_scrolling(self, text, words_per_minute=250):
        self.scroll_thread = threading.Thread(
            target=self._timed_update, args=(text, words_per_minute)
        )
        self.scroll_thread.start()

    def _timed_update(self, text, words_per_minute):
        words = text.split()
        num_words = len(words)
        time_per_word = 60 / words_per_minute
        punctuation_delay = time_per_word * 1.5

        for index in range(num_words + 1):
            new_text = self._bold_one_word_at_a_time(text, index)
            QMetaObject.invokeMethod(
                self,
                "update_text",
                Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, new_text),
            )
            current_word = words[index] if index < num_words else ""
            if current_word.endswith((".", ",", ";", ":", "?", "!")):
                time.sleep(punctuation_delay)
            else:
                adjusted_speed = self._adjust_speed_based_on_word_length(
                    current_word, time_per_word, 0.15
                )
                time.sleep(adjusted_speed)

    @staticmethod
    def _bold_one_word_at_a_time(text, index):
        words = text.split()
        if index < len(words):
            words[index] = f"<b>{words[index]}</b>"
        else:
            return ""  # Return an empty string when the index is out of range
        return " ".join(words[max(0, index - 2) : index + 3])

    @staticmethod
    def _adjust_speed_based_on_word_length(word, base_speed, multiplier):
        adjusted_speed = base_speed * max(
            len(word) * multiplier, 0.5
        )  # Ensure a minimum speed
        return adjusted_speed
