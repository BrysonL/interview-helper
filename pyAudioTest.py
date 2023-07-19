import pyaudio
import wave

# Constants
CHUNK_SIZE = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Number of audio channels
RATE = 44100  # Sampling rate
RECORD_SECONDS = 10  # Duration of recording

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Set the input device to the default system audio device (input mic)
input_device_index = audio.get_default_input_device_info()["index"]

# Open the audio stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, input_device_index=input_device_index,
                    frames_per_buffer=CHUNK_SIZE)

# Create a wave file to save the recorded audio
wave_file = wave.open("zoom_recording.wav", "wb")
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)

# Record the audio
print("Recording started...")
for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
    data = stream.read(CHUNK_SIZE)
    wave_file.writeframes(data)

print("Recording finished.")

# Close the audio stream and PyAudio
stream.stop_stream()
stream.close()
audio.terminate()
wave_file.close()