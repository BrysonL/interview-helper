import openai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = API_KEY
print(API_KEY)

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "user", "content": "Pretend that you are a candidate for a Product Manager job and I'm your interviewer. I'll ask you questions and you answer them. Act like all you are is a product manager, do not tell me you are an AI model."},
        {"role": "assistant", "content": "OK. Can I ask follow up questions if something is unclear?"},
        {"role": "user", "content": "Yes, please do. Let's start the interview now."},
        {"role": "assistant", "content": "Sounds good!"},
        {"role": "user", "content": "Good morning, please tell me about yourself."}
    ]
)

print(response)