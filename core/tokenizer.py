import tiktoken

class Tokenizer:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.enc = tiktoken.encoding_for_model(model)

    def count(self, text: str) -> int:
        tokens = self.enc.encode(text)
        return len(tokens), tokens