import openai


class TextResponder:
    def __init__(self, api_key, model, starting_messages):
        openai.api_key = api_key
        self.model = model
        self.messages = starting_messages

    def generate_response_full(self, next_message):
        self.messages.append({"role": "user", "content": next_message})
        response = openai.ChatCompletion.create(
            model=self.model, messages=self.messages
        )
        self.messages.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )

        return response["choices"][0]["message"]["content"]

    # adapted from https://github.com/trackzero/openai/blob/main/oai-text-gen-with-secrets-and-streaming.py
    # note: function is a generator, you must iterate over it to get the results
    def generate_response_stream(self, next_message):
        self.messages.append({"role": "user", "content": next_message})
        response = openai.ChatCompletion.create(
            model=self.model, messages=self.messages, stream=True
        )
        # event variables
        collected_chunks = []
        collected_messages = ""

        # capture and print event stream
        for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk["choices"][0]["delta"]  # extract the message
            # print(chunk_message)
            if "content" in chunk_message:
                message_text = chunk_message["content"]
                collected_messages += message_text
                yield message_text
        #         print(f"{message_text}", end="")
        # print(f"\n")

        # print(collected_messages)
        self.messages.append({"role": "assistant", "content": collected_messages})
