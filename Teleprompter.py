import threading
import time
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QMetaObject
from PyQt6.QtGui import QColor, QPainter, QGuiApplication
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
import sys


class Teleprompter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)

        # Move window to the top center of the screen
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 2 - self.width() // 2, 0, self.width(), self.height()
        )

        # Make the window transparent
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

        # Set the child label (window) size to 30% of the screen width and 10% of the screen height
        width = screen.width() * 0.3
        height = screen.height() * 0.1
        self.label.setFixedWidth(width)
        self.label.setFixedHeight(height)
        self.label.setWordWrap(True)

        # Set scrolling control variables
        self.scroll_state = 'stop'  # or 'play' or 'reverse'
        self.current_index = 0  # the current word being displayed

        # Display the window
        self.show()
        self.start_scrolling("Hello world! Here's a test of the teleprompter that is more than a few words long.")

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
        print("start_scrolling called")
        self.text = text
        self.words_per_minute = words_per_minute
        self.words = self.text.split()
        self.num_words = len(self.words)
        self.time_per_word = 60 / self.words_per_minute
        self.punctuation_delay = 1.5

        self.scroll_thread = threading.Thread(target=self._timed_update)
        self.scroll_thread.start()
        print("start_scrolling finished")

    def _timed_update(self):
        while True:
            if self.scroll_state == "play":
                if self.current_index < self.num_words:
                    new_text = self._bold_one_word_at_a_time(
                        self.text, self.current_index
                    )
                    print(new_text)
                    QMetaObject.invokeMethod(
                        self,
                        "update_text",
                        Qt.ConnectionType.QueuedConnection,
                        QtCore.Q_ARG(str, new_text),
                    )
                    current_word = self.words[self.current_index]
                    adjusted_speed = self._adjust_speed_based_on_word_length(
                        current_word, self.time_per_word, 0.15
                    )
                    if current_word.endswith((".", ",", ";", ":", "?", "!")):
                        time.sleep(adjusted_speed * self.punctuation_delay)
                    else:
                        time.sleep(adjusted_speed)
                    self.current_index += 1
            elif self.scroll_state == "reverse":
                if self.current_index > 0:
                    self.current_index -= 1
                    new_text = self._bold_one_word_at_a_time(
                        self.text, self.current_index
                    )
                    QMetaObject.invokeMethod(
                        self,
                        "update_text",
                        Qt.ConnectionType.QueuedConnection,
                        QtCore.Q_ARG(str, new_text),
                    )
                    current_word = self.words[self.current_index]
                    adjusted_speed = self._adjust_speed_based_on_word_length(
                        current_word, self.time_per_word, 0.15
                    )
                    if current_word.endswith((".", ",", ";", ":", "?", "!")):
                        time.sleep(adjusted_speed * self.punctuation_delay)
                    else:
                        time.sleep(adjusted_speed)
            elif self.scroll_state == "stop":
                time.sleep(0.1)  # sleep a bit to not use CPU excessively

    # Here would be your functions to control the scroll_state
    def play(self):
        print("play called")
        self.scroll_state = "play"

    def stop(self):
        print("stop called")
        self.scroll_state = "stop"

    def reverse(self):
        print("reverse called")
        self.scroll_state = "reverse"

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
