import json
import socket
import urllib.request
import urllib.error
from typing import Optional

class OllamaCompressor:
    def __init__(self, endpoint: str = "http://localhost:11434/api/generate", model: str = "qwen2.5-coder:7b-instruct-q4_K_M", timeout: float = 120.0):
        """
        Compressor that uses a free local/cloud Ollama model to reduce token count
        without losing context.
        """
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout

    def compress(self, text: str) -> Optional[str]:
        system_prompt = (
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
        
        data = {
            "model": self.model,
            "prompt": text,
            "system": system_prompt,
            "stream": False
        }
        
        req = urllib.request.Request(
            self.endpoint, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '').strip()
        except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
            print(f"[OllamaCompressor] NETWORK/TIMEOUT ERROR contacting Ollama at {self.endpoint}: {e}")
            return None
        except Exception as e:
            print(f"[OllamaCompressor] FATAL ERROR during compression execution: {e}")
            return None