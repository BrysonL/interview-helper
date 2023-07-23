# interview-helper
This project provides a teleprompter-like interview experience. It listens to your microphone or system sound, transcribes the audio, generates a response using an LLM, and then displays the response scrolling across the screen.

There are a number of requirements for running this project. I've only tested it on an Apple Silicon Mac (M1 Pro); if you have problems running this on another system please let me know.

Note: I linked some ChatGPT queries on basic tasks, but didn't try them out on all systems. YMMV.

### To get your environment set up:
- git clone this repo.
- If desired, [set up a venv for this project](https://chat.openai.com/share/18b56881-85a8-4fce-9fe2-17e3c3834638).
- Install the requirements from requirements.txt.
  - Note: some of the requirements (like PyAudio) may require additional installation steps. Please ask ChatGPT if you're having issues with any of the packages.
- If you want to transcribe questions from the system audio (e.g. over a video call) (I presume this is most of you), you'll need to install a driver that can listen to system audio. I used [VB-Cable](https://vb-audio.com/Cable/).
- [Set your primary display](https://chat.openai.com/share/abcf3e01-4a2f-472b-86ba-ad173f6d4ba4) to the display with your camera (or the one you want to look at). The transcriber will show up in the top center of your primary monitor.

### Before running the code:
- [Create a .env file](https://chat.openai.com/share/15d5f385-f191-48e0-9877-713cdbd00c8c) in the root directory of the project and the line: OPENAI_API_KEY=<ab-YOURAPIKEY>
- Modify the system message (as of this commit it is on line 55 of the CentralController.py). You can use a [prompt like this](https://chat.openai.com/share/fb1ade46-19b8-4677-969f-7d22002625d2) to generate your message or write it yourself. Use the one in the repo currently as inspiration, it works pretty well.
- <todo: VB-Cable instructions>
- If desired, test out each of the classes (SoundRecorder, Transcriber, TextResponder, Teleprompter) with the included test files before running the CentralController.

### To run the code:
- Familiarize yourself with the hotkey assignments (as of this commit they are on lines 75-83 of CentralController.py) and the associated functions.
  - tl;dr: (either) shift key to start recording; shift key again to stop recording, transcribe, and display the result; `d` to start scrolling the teleprompter; `s` to stop the teleprompter; `a` to reverse the teleprompter; repeated pressing of `a` and `d` speed up and slow down scroll speed.
- If you're using a virtual environment, [activate it](https://chat.openai.com/share/18b56881-85a8-4fce-9fe2-17e3c3834638)
- Run CentralController.py