# interview-helper
This project provides a teleprompter-like interview experience. It listens to your microphone or system sound, transcribes the audio, generates a response using an LLM, and then displays the response scrolling across the screen.

There are a number of requirements for running this project. I've only tested it on an Apple Silicon Mac (M1 Pro); if you have problems running this on another system please let me know.

To get your environment set up:
- If desired, [set up a venv for this project](https://chat.openai.com/share/18b56881-85a8-4fce-9fe2-17e3c3834638)
- Install the requirements from requirements.txt
  - Note: some of the requirements (like PyAudio) may require additional installation steps. Please ask ChatGPT if you're having issues with any of the packages.
- If you want to transcribe questions from the system audio (e.g. over a video call) (I presume this is most of you), you'll need to install a driver that can listen to system audio. I used [VB-Cable](https://vb-audio.com/Cable/).

Before running the code:
- Modify the system message (as of this commit it is on line 55 of the CentralController.py). You can use a [prompt like this](https://chat.openai.com/share/fb1ade46-19b8-4677-969f-7d22002625d2) to generate your message or write it yourself. Use the one in the repo currently as inspiration, it works pretty well.
