from SoundRecorder import SoundRecorder
from Transcriber import Transcriber
from TextResponder import TextResponder
from Teleprompter import Teleprompter
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard
import os, sys, time

load_dotenv()

# This class controls the interview bot/teleprompter
class CentralController(QThread):
    ###
    # Helper classes
    ###

    # In order to scroll the teleprompter while the response is being generated, we need to use a separate thread
    class ResponseThread(QThread):
        new_text_signal = pyqtSignal(str)

        def __init__(self, response_stream):
            super().__init__()
            self.response_stream = response_stream

        def run(self):
            for response in self.response_stream:
                self.new_text_signal.emit(response)

    # In order to listen for keypresses while the teleprompter is running, we need to use a separate thread
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


    ###
    # Main class
    ###

    # API and other configurations
    API_KEY = os.getenv("OPENAI_API_KEY")
    AUDIO_FILE_PATH = "recording_test.wav"
    TRANSCRIPTION_MODEL = "whisper-1"
    RESPONSE_MODEL = "gpt-3.5-turbo"
    STARTING_MESSAGES = [
        {
            "role": "system",
            "content": "Imagine yourself as a product manager in a mock interview scenario. You are helping train interviewers, so your role is to answer their questions as if you were a real product manager. Remember to stay in character throughout the conversation. If you encounter a question you do not have direct information on, use your knowledge to provide a believable response in the context of a product manager. You are embodying a persona with an extensive background in product management across various organizations. You've started your career as a Data Architect Intern at Pearl Automation, where you designed and implemented a cloud-based algorithm regression environment. From there, you moved on to be a Senior Product Manager at Applied Predictive Technologies. There, you led design and engineering projects, researched business and user needs for an external API, and grew a BI product substantially in terms of revenue and client base. Next, you worked at Grubhub as a Product Manager, where you led vision, strategy, and roadmap creation for the Logistics Experimentation and Simulation teams. There, you increased the rate of logistics experimentation significantly and collaborated with various teams to improve the quality of these experiments. Most recently, you served as a Senior Product Manager at Guild Education. In this role, you built a deep understanding of the organization's three-sided marketplace and internal operations to inform software redesign. You drove the definition of first principles for system design, led efforts to remove redundant data stores, and played a key role in accelerating Guild's IPO. You also worked across numerous teams to create and drive alignment on the product roadmap. Throughout your career, you've demonstrated strong collaboration, leadership, and technical skills. Remember to use this background to provide believable responses in the context of a product manager. When encountering an unclear question, remember to ask follow-up questions just as a typical interviewee would.",
        }
    ]
    TEST_TEXT1 = "Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long. Hello world! Here's a test of the teleprompter that is more than a few words long."

    # Spin up all the components of the controller
    def __init__(self):
        super().__init__()

        self.sound_recorder = SoundRecorder(self.AUDIO_FILE_PATH)
        # self.sound_recorder = SoundRecorder(self.AUDIO_FILE_PATH, device_name="VB-Cable") # Use this line to record from the VB-Cable virtual audio device
        self.transcriber = Transcriber(self.API_KEY, self.TRANSCRIPTION_MODEL)
        self.text_responder = TextResponder(
            self.API_KEY, self.RESPONSE_MODEL, self.STARTING_MESSAGES
        )
        self.teleprompter = Teleprompter(scroll_direction="horizontal")
        self.is_recording = False

    # Start listening for key presses
    def start(self):
        print("Controller started. Waiting for keypress...")

        # Define the hotkeys and their corresponding methods
        # Multiple successive keypresses will call a method multiple times
        hotkeys = {
            "Key.shift": self.trigger_recording,
            "Key.shift_r": self.trigger_recording,
            "'d'": self.start_scrolling,
            "'s'": self.stop_scrolling,
            "'a'": self.reverse_scrolling,
            "Key.esc": exit,
            "'t'": self.test_with_test_string,
        }

        # Start the key listener on a separate thread
        self.key_listener_thread = self.KeyListenerThread(hotkeys)
        self.key_listener_thread.start()

    # Start the teleprompter scrolling (see Teleprompter.py)
    # Call repeatedly to speed forward scroll speed or slow down reverse scroll speed
    def start_scrolling(self):
        self.teleprompter.play()

    # Stop the teleprompter scrolling (see Teleprompter.py)
    def stop_scrolling(self):
        self.teleprompter.stop()

    # Reverse the teleprompter scrolling or slow it down (see Teleprompter.py)
    # Call repeatedly to speed up reverse scroll speed or slow down forward scroll speed
    def reverse_scrolling(self):
        self.teleprompter.reverse()

    # If recording, stop it, otherwise start it
    def trigger_recording(self):
        if self.is_recording:
            self.stop_recording_and_transcribe_stream()
        else:
            self.start_recording()

        self.is_recording = not self.is_recording

    # Start recording
    def start_recording(self):
        print("Starting recording...")
        self.sound_recorder.start_recording()

    ###
    # Full response methods, not streaming (see TextResponder.py)
    ###

    # Stop recording, transcribe the audio, and then call the text responder
    def stop_recording_and_transcribe_full(self):
        print("Stopping recording and transcribing...")
        self.sound_recorder.stop_recording()
        time.sleep(
            0.1
        )  # Wait for the file to be written, I think this is required but not 100% sure. If it is required, this is not a 100% safe way to wait for the file.
        self.transcription = self.transcriber.transcribe_audio(self.AUDIO_FILE_PATH)
        self.respond_to_transcription_full()

    # Generate a response to the transcription and display it on the teleprompter
    def respond_to_transcription_full(self):
        print("Generating response to transcription...")
        self.response = self.text_responder.generate_response_full(self.transcription)
        self.display_response_full(self.response)

    # Display the response on the teleprompter
    def display_response_full(self, text):
        print("Displaying response on teleprompter...")
        self.teleprompter.start_scrolling(text)
        self.stop_scrolling()  # Stop scrolling on new text

    ###
    # Streaming response methods (see TextResponder.py)
    ###

    # Stop recording, transcribe the audio, and then call the text responder
    def stop_recording_and_transcribe_stream(self):
        print("Stopping recording and transcribing...")
        self.sound_recorder.stop_recording()
        time.sleep(
            0.1
        )  # Wait for the file to be written, I think this is required but not 100% sure
        self.transcription = self.transcriber.transcribe_audio(self.AUDIO_FILE_PATH)
        self.respond_to_transcription_stream()

    # Generate a response to the transcription and display it on the teleprompter
    def respond_to_transcription_stream(self):
        print("Generating response to transcription...")
        self.response_stream = self.text_responder.generate_response_stream(
            self.transcription
        )
        self.display_response_stream(self.response_stream)

    # Display the response on the teleprompter
    def display_response_stream(self, response_stream):
        print("Streaming response to teleprompter...")
        self.teleprompter.start_scrolling("") # Empty the text on the teleprompter

        self.stop_scrolling()  # Stop scrolling on new text to reset scroll speed

        # response_stream param is a generator, pass that to the threaded response stream
        self.response_thread = self.ResponseThread(response_stream)

        # The response_thread will emit an event with each new piece of text
        # Connect that event to the teleprompter's continue_scrolling method to add each new piece of text (each word) to the teleprompter
        self.response_thread.new_text_signal.connect(
            self.teleprompter.continue_scrolling
        )
        self.response_thread.start()

        self.start_scrolling()  # Start scrolling on the new text

    # Test the teleprompter with a test string
    # You can also use this to teleprompter a pre-written response (like an answer to "tell me about yourself")
    def test_with_test_string(self):
        print("Testing with test string...")
        self.display_response_full(self.TEST_TEXT1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = CentralController()
    controller.start()
    sys.exit(app.exec())
