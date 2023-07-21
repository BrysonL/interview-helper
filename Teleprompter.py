import threading
import time
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QMetaObject
from PyQt6.QtGui import QColor, QPainter, QGuiApplication
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class Teleprompter(QWidget):
    WIDTH_MULTIPLIER = 0.2
    HEIGHT_MULTIPLIER = 0.2

    VERTICAL_SCROLL_DELAY = 0.05  # seconds
    HORIZONTAL_SCROLL_DELAY = 0.005  # seconds
    SCROLL_DELAY_MULTIPLIER = 1.5

    def __init__(self, scroll_direction="horizontal", parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)

        # Move window to the top center of the screen
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 2 - self.width() // 2, 0, self.width(), self.height()
        )

        self.text_widget = QTextEdit(self)
        self.text_widget.setReadOnly(True)
        self.text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_widget.setStyleSheet(
            "color: white; font-size: 32px; qproperty-alignment: AlignCenter; background-color: black;"
        )  # Updated style sheet
        layout = QVBoxLayout()
        layout.addWidget(self.text_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Removes layout margins
        self.setLayout(layout)
        self.mouse_down = False
        self.offset = QPoint()

        # Set the child text_widget (window) size to 30% of the screen width and 10% of the screen height
        width = screen.width() * self.WIDTH_MULTIPLIER
        height = screen.height() * self.HEIGHT_MULTIPLIER
        self.text_widget.setFixedWidth(width)
        self.text_widget.setFixedHeight(height)

        # Set scrolling control variables
        self.scroll_state = "stop"  # or 'play' or 'reverse'
        self.current_index = 0  # the current word being displayed
        self.scroll_direction = scroll_direction
        self.base_scroll_delay = self.VERTICAL_SCROLL_DELAY

        if self.scroll_direction == "horizontal":
            self.text_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            self.text_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.text_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.base_scroll_delay = self.HORIZONTAL_SCROLL_DELAY

            # make the window shorter and wider if scrolling horizontally
            self.text_widget.setFixedHeight(height*.4)
            self.text_widget.setFixedWidth(width*1.5)

        self.scroll_delay = self.base_scroll_delay

        # Display the window
        self.show()
        self.start_scrolling(
            "Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long."
        )

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
        self.text_widget.setHtml(text)
        
        self.text_widget.adjustSize()  # Adjust the QLabel size to fit the text
        self.adjustSize()  # Adjust the window size to fit the QLabel
        self.center_window()  # Center the window at the top of the screen
        
        self.repaint()

    @pyqtSlot(str)
    def continue_update_text(self, text):
        text = text.replace(' ', '&nbsp;')
        self.text_widget.insertHtml(text)


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

    def start_scrolling(self, text, words_per_minute=110):
        # Set scrolling control variables
        self.text = text
        self.words_per_minute = words_per_minute
        self.words = self.text.split()
        self.current_index = 0
        self.num_words = len(self.words)
        self.time_per_word = 60 / self.words_per_minute
        self.punctuation_delay = 1.5

        # Start the thread that will update the text
        if self.scroll_direction == "horizontal":
            self.scroll_thread = threading.Thread(target=self._timed_update_horizontal)
        elif self.scroll_direction == "vertical":
            self.scroll_thread = threading.Thread(target=self._timed_update_vertical)
        elif self.scroll_direction == "bold":
            self.scroll_thread = threading.Thread(target=self._timed_update_bold)
        else:
            raise ValueError(
                f"scroll_direction must be 'horizontal', 'vertical', or 'bold', not {self.scroll_direction}"
            )
        self.scroll_thread.start()

        # Update the teleprompter with the first thing to display so that the user knows it's ready
        if self.scroll_direction == "bold":
            QMetaObject.invokeMethod(
                self,
                "update_text",
                Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, self._bold_one_word_at_a_time(self.text, 0)),
            )
        else:
            QMetaObject.invokeMethod(
                self,
                "update_text",
                Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(str, self.text),
            )

    # Used when streaming response from TextResponder
    def continue_scrolling(self, text):
        self.text += text

        QMetaObject.invokeMethod(
            self,
            "continue_update_text",
            Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, text),
        )



    def _timed_update_bold(self):
        while True:
            if self.scroll_state == "play":
                if self.current_index < self.num_words:
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

    def _timed_update_vertical(self):
        while True:
            if self.scroll_state == "play":
                # Perform the scroll by updating the QTextEdit's vertical scrollbar's value
                scroll_bar = self.text_widget.verticalScrollBar()
                new_value = scroll_bar.value() + 1
                if new_value <= scroll_bar.maximum():
                    scroll_bar.setValue(new_value)
                    time.sleep(self.scroll_delay)  # Modify this value to adjust the scroll speed
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the bottom
            elif self.scroll_state == "reverse":
                # Perform the scroll by updating the QTextEdit's vertical scrollbar's value
                scroll_bar = self.text_widget.verticalScrollBar()
                new_value = scroll_bar.value() - 1
                if new_value >= scroll_bar.minimum():
                    scroll_bar.setValue(new_value)
                    time.sleep(self.scroll_delay)
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the top
            elif self.scroll_state == "stop":
                time.sleep(0.1)

    def _timed_update_horizontal(self):
        while True:
            if self.scroll_state == "play":
                # Perform the scroll by updating the QTextEdit's horizontal scrollbar's value
                scroll_bar = self.text_widget.horizontalScrollBar()
                new_value = scroll_bar.value() + 1
                if new_value <= scroll_bar.maximum():
                    scroll_bar.setValue(new_value)
                    time.sleep(self.scroll_delay)  # Modify this value to adjust the scroll speed
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the end
            elif self.scroll_state == "reverse":
                # Perform the scroll by updating the QTextEdit's horizontal scrollbar's value
                scroll_bar = self.text_widget.horizontalScrollBar()
                new_value = scroll_bar.value() - 1
                if new_value >= scroll_bar.minimum():
                    scroll_bar.setValue(new_value)
                    time.sleep(self.scroll_delay)  # Modify this value to adjust the scroll speed
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the start
            elif self.scroll_state == "stop":
                time.sleep(0.1)  # sleep a bit to not use CPU excessively


    # Here would be your functions to control the scroll_state
    def play(self):
        print("play called")
        if self.scroll_state == "play":
            self.scroll_delay /= self.SCROLL_DELAY_MULTIPLIER # Increase the scroll speed if we're already going
        elif self.scroll_state == "reverse":
            self.scroll_delay *= self.SCROLL_DELAY_MULTIPLIER # Decrease the scroll speed if we're reversing
        else: # Only play if we're stopped
            self.scroll_delay = self.base_scroll_delay
            self.scroll_state = "play"

    def stop(self):
        print("stop called")
        self.scroll_state = "stop"

    def reverse(self):
        print("reverse called")
        if self.scroll_state == "reverse":
            self.scroll_delay /= self.SCROLL_DELAY_MULTIPLIER # Increase the scroll speed if we're already going
        elif self.scroll_state == "play":
            self.scroll_delay *= self.SCROLL_DELAY_MULTIPLIER # Decrease the scroll speed if we're reversing
        else: # Only reverse if we're stopped
            self.scroll_delay = self.base_scroll_delay
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
