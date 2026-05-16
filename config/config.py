import os
import logging

class Config:
    """Centralized configuration for TokenGuard."""
    
    # Ollama Settings
    OLLAMA_ENDPOINT = os.getenv("TOKENGUARD_OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
    OLLAMA_MODEL = os.getenv("TOKENGUARD_OLLAMA_MODEL", "qwen2.5-coder:7b-instruct-q4_K_M")
    OLLAMA_TIMEOUT = float(os.getenv("TOKENGUARD_OLLAMA_TIMEOUT", "120.0"))
    
    # Budget Settings
    DEFAULT_BUDGET_LIMIT = float(os.getenv("TOKENGUARD_BUDGET_LIMIT", "0.05"))
    
    # Tokenizer Settings
    TOKENIZER_MODEL = os.getenv("TOKENGUARD_TOKENIZER_MODEL", "gpt-4o-mini")
    
    # Logging Settings
    LOG_LEVEL = os.getenv("TOKENGUARD_LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("TOKENGUARD_LOG_DIR", "logs")
    TELEMETRY_FILE = os.path.join(LOG_DIR, "tokenguard_telemetry.jsonl")
    ENABLE_PROMPT_LOGGING = os.getenv("TOKENGUARD_ENABLE_PROMPT_LOGGING", "true").lower() == "true"


# Configure basic logging for the library
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
