# 🛡️ TokenGuard

**TokenGuard** is an enterprise-grade Python library designed to monitor, protect, and optimize LLM token budgets in real-time. It acts as an intelligent proxy between your application and your LLM, automatically compressing over-budget prompts using local models (Ollama) to ensure cost-efficiency and system stability.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Asyncio Supported](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)

## ✨ Features

- 🚀 **Hybrid Async/Sync Support**: First-class support for both synchronous and asynchronous Python functions.
- 📉 **Auto-Compression**: Automatically detects budget breaches and compresses prompts using local LLMs (via Ollama).
- 🧠 **Smart Caching**: Built-in LRU caching to avoid redundant compression of identical prompts.
- 📊 **Enterprise Telemetry**: Structured JSONL logging for seamless integration with Datadog, ELK, or CloudWatch.
- 🛡️ **DoS Protection**: Built-in input validation to prevent large-payload memory exhaustion.
- 🔌 **Strategy Pattern**: Extensible architecture to support multiple compression providers (Ollama, OpenAI, local BERT).

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy `.env.example` to `.env` and configure your Ollama endpoint:
```bash
TOKENGUARD_OLLAMA_ENDPOINT=http://localhost:11434/api/generate
TOKENGUARD_OLLAMA_MODEL=qwen2.5-coder:7b-instruct
TOKENGUARD_BUDGET_LIMIT=0.05
```

### 3. Usage

#### Synchronous Functions
```python
from tokenguard.decorators.decorator import guard

@guard(limit=0.001)
def generate_text(prompt: str):
    # If 'prompt' is too expensive, it will be auto-compressed before reaching here
    return llm_call(prompt)
```

#### Asynchronous Functions
```python
from tokenguard.decorators.decorator import guard

@guard(prompt_arg_name="system_message")
async def chat_async(user_input: str, system_message: str):
    # 'system_message' will be compressed if it exceeds the token budget
    return await async_llm_call(system_message, user_input)
```

## 🏗️ Architecture

TokenGuard follows a clean, decoupled architecture:
- **Processors**: Orchestrate the token counting and compression logic.
- **Compressors**: Pluggable strategies for prompt reduction (Ollama, etc.).
- **Observers**: Handle high-performance telemetry and cost calculation.
- **Decorators**: Provide a zero-boilerplate integration layer for developers.

## 🧪 Testing

Run the standard test suite:
```bash
python tests/test_core.py
```

Run the production demonstration:
```bash
python test.py
```

## 🛡️ Security

TokenGuard is built with security in mind:
- **PII Filtering**: Optionally disable prompt logging in telemetry via `TOKENGUARD_ENABLE_PROMPT_LOGGING=false`.
- **Input Validation**: Hard limits on input character size to prevent DoS attacks.
- **Secret Management**: All configurations are managed via environment variables.

## 📄 License

MIT © [Amit Dinnimani](https://github.com/AmitDinnimani)
