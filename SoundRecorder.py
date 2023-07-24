import pyaudio
import wave
import threading

# SoundRecorder uses PyAudio to record sound from your system and save it to a .wav file
class SoundRecorder:
    # Bunch of constants for PyAudio
    CHUNK_SIZE = 1024  # Number of frames per buffer
    FORMAT = pyaudio.paInt16  # Audio format
    CHANNELS = 1  # Number of audio channels
    RATE = 44100  # Sampling rate

    # initialize the recorder, file name is self-explanatory, device-name is the name of the audio device you want to record from
    def __init__(self, recording_file_destination, device_name=None):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.device_name = device_name
        self.file_name = recording_file_destination
        self.wave_file = None
        self.is_recording = False

    # Start recording from the specified device, if no device is specified, the system mic (default device) is used
    def start_recording(self):
        input_device_index = None

        # if no device name is specified, use the default device
        if self.device_name is None:
            input_device_index = self.audio.get_default_input_device_info()["index"]
        # else loop through all the devices and find the one with the specified name
        else:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if self.device_name in device_info["name"]:
                    input_device_index = device_info["index"]
                    break

            if input_device_index is None:
                print(f"Error: {self.device_name} virtual audio device not found.")
                return

        # Open the stream
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

    # Stop recording
    def stop_recording(self):
        self.is_recording = False
        # Wait for the recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()
        print("Recording stopped.")

    # The recording thread function
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

    # Close the audio object when it's time to clean up
    def close(self):
        self.audio.terminate()

    def __del__(self):
        self.close()
