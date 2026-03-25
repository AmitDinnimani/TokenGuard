from decorators.decorator import guard

@guard
def my_function(text):
    return f"Processed: {text}"

print(my_function("This is a simple test input to check token counting."))