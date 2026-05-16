import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config.config import Config
from observer.operations import CostCalculator

@dataclass
class TokenMetrics:
    """Production schema for tracking prompt lifecycles."""
    request_id: str
    timestamp_utc: str
    
    # Token Counts
    original_prompt_tokens: int = 0
    compressed_prompt_tokens: int = 0
    completion_tokens: int = 0
    
    # Prompt Texts (Optional: in high-security prod, you might only log tokens)
    original_prompt_text: str = ""
    compressed_prompt_text: str = ""
    
    # Compression Metadata
    is_compressed: bool = False
    compression_time_ms: float = 0.0
    
    # Financial metrics
    original_estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0
    tokens_saved: int = 0
    cost_saved_usd: float = 0.0

class TokenObserver:
    def __init__(self, log_dir: Optional[str] = None):
        """
        Production observer for tracking TokenGuard metrics.
        Appends single-line JSON entries (JSONL) for easy ingestion by log aggregators.
        """
        self.log_dir = Path(log_dir or Config.LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = Path(Config.TELEMETRY_FILE)
        
        self.logger = logging.getLogger("TokenGuard.Observer")
        self.active_requests: dict[str, TokenMetrics] = {}

    def start_request(self) -> str:
        """Starts a new tracking session."""
        req_id = str(uuid.uuid4())
        self.active_requests[req_id] = TokenMetrics(
            request_id=req_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat()
        )
        self.logger.debug(f"Started monitoring request ID: {req_id}")
        return req_id

    def record_original_prompt(self, req_id: str, tokens: int, text: str = ""):
        """Records initial prompt metadata."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.original_prompt_tokens = tokens
            if Config.ENABLE_PROMPT_LOGGING:
                metrics.original_prompt_text = text
            metrics.original_estimated_cost_usd = CostCalculator.calculate_input_cost(tokens)

    def record_compressed_prompt(self, req_id: str, tokens: int, time_ms: float, text: str = ""):
        """Records compression results and savings."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.compressed_prompt_tokens = tokens
            if Config.ENABLE_PROMPT_LOGGING:
                metrics.compressed_prompt_text = text
            metrics.is_compressed = True
            metrics.compression_time_ms = time_ms
            
            metrics.tokens_saved = metrics.original_prompt_tokens - tokens
            orig_cost = metrics.original_estimated_cost_usd
            new_cost = CostCalculator.calculate_input_cost(tokens)
            metrics.cost_saved_usd = max(0.0, orig_cost - new_cost)
            
            self.logger.info(f"Compressed [{req_id}]: Saved {metrics.tokens_saved} tokens "
                             f"(${metrics.cost_saved_usd:.5f})")

    def record_completion(self, req_id: str, tokens: int):
        """Records output tokens."""
        metrics = self.active_requests.get(req_id)
        if metrics:
            metrics.completion_tokens = tokens
            
    def finalize_request(self, req_id: str):
        """Finalizes metrics and persists to JSONL log."""
        metrics = self.active_requests.pop(req_id, None)
        if not metrics:
            self.logger.warning(f"Finalize failed: Unknown request ID {req_id}")
            return
            
        input_tokens = metrics.compressed_prompt_tokens if metrics.is_compressed else metrics.original_prompt_tokens
        input_cost = CostCalculator.calculate_input_cost(input_tokens)
        output_cost = CostCalculator.calculate_output_cost(metrics.completion_tokens)
        
        metrics.actual_cost_usd = input_cost + output_cost
        
        # Persist as single-line JSON (standard JSONL)
        self._append_to_log(asdict(metrics))
        self.logger.info(f"Finalized {req_id}. Total Cost: ${metrics.actual_cost_usd:.5f}")

    def _append_to_log(self, data: dict):
        """Atomically appends JSON entry to log file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                # Use indent=None for standard JSONL format
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write telemetry to {self.log_file}: {e}")