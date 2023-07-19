import pyaudio
import wave
import audioop

# Constants
CHUNK_SIZE = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Number of audio channels
RATE = 44100  # Sampling rate
RECORD_SECONDS = 60  # Duration of recording
SILENCE_THRESHOLD = 500  # Amount of RMS energy for a segment to be considered silence
SILENCE_DURATION = 3  # Duration of silence (in seconds) before recording is stopped

# Initialize PyAudio
audio = pyaudio.PyAudio()

# # Set the input device to the default system audio device (input mic)
# input_device_index = audio.get_default_input_device_info()["index"]

# Set the input device to the VB-Cable virtual audio device
input_device_index = None
for i in range(audio.get_device_count()):
    device_info = audio.get_device_info_by_index(i)
    print(device_info)
    if "VB-Cable" in device_info["name"]:
        input_device_index = device_info["index"]
        break

if input_device_index is None:
    print("Error: VB-Cable virtual audio device not found.")
    audio.terminate()
    exit(1)

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
silence_counter = 0
for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
    data = stream.read(CHUNK_SIZE)
    wave_file.writeframes(data)
    rms_energy = audioop.rms(data, 2)
    if rms_energy < SILENCE_THRESHOLD:
        silence_counter += 1
        if silence_counter >= SILENCE_DURATION * (RATE / CHUNK_SIZE):
            print("Silence detected. Recording stopped.")
            break
    else:
        silence_counter = 0

print("Recording finished.")

# Close the audio stream and PyAudio
stream.stop_stream()
stream.close()
audio.terminate()
wave_file.close()