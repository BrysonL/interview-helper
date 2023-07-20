import keyboard
from sound_recorder import SoundRecorder
from transcriber import Transcriber
from text_responder import TextResponder
from teleprompter import Teleprompter

class CentralController:

    def __init__(self):
        self.sound_recorder = SoundRecorder("my_recording.wav")
        self.transcriber = Transcriber()
        self.text_responder = TextResponder()
        self.teleprompter = Teleprompter()

    def start(self):
        print("Controller started. Waiting for keypress...")

        keyboard.add_hotkey('f1', self.start_recording)
        keyboard.add_hotkey('f2', self.stop_recording_and_transcribe)
        keyboard.add_hotkey('f3', self.respond_to_transcription)
        keyboard.add_hotkey('f4', self.display_response)

        keyboard.wait('esc')

    def start_recording(self):
        print("Starting recording...")
        self.sound_recorder.start_recording()

    def stop_recording_and_transcribe(self):
        print("Stopping recording and transcribing...")
        self.sound_recorder.stop_recording()
        self.transcription = self.transcriber.transcribe("my_recording.wav")

    def respond_to_transcription(self):
        print("Generating response to transcription...")
        self.response = self.text_responder.generate_response(self.transcription)

    def display_response(self):
        print("Displaying response on teleprompter...")
        self.teleprompter.display_text(self.response)
