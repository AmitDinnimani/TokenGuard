import logging
import httpx
from typing import Optional
from config.config import Config
from compression.base import AbstractCompressor

class OllamaCompressor(AbstractCompressor):
    def __init__(self, endpoint: Optional[str] = None, model: Optional[str] = None, timeout: Optional[float] = None):
        """
        Compressor that uses a local/cloud Ollama model.
        Supports both sync and async via httpx.
        """
        self.endpoint = endpoint or Config.OLLAMA_ENDPOINT
        self.model = model or Config.OLLAMA_MODEL
        self.timeout = timeout or Config.OLLAMA_TIMEOUT
        self.logger = logging.getLogger("TokenGuard.Compressor")
        
        self.system_prompt = (
            "You are an expert prompt compressor. Your goal is to drastically reduce "
            "the length of the provided text while preserving its exact semantic meaning, "
            "critical variables, code snippets, and instructions for a downstream LLM.\n\n"
            "STRICT RULES:\n"
            "1. Remove all conversational filler, pleasantries, and redundant explanations.\n"
            "2. Keep all code, system commands, JSON, variables, and precise terminology exactly as written.\n"
            "3. Use abbreviations or shorter phrasing where it does not lose context.\n"
            "4. NEVER output any introductory phrases like 'Here is the compressed text:' or 'Compressed:'.\n"
            "5. The output must ONLY contain the compressed prompt itself."
        )

    def _prepare_payload(self, text: str) -> dict:
        return {
            "model": self.model,
            "prompt": text,
            "system": self.system_prompt,
            "stream": False
        }

    def compress(self, text: str) -> Optional[str]:
        """Synchronously compress the input text."""
        payload = self._prepare_payload(text)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.endpoint, json=payload)
                response.raise_for_status()
                return response.json().get('response', '').strip()
        except Exception as e:
            self.logger.error(f"Sync compression failed: {e}")
            return None

    async def compress_async(self, text: str) -> Optional[str]:
        """Asynchronously compress the input text."""
        payload = self._prepare_payload(text)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                return response.json().get('response', '').strip()
        except Exception as e:
            self.logger.error(f"Async compression failed: {e}")
            return None

    def is_healthy(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            # We check the base tags endpoint or just a simple ping
            health_url = self.endpoint.replace("/api/generate", "/api/tags")
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                return response.status_code == 200
        except Exception:
            return False

    async def is_healthy_async(self) -> bool:
        """Asynchronously check if Ollama is reachable."""
        try:
            health_url = self.endpoint.replace("/api/generate", "/api/tags")
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                return response.status_code == 200
        except Exception:
            return False