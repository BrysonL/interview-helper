import pyaudio
import wave
import threading


class SoundRecorder:
    CHUNK_SIZE = 1024  # Number of frames per buffer
    FORMAT = pyaudio.paInt16  # Audio format
    CHANNELS = 1  # Number of audio channels
    RATE = 44100  # Sampling rate
    SILENCE_THRESHOLD = (
        500  # Amount of RMS energy for a segment to be considered silence
    )
    SILENCE_DURATION = 3  # Duration of silence (in seconds) before recording is stopped

    def __init__(self, recording_file_destination, device_name=None):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.device_name = device_name
        self.file_name = recording_file_destination
        self.wave_file = None
        self.silence_counter = 0
        self.is_recording = False

    def start_recording(self):
        input_device_index = None

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

        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        self.wave_file = wave.open(self.file_name, "wb")
        self.wave_file.setnchannels(self.CHANNELS)
        self.wave_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        self.wave_file.setframerate(self.RATE)

        # Start the recording thread
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()

        print("Recording setup complete and recording started.")

    def stop_recording(self):
        self.is_recording = False
        # Wait for the recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()
        print("Recording stopped.")

    def record(self):
        while self.is_recording:
            data = self.stream.read(self.CHUNK_SIZE)
            self.wave_file.writeframes(data)

        # Cleanup after recording
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.wave_file.close()
            self.stream = None
            self.wave_file = None

    def close(self):
        self.audio.terminate()

    def __del__(self):
        self.close()
