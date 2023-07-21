from TextResponder import TextResponder
from dotenv import load_dotenv
import os

load_dotenv()

# API and other configurations
API_KEY = os.getenv("OPENAI_API_KEY")
RESPONSE_MODEL = "gpt-3.5-turbo"
STARTING_MESSAGES = [
    {"role": "system", "content": "Imagine yourself as a product manager in a mock interview scenario. You are helping train interviewers, so your role is to answer their questions as if you were a real product manager. Remember to stay in character throughout the conversation. If you encounter a question you do not have direct information on, use your knowledge to provide a believable response in the context of a product manager."}
]


def main():
    text_responder = TextResponder(API_KEY, RESPONSE_MODEL, STARTING_MESSAGES)
    next_message = "What are some of your greatest strengths and weaknesses?"

    text_responder.generate_response_stream(next_message)

if __name__ == "__main__":
    main()