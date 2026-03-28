class CostCalculator:
    INPUT_PRICE_PER_TOKEN = 2 / 1_000_000  
    OUTPUT_PRICE_PER_TOKEN = 4 / 1_000_000 

    @classmethod
    def calculate_input_cost(cls, token_count: int) -> float:
        """Calculates the cost based on the number of input tokens."""
        return token_count * cls.INPUT_PRICE_PER_TOKEN

    @classmethod
    def calculate_output_cost(cls, token_count: int) -> float:
        """Calculates the cost based on the number of output tokens."""
        return token_count * cls.OUTPUT_PRICE_PER_TOKEN
    
    @classmethod
    def calculate_compression_ratio(cls, original_tokens: int, compressed_tokens: int) -> float:
        """Calculates how much the prompt was compressed as a ratio."""
        if original_tokens == 0:
            return 0.0
        return compressed_tokens / original_tokens
