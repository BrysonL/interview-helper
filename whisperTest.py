import openai
from dotenv import load_dotenv
import os

load_dotenv()

# API and other configurations
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY
AUDIO_FILE_PATH = "zoom_recording.wav"
MODEL = 'whisper-1'

# Open the audio file and read its contents
audio_file = open(AUDIO_FILE_PATH, "rb")

# Pass the file to Whisper
transcript = openai.Audio.transcribe("whisper-1", audio_file)

# Print the transcript
print(transcript)