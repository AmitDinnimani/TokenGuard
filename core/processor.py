import time
import logging
import functools
from typing import Optional, Tuple, Any
from core.tokenizer import Tokenizer
from core.budget import BudgetManager
from compression.compressor import OllamaCompressor
from observer.observer import TokenObserver
from observer.operations import CostCalculator
from config.config import Config

class TokenGuardProcessor:
    def __init__(self, limit: Optional[float] = None, ollama_model: Optional[str] = None, cache_size: int = 100):
        self.tokenizer = Tokenizer()
        self.budget_manager = BudgetManager(default_limit=limit or Config.DEFAULT_BUDGET_LIMIT)
        self.compressor = OllamaCompressor(model=ollama_model or Config.OLLAMA_MODEL)
        self.observer = TokenObserver()
        self.logger = logging.getLogger("TokenGuard.Processor")
        
        # Security: Hard limit on input size to prevent DoS (e.g., 1MB or 100k tokens)
        self.max_input_chars = 1_000_000 
        
        # Performance: Internal LRU Cache for compression
        # We wrap the internal compression methods with caching
        self._cached_compress = functools.lru_cache(maxsize=cache_size)(self.compressor.compress)
        # Note: lru_cache doesn't support async natively in Python < 3.8 easily without wrappers,
        # but for this logic, we'll implement a simple manual cache or use the sync one if appropriate.
        self._async_cache = {}

    def _validate_input(self, prompt: str):
        if len(prompt) > self.max_input_chars:
            raise ValueError(f"Input prompt exceeds maximum allowed size of {self.max_input_chars} characters.")

    def process(self, prompt: str, dynamic_limit: Optional[float] = None, auto_approve: bool = True) -> Tuple[str, str]:
        """Synchronously process the prompt."""
        self._validate_input(prompt)
        req_id = self.observer.start_request()
        
        token_count, _ = self.tokenizer.count(prompt)
        self.observer.record_original_prompt(req_id, token_count, prompt)
        
        estimated_cost = CostCalculator.calculate_input_cost(token_count)
        
        if self.budget_manager.is_within_budget(estimated_cost, dynamic_limit=dynamic_limit):
            self.logger.info(f"Prompt within budget (${estimated_cost:.5f})")
            return prompt, req_id
            
        self.logger.warning(f"BUDGET EXCEEDED: Cost (${estimated_cost:.5f}) exceeds limit!")
        
        # Try cache first
        compressed_prompt = self._cached_compress(prompt)
        
        if not compressed_prompt:
            self.logger.error("Compression failed. Proceeding with original.")
            return prompt, req_id
            
        return self._finalize_processing(req_id, prompt, compressed_prompt, token_count, estimated_cost, auto_approve)

    async def process_async(self, prompt: str, dynamic_limit: Optional[float] = None, auto_approve: bool = True) -> Tuple[str, str]:
        """Asynchronously process the prompt."""
        self._validate_input(prompt)
        req_id = self.observer.start_request()
        
        token_count, _ = self.tokenizer.count(prompt)
        self.observer.record_original_prompt(req_id, token_count, prompt)
        
        estimated_cost = CostCalculator.calculate_input_cost(token_count)
        
        if self.budget_manager.is_within_budget(estimated_cost, dynamic_limit=dynamic_limit):
            return prompt, req_id

        # Async Cache Check
        if prompt in self._async_cache:
            compressed_prompt = self._async_cache[prompt]
        else:
            compressed_prompt = await self.compressor.compress_async(prompt)
            if compressed_prompt:
                self._async_cache[prompt] = compressed_prompt
        
        if not compressed_prompt:
            return prompt, req_id
            
        return self._finalize_processing(req_id, prompt, compressed_prompt, token_count, estimated_cost, auto_approve)

    def _finalize_processing(self, req_id: str, original: str, compressed: str, orig_tokens: int, orig_cost: float, auto_approve: bool) -> Tuple[str, str]:
        comp_token_count, _ = self.tokenizer.count(compressed)
        comp_cost = CostCalculator.calculate_input_cost(comp_token_count)
        
        self.logger.info(f"Compression Successful! Tokens: {orig_tokens} ➔ {comp_token_count}")
        
        if auto_approve:
            self.observer.record_compressed_prompt(req_id, comp_token_count, 0.0, compressed)
            return compressed, req_id
        else:
            # Fallback for CLI, though async environments usually don't want blocking input()
            user_input = input("Approve compression? (y/n): ").strip().lower()
            if user_input == 'y':
                self.observer.record_compressed_prompt(req_id, comp_token_count, 0.0, compressed)
                return compressed, req_id
            return original, req_id