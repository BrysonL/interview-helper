import openai


class TextResponder:
    def __init__(self, api_key, model, starting_messages):
        openai.api_key = api_key
        self.model = model
        self.messages = starting_messages

    def generate_response(self, next_message):
        self.messages.append({"role": "user", "content": next_message})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})

        return response
