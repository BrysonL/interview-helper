import threading
import time
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QMetaObject
from PyQt6.QtGui import QColor, QPainter, QGuiApplication
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

# This class will display and scroll through text
class Teleprompter(QWidget):
    # Set the size of the window relative to the screen size
    WIDTH_MULTIPLIER = 0.2
    HEIGHT_MULTIPLIER = 0.2

    # Scroll constants
    VERTICAL_SCROLL_DELAY = 0.075  # seconds
    HORIZONTAL_SCROLL_DELAY = 0.0075  # seconds
    SCROLL_DELAY_MULTIPLIER = 1.5

    # The teleprompter can be used to scroll text "vertical", "horizontal", or "bold"
    # "vertical" will smoothly scroll the text up and down
    # "horizontal" will smoothly scroll the text left and right
    # "bold" will bold one word at a time, displaying only a few words at a time (a bit choppy)
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

        # Set the child text_widget (window) size
        width = screen.width() * self.WIDTH_MULTIPLIER
        height = screen.height() * self.HEIGHT_MULTIPLIER
        self.text_widget.setFixedWidth(width)
        self.text_widget.setFixedHeight(height)

        # Set scrolling control variables
        self.scroll_state = "stop"  # or 'play' or 'reverse'
        self.current_index = 0  # the current word being displayed
        self.scroll_direction = scroll_direction
        self.base_scroll_delay = self.VERTICAL_SCROLL_DELAY

        # For horizontally scrolling text, change some of the properties
        if self.scroll_direction == "horizontal":
            self.text_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            self.text_widget.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.text_widget.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self.base_scroll_delay = self.HORIZONTAL_SCROLL_DELAY

            # make the window shorter and wider if scrolling horizontally
            self.text_widget.setFixedHeight(height * 0.4)
            self.text_widget.setFixedWidth(width * 1.5)

        self.scroll_delay = self.base_scroll_delay

        # Display the window
        self.show()
        self.start_scrolling("")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0)  # Adjust the background opacity (0-1)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

    # center the window on the screen
    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = self.frameSize()
        x = (screen.width() - window_size.width()) // 2
        self.move(x, 0)

    # The first time you're updating the text with a string, use this function to reset window size, etc.
    # Also used if you are not streaming a response from TextResponder and are waiting for a full update
    @pyqtSlot(str)
    def update_text(self, text):
        self.text_widget.setHtml(text)

        self.text_widget.adjustSize()  # Adjust the QLabel size to fit the text
        self.adjustSize()  # Adjust the window size to fit the QLabel
        self.center_window()  # Center the window at the top of the screen

        self.repaint()

    # Used after the first update when streaming response from TextResponder
    @pyqtSlot(str)
    def continue_update_text(self, text):
        text = text.replace(" ", "&nbsp;")  # prevent the html from collapsing spaces
        self.text_widget.insertHtml(text)

    # Move the window when the user clicks and drags
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

    ###
    # Teleprompter text update functions
    ###

    # Start scrolling the text
    # words_per_minute is the speed at which the text will bold if you're using the "bold" setting
    # If you're using the "vertical" or "horizontal" settings, the speed is controlled by the scroll_delay constant
    # Call this when you want to start scrolling a full string or with the first result of a stream
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

        # UI can only be safely updated from the main thread, so we need to use invokeMethod
        QMetaObject.invokeMethod(
            self,
            "continue_update_text",
            Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, text),
        )

    # Bold one word at a time of the text
    # I like horizontal and vertical scroll better than bold, but this is here if you want it
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

    # Scroll the text vertically
    def _timed_update_vertical(self):
        while True:
            if self.scroll_state == "play":
                # Perform the scroll by updating the QTextEdit's vertical scrollbar's value
                scroll_bar = self.text_widget.verticalScrollBar()
                new_value = scroll_bar.value() + 1
                if new_value <= scroll_bar.maximum():
                    scroll_bar.setValue(new_value)
                    time.sleep(
                        self.scroll_delay
                    )  # Modify this value to adjust the scroll speed
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
                time.sleep(0.1) # Don't use CPU excessively if we're stopped

    # Scroll the text horizontally
    def _timed_update_horizontal(self):
        while True:
            if self.scroll_state == "play":
                # Perform the scroll by updating the QTextEdit's horizontal scrollbar's value
                scroll_bar = self.text_widget.horizontalScrollBar()
                new_value = scroll_bar.value() + 1
                if new_value <= scroll_bar.maximum():
                    scroll_bar.setValue(new_value)
                    time.sleep(
                        self.scroll_delay
                    )  # Modify this value to adjust the scroll speed
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the end
            elif self.scroll_state == "reverse":
                # Perform the scroll by updating the QTextEdit's horizontal scrollbar's value
                scroll_bar = self.text_widget.horizontalScrollBar()
                new_value = scroll_bar.value() - 1
                if new_value >= scroll_bar.minimum():
                    scroll_bar.setValue(new_value)
                    time.sleep(
                        self.scroll_delay
                    )  # Modify this value to adjust the scroll speed
                else:
                    time.sleep(0.05)  # Don't use CPU excessively if we're at the start
            elif self.scroll_state == "stop":
                time.sleep(0.1)  # Don't use CPU excessively if we're stopped

    ###
    # Scroll state functions
    ###

    # Start the teleprompter scrolling, speed it up, or slow it down (depending on the current state)
    def play(self):
        # If the teleprompter is already playing, speed it up
        if self.scroll_state == "play":
            self.scroll_delay /= (
                self.SCROLL_DELAY_MULTIPLIER
            )
        # If the teleprompter is reversing, slow it down    
        elif self.scroll_state == "reverse":
            self.scroll_delay *= (
                self.SCROLL_DELAY_MULTIPLIER
            ) 
        # Otherwise (the teleprompter is stopped), start the teleprompter
        else:
            self.scroll_delay = self.base_scroll_delay
            self.scroll_state = "play"

    # Stop the teleprompter
    def stop(self):
        self.scroll_state = "stop"

    # Reverse the teleprompter scrolling, speed it up, or slow it down (depending on the current state)
    def reverse(self):
        # If the teleprompter is already playing, speed it up
        if self.scroll_state == "reverse":
            self.scroll_delay /= (
                self.SCROLL_DELAY_MULTIPLIER
            )  
        # If the teleprompter is reversing, slow it down    
        elif self.scroll_state == "play":
            self.scroll_delay *= (
                self.SCROLL_DELAY_MULTIPLIER
            )  
        # Otherwise (the teleprompter is stopped), start the teleprompter
        else:
            self.scroll_delay = self.base_scroll_delay
            self.scroll_state = "reverse"

    ###
    # Helper functions
    ###

    # Bold one word at a time of the text
    @staticmethod
    def _bold_one_word_at_a_time(text, index):
        words = text.split()
        if index < len(words):
            words[index] = f"<b>{words[index]}</b>"
        else:
            return ""  # Return an empty string when the index is out of range
        return " ".join(words[max(0, index - 2) : index + 3])

    # Adjust the update speed based on the length of the word
    @staticmethod
    def _adjust_speed_based_on_word_length(word, base_speed, multiplier):
        adjusted_speed = base_speed * max(
            len(word) * multiplier, 0.5
        )  # Ensure a minimum speed
        return adjusted_speed
