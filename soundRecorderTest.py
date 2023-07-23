import os
import time
from SoundRecorder import SoundRecorder


def test_start_stop_methods():
    recorder = SoundRecorder("test2.wav")
    recorder.start_recording()
    time.sleep(3)  # Let it record for 3 seconds
    recorder.stop_recording()
    if os.path.isfile("test2.wav"):
        print("Test 2 passed.")
    else:
        print("Test 2 failed.")


test_start_stop_methods()
