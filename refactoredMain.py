import sys
import threading
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QMetaObject
from PyQt6.QtGui import QGuiApplication
from PyQt6 import QtCore

from SoundRecorder import SoundRecorder
from Transcriber import Transcriber
from TextResponder import TextResponder
from Teleprompter import Teleprompter

from dotenv import load_dotenv
import os

load_dotenv()

# API and other configurations
API_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_FILE_PATH = "recording_test.wav"
TRANSCRIPTION_MODEL = "whisper-1"
RESPONSE_MODEL = "gpt-3.5-turbo"
STARTING_MESSAGES = [
    {"role": "user",
     "content": "Pretend that you are a candidate for a Product Manager job and I'm your interviewer. I'll ask you "
                "questions and you answer them. Act like all you are is a product manager, do not tell me you are an "
                "AI model."},
    {"role": "assistant", "content": "OK. Can I ask follow up questions if something is unclear?"},
    {"role": "user", "content": "Yes, please do. Let's start the interview now."},
    {"role": "assistant", "content": "Sounds good!"}
]

TEST_TEXT = "I'm sorry to hear that you're not feeling well today, but taking a day off to rest and recover is the " \
            "best decision. Your health should always be a top priority. Don't worry about work, we'll manage in your " \
            "absence. Thank you for letting us know, and please take all the time you need to feel better. We hope " \
            "you get well soon!"

# Function to bold one word at a time in a given text
def bold_one_word_at_a_time(text, index):
    words = text.split()
    if index < len(words):
        words[index] = f"<b>{words[index]}</b>"
    else:
        return ""  # Return an empty string when the index is out of range
    return " ".join(words[max(0, index - 2):index + 3])

# Function to adjust the speed based on the word length
def adjust_speed_based_on_word_length(word, base_speed, multiplier):
    adjusted_speed = base_speed * max(len(word) * multiplier, 0.5)  # Ensure a minimum speed
    return adjusted_speed

# Function to update the text in the window with a timed delay
def timed_update(window, text, words_per_minute=250):
    words = text.split()
    num_words = len(words)
    time_per_word = 60 / words_per_minute
    punctuation_delay = time_per_word * 1.5

    for index in range(num_words + 1):
        new_text = bold_one_word_at_a_time(text, index)
        QMetaObject.invokeMethod(window, "update_text", Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, new_text))
        current_word = words[index] if index < num_words else ""
        if current_word.endswith((".", ",", ";", ":", "?", "!")):
            time.sleep(punctuation_delay)
        else:
            adjusted_speed = adjust_speed_based_on_word_length(current_word, time_per_word, 0.15)
            time.sleep(adjusted_speed)


# Function to continue the conversation and update the window with responses
def continue_conversation(window):
    new_text = None
    while new_text != "exit()":
        # Create our sound recorder
        recorder = SoundRecorder(AUDIO_FILE_PATH)

        # Start the recording process
        recorder.start_recording()
        time.sleep(5)
        recorder.stop_recording()

        transcriber = Transcriber(API_KEY, TRANSCRIPTION_MODEL)
        transcript = transcriber.transcribe_audio(AUDIO_FILE_PATH)
        next_message = transcript['text']
        next_message = "What are some of your greatest strengths and weaknesses?"
        print(next_message)

        text_responder = TextResponder(API_KEY, RESPONSE_MODEL, STARTING_MESSAGES)

        response = text_responder.generate_response(next_message)
        message = response['choices'][0]['message']['content']
        formatted_text = message
        timed_update(window, formatted_text)

        new_text = input("Press enter to continue")
        next_message = "Interesting. Tell me more."
        print(next_message)

        text_responder = TextResponder(API_KEY, RESPONSE_MODEL, STARTING_MESSAGES)

        response = text_responder.generate_response(next_message)
        message = response['choices'][0]['message']['content']
        formatted_text = message
        window.start_scrolling(formatted_text)

        # Not used, just for waiting purposes
        new_text = input("Press enter to continue")


def test_timing(window):
    timed_update(window, TEST_TEXT)


def create_window_with_transparent_background(text):
    app = QApplication(sys.argv)
    window = Teleprompter()
    window.update_text(text)

    screen = QGuiApplication.primaryScreen().geometry()
    window.setGeometry(screen.width() // 2 - window.width() // 2, 0, window.width(),
                       window.height())  # Move window to the top center of the screen

    # Run the update_text_in_window function in a separate thread
    update_thread = threading.Thread(target=continue_conversation, args=(window,))
    update_thread.start()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    text = "Sample text"
    create_window_with_transparent_background(text)