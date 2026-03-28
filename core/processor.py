import time
from core.tokenizer import Tokenizer
from core.budget import BudgetManager
from compression.compressor import OllamaCompressor
from observer.observer import TokenObserver
from observer.operations import CostCalculator

class TokenGuardProcessor:
    def __init__(self, limit: float = 0.05, ollama_model: str = "qwen2.5-coder:7b-instruct-q4_K_M"):
        self.tokenizer = Tokenizer()
        self.budget_manager = BudgetManager(default_limit=limit)
        self.compressor = OllamaCompressor(model=ollama_model)
        self.observer = TokenObserver()

    def process(self, prompt: str, dynamic_limit: float = None, auto_approve: bool = True) -> tuple[str, str]:
        """
        Processes the prompt. If it exceeds budget, compresses it.
        Returns a tuple of (final_prompt, request_id)
        """
        req_id = self.observer.start_request()
        
        token_count, _ = self.tokenizer.count(prompt)
        self.observer.record_original_prompt(req_id, token_count, prompt)
        
        estimated_cost = CostCalculator.calculate_input_cost(token_count)
        
        if self.budget_manager.is_within_budget(estimated_cost, dynamic_limit=dynamic_limit):
            print(f"✔️ [TokenGuard] Prompt within strict budget (${estimated_cost:.5f})")
            return prompt, req_id
            
        print(f"\n⚠️  [TokenGuard] BUDGET EXCEEDED: Cost (${estimated_cost:.5f}) is too high!")
        print(f"🔄 [TokenGuard] Sending {token_count} tokens to Local Ollama for compression...")
        
        start_time = time.time()
        compressed_prompt = self.compressor.compress(prompt)
        compression_ms = (time.time() - start_time) * 1000
        
        if not compressed_prompt:
            print("❌ [TokenGuard] Compression failed! Proceeding with original prompt.")
            return prompt, req_id
            
        comp_token_count, _ = self.tokenizer.count(compressed_prompt)
        comp_estimated_cost = CostCalculator.calculate_input_cost(comp_token_count)
        
        print(f"📉 [TokenGuard] Compression Successful!")
        print(f"   ➤ Tokens: {token_count} ➔ {comp_token_count}")
        print(f"   ➤ Cost  : ${estimated_cost:.5f} ➔ ${comp_estimated_cost:.5f}\n")
        
        if auto_approve:
            self.observer.record_compressed_prompt(req_id, comp_token_count, compression_ms, compressed_prompt)
            print("🛡️  [TokenGuard] Auto-approving compressed prompt for execution.")
            return compressed_prompt, req_id
        else:
            user_input = input("Approve compression and use the new prompt? (y/n): ").strip().lower()
            if user_input == 'y':
                self.observer.record_compressed_prompt(req_id, comp_token_count, compression_ms, compressed_prompt)
                print("🛡️  [TokenGuard] Compression approved. Overriding prompt.")
                return compressed_prompt, req_id
            else:
                print("❌ [TokenGuard] Compression rejected. Proceeding with massive prompt.")
                return prompt, req_id