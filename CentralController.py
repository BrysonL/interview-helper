from SoundRecorder import SoundRecorder
from Transcriber import Transcriber
from TextResponder import TextResponder
from Teleprompter import Teleprompter
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from pynput import keyboard
import os, sys, time


class CentralController:
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
    TEST_TEXT1 = "Hello world! Here's a test of the teleprompter that is more than a few words long."
    TEST_TEXT2 = "This is another test to see if we can switch texts."

    class KeyListenerThread(QThread):
        def __init__(self, hotkeys):
            super().__init__()
            self.hotkeys = hotkeys

        def run(self):
            with keyboard.Listener(on_press=self.on_press(self.hotkeys)) as listener:
                listener.join()

        def on_press(self, hotkeys):
            def _on_press(key):
                print(str(key) + "pressed.")
                try:
                    # If the key is in the hotkeys, call the associated method
                    hotkeys[str(key)]()
                except KeyError:
                    # Ignore keys that are not in the hotkeys
                    pass
            return _on_press

    def __init__(self):
        self.sound_recorder = SoundRecorder(self.AUDIO_FILE_PATH)
        self.transcriber =Transcriber(self.API_KEY, self.TRANSCRIPTION_MODEL)
        self.text_responder = TextResponder(self.API_KEY, self.RESPONSE_MODEL, self.STARTING_MESSAGES)
        self.teleprompter = Teleprompter()
        self.is_recording = False
    
    
    def start(self):
        print("Controller started. Waiting for keypress...")

        # Define the hotkeys and their corresponding methods
        hotkeys = {
            "Key.shift": self.trigger_recording,
            "Key.shift_r": self.trigger_recording,
            "Key.right": self.start_scrolling,
            "Key.down": self.stop_scrolling,
            "Key.left": self.reverse_scrolling,
            "Key.esc": exit
        }

        # Start the key listener on a separate thread
        self.key_listener_thread = self.KeyListenerThread(hotkeys)
        self.key_listener_thread.start()

    def start_scrolling(self):
        self.teleprompter.play()

    def stop_scrolling(self):
        self.teleprompter.stop()

    def reverse_scrolling(self):
        self.teleprompter.reverse()

    def trigger_recording(self):
        if self.is_recording:
            self.stop_recording_and_transcribe()
        else:
            self.start_recording()
        
        self.is_recording = not self.is_recording

    def start_recording(self):
        print("Starting recording...")
        self.sound_recorder.start_recording()

    def stop_recording_and_transcribe(self):
        print("Stopping recording and transcribing...")
        self.sound_recorder.stop_recording()
        time.sleep(0.1) # Wait for the file to be written, I think this is required but not 100% sure
        self.transcription = self.transcriber.transcribe_audio(self.AUDIO_FILE_PATH)
        self.respond_to_transcription()

    def respond_to_transcription(self):
        print("Generating response to transcription...")
        self.response = self.text_responder.generate_response(self.transcription)
        self.display_response(self.response)

    def display_response(self, text):
        print("Displaying response on teleprompter...")
        self.teleprompter.start_scrolling(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = CentralController()
    controller.start()
    sys.exit(app.exec())