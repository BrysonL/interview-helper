import pyaudio
import wave
import audioop


class SoundRecorder:
    CHUNK_SIZE = 1024  # Number of frames per buffer
    FORMAT = pyaudio.paInt16  # Audio format
    CHANNELS = 1  # Number of audio channels
    RATE = 44100  # Sampling rate
    RECORD_SECONDS = 60  # Duration of recording
    SILENCE_THRESHOLD = 500  # Amount of RMS energy for a segment to be considered silence
    SILENCE_DURATION = 3  # Duration of silence (in seconds) before recording is stopped

    def __init__(self, recording_file_destination, device_name=None):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.device_name = device_name
        self.file_name = recording_file_destination
        self.wave_file = None
        self.silence_counter = 0

    def start_recording(self):
        # Set the input device to the virtual audio device
        input_device_index = None

        # if no input device is provided, use the default input device (system mic)
        if self.device_name is None:
            input_device_index = self.audio.get_default_input_device_info()["index"]
        else:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if self.device_name in device_info["name"]:
                    input_device_index = device_info["index"]
                    break

            if input_device_index is None:
                print(f"Error: {self.device_name} virtual audio device not found.")
                return

        # Open the audio stream
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                      input=True, input_device_index=input_device_index,
                                      frames_per_buffer=self.CHUNK_SIZE)

        # Create a wave file to save the recorded audio
        self.wave_file = wave.open(self.file_name, "wb")
        self.wave_file.setnchannels(self.CHANNELS)
        self.wave_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        self.wave_file.setframerate(self.RATE)

        print("Recording setup complete.")

    def record(self):
        if not self.stream or not self.wave_file:
            print("Error: Recording not set up.")
            return

        # Record the audio
        print("Recording started...")
        for i in range(0, int(self.RATE / self.CHUNK_SIZE * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK_SIZE)
            self.wave_file.writeframes(data)
            rms_energy = audioop.rms(data, 2)
            if rms_energy < self.SILENCE_THRESHOLD:
                self.silence_counter += 1
                if self.silence_counter >= self.SILENCE_DURATION * (self.RATE / self.CHUNK_SIZE):
                    print("Silence detected. Recording stopped.")
                    break
            else:
                self.silence_counter = 0

        print("Recording finished.")

    def stop_recording(self):
        if self.stream:
            # Close the audio stream and PyAudio
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.wave_file.close()
            self.stream = None
            self.wave_file = None
