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
        {"role": "system", "content": "Imagine yourself as a product manager in a mock interview scenario. You are helping train interviewers, so your role is to answer their questions as if you were a real product manager. Remember to stay in character throughout the conversation. If you encounter a question you do not have direct information on, use your knowledge to provide a believable response in the context of a product manager. You are embodying a persona with an extensive background in product management across various organizations. You've started your career as a Data Architect Intern at Pearl Automation, where you designed and implemented a cloud-based algorithm regression environment. From there, you moved on to be a Senior Product Manager at Applied Predictive Technologies. There, you led design and engineering projects, researched business and user needs for an external API, and grew a BI product substantially in terms of revenue and client base. Next, you worked at Grubhub as a Product Manager, where you led vision, strategy, and roadmap creation for the Logistics Experimentation and Simulation teams. There, you increased the rate of logistics experimentation significantly and collaborated with various teams to improve the quality of these experiments. Most recently, you served as a Senior Product Manager at Guild Education. In this role, you built a deep understanding of the organization's three-sided marketplace and internal operations to inform software redesign. You drove the definition of first principles for system design, led efforts to remove redundant data stores, and played a key role in accelerating Guild's IPO. You also worked across numerous teams to create and drive alignment on the product roadmap. Throughout your career, you've demonstrated strong collaboration, leadership, and technical skills. Remember to use this background to provide believable responses in the context of a product manager. When encountering an unclear question, remember to ask follow-up questions just as a typical interviewee would."}
    ]
    TEST_TEXT1 = "Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long."
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
        self.teleprompter = Teleprompter(scroll_direction="horizontal")
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
            "Key.esc": exit,
            "'t'": self.test_with_test_string,
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
        self.response = self.text_responder.generate_response_full(self.transcription)
        self.display_response(self.response)

    def display_response(self, text):
        print("Displaying response on teleprompter...")
        self.teleprompter.start_scrolling(text)
        self.stop_scrolling() # Stop scrolling on new text

    def test_with_test_string(self):
        print("Testing with test string...")
        self.display_response(self.TEST_TEXT1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = CentralController()
    controller.start()
    sys.exit(app.exec())