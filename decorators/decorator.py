from core.tokenizer import Tokenizer

tokenizer = Tokenizer()

def guard(func):
    def wrapper(*args, **kwargs):
        # assume first argument is text
        text = args[0]

        # count tokens
        token_count , tokens = tokenizer.count(text)

        print(f"[TokenGuard] Input tokens: {token_count}")
        print(f"[TokenGuard] Tokens: {tokens}")

        # call original function
        result = func(*args, **kwargs)

        return result

    return wrapper