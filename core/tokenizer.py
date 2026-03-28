import tiktoken
import logging

class Tokenizer:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        try:
            self.enc = tiktoken.encoding_for_model(model)
        except KeyError:
            logging.warning(f"[Tokenizer] Unknown model '{model}' for tiktoken. Falling back to 'cl100k_base'.")
            self.enc = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> tuple[int, list[int]]:
        if not text:
            return 0, []
        tokens = self.enc.encode(text)
        return len(tokens), tokens