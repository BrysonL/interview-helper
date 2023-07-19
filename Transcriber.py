import openai

class Transcriber:
    def __init__(self, api_key, audio_file_path, model):
        openai.api_key = api_key
        self.audio_file_path = audio_file_path
        self.model = model

    def transcribe_audio(self):
        with open(self.audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(self.model, audio_file)
            return transcript
