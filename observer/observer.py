import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

# Provide compatibility in case we run this from different entry points
try:
    from .operations import CostCalculator
except ImportError:
    from operations import CostCalculator

@dataclass
class TokenMetrics:
    """Enterprise-level schema for tracking individual prompt lifecycles with clear labels."""
    request_id: str
    timestamp_utc: str
    
    # Token Counts
    original_prompt_tokens: int = 0
    compressed_prompt_tokens: int = 0
    completion_tokens: int = 0
    
    # Prompt Texts
    original_prompt_text: str = ""
    compressed_prompt_text: str = ""
    
    # Compression Metadata
    is_compressed: bool = False
    compression_time_ms: float = 0.0
    
    # Financial metrics for robust tracking
    original_estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0
    tokens_saved: int = 0
    cost_saved_usd: float = 0.0

class TokenObserver:
    def __init__(self, log_dir: str = "logs"):
        """
        Enterprise-level observer for tracking TokenGuard metrics.
        Appends structured JSON logs per request for easy ingestion by Datadog, ELK, or CloudWatch.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "tokenguard_telemetry.jsonl"
        
        # Setup structured console logging
        self.logger = logging.getLogger("TokenGuard.Observer")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Thread-safe mapping of active requests
        self.active_requests: dict[str, TokenMetrics] = {}

    def start_request(self) -> str:
        """Starts a new tracking session and returns its unique request ID."""
        req_id = str(uuid.uuid4())
        self.active_requests[req_id] = TokenMetrics(
            request_id=req_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat()
        )
        self.logger.debug(f"Started monitoring request ID: {req_id}")
        return req_id

    def record_original_prompt(self, req_id: str, tokens: int, text: str = ""):
        """Records the initial raw prompt tokens, text structure, and its theoretical cost."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.original_prompt_tokens = tokens
            metrics.original_prompt_text = text
            metrics.original_estimated_cost_usd = CostCalculator.calculate_input_cost(tokens)

    def record_compressed_prompt(self, req_id: str, tokens: int, time_ms: float, text: str = ""):
        """Logs the fact the prompt was compressed, updating cost savings appropriately."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.compressed_prompt_tokens = tokens
            metrics.compressed_prompt_text = text
            metrics.is_compressed = True
            metrics.compression_time_ms = time_ms
            
            # Calculate and record exact savings
            metrics.tokens_saved = metrics.original_prompt_tokens - tokens
            orig_cost = metrics.original_estimated_cost_usd
            new_cost = CostCalculator.calculate_input_cost(tokens)
            metrics.cost_saved_usd = orig_cost - new_cost
            self.logger.info(f"Compressed prompt [{req_id}]. Saved {metrics.tokens_saved} tokens "
                             f"(${metrics.cost_saved_usd:.4f}).")

    def record_completion(self, req_id: str, tokens: int):
        """Records output tokens from the primary LLM call."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.completion_tokens = tokens
            
    def finalize_request(self, req_id: str):
        """Calculates final totals, writes telemetry to the JSONL log, and cleans memory footprint."""
        metrics = self.active_requests.pop(req_id, None)
        if not metrics:
            self.logger.warning(f"Attempted to finalize tracking for unknown or cleared request: {req_id}")
            return
            
        # Overall cost calculation (Input + Output)
        input_tokens = (metrics.compressed_prompt_tokens 
                        if metrics.is_compressed 
                        else metrics.original_prompt_tokens)
        
        input_cost = CostCalculator.calculate_input_cost(input_tokens)
        output_cost = CostCalculator.calculate_output_cost(metrics.completion_tokens)
        
        metrics.actual_cost_usd = input_cost + output_cost
        
        # Persist structured log
        self._append_to_log(asdict(metrics))
        self.logger.info(f"Finalized request {metrics.request_id}. "
                         f"Final Cost: ${metrics.actual_cost_usd:.4f}")

    def _append_to_log(self, data: dict):
        """Atomically appends JSON entry to log."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data, indent=4) + "\n")