import os
import time
from SoundRecorder import SoundRecorder

# def test_stop_on_silence():
#     recorder = SoundRecorder("test1.wav")
#     recorder.record()
#     # Manually ensure silence after some time to check if recording stops
#     print("Please ensure there is silence after a few seconds.")
#     time.sleep(5)
#     if os.path.isfile("test1.wav"):
#         print("Test 1 passed.")
#     else:
#         print("Test 1 failed.")

def test_start_stop_methods():
    recorder = SoundRecorder("test2.wav")
    recorder.start_recording()
    time.sleep(3) # Let it record for 3 seconds
    recorder.stop_recording()
    if os.path.isfile("test2.wav"):
        print("Test 2 passed.")
    else:
        print("Test 2 failed.")

# test_stop_on_silence()
test_start_stop_methods()