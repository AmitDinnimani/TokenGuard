# 🛡️ TokenGuard

**TokenGuard** is an intelligent assistant for your LLM (Large Language Model) applications. It acts like a "security guard" for your AI costs, making sure you never spend too much on a single request by automatically shrinking large prompts before they are sent to expensive cloud models.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Asyncio Supported](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)

---

## 🤔 What does TokenGuard do?

Imagine you have a monthly budget for an AI service like OpenAI or Anthropic. Occasionally, a user might send a massive document that costs $2.00 just to process. If 1,000 users do that, your budget is gone in minutes.

**TokenGuard solves this by:**
1.  **Watching**: It counts every token in your prompt before it's sent.
2.  **Checking**: It calculates the cost. If the cost is higher than your set limit, it "blows the whistle."
3.  **Shrinking**: Instead of failing, it sends the huge prompt to a **local, free AI** (via Ollama) to summarize and compress it while keeping the important instructions.
4.  **Saving**: It sends the much smaller, cheaper prompt to your main AI, saving you up to 90% in costs.

---

## ✨ Key Features

- ⚡ **Lightning Fast Async**: Works perfectly with modern "async" web apps (like FastAPI) so your users don't wait.
- 📉 **Auto-Compression**: Uses a local model (Ollama) to rewrite long prompts into short, punchy versions that cloud LLMs still understand.
- 🚀 **Smart Memory (Caching)**: If you send the same long prompt twice, TokenGuard remembers the compressed version, making the second time instant.
- 📝 **Detailed Logs (Telemetry)**: Every request is saved in a simple file (`.jsonl`) so you can see exactly how much money you saved at the end of the month.
- 🛡️ **Safety First**: Prevents "Denial of Service" (DoS) attacks by blocking prompts that are way too large for your system to handle.

---

## 🛠️ Installation

### 1. Requirements
Make sure you have [Ollama](https://ollama.com/) installed and running on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Configuration
Create a `.env` file in your project folder (you can copy `.env.example`):

```bash
# Where is your Ollama running?
TOKENGUARD_OLLAMA_ENDPOINT=http://localhost:11434/api/generate

# Which local model should do the shrinking? (Any Ollama model works)
TOKENGUARD_OLLAMA_MODEL=qwen2.5-coder:7b-instruct

# What is the maximum $ cost allowed per request?
TOKENGUARD_BUDGET_LIMIT=0.01
```

---

## 🚀 How to use it

### ⚡ The `@guard` Decorator
Just add `@guard()` on top of any function that takes a prompt. It works for both normal and `async` functions!

```python
from tokenguard.decorators.decorator import guard

# This function is now protected!
@guard(limit=0.005) # Limit this specific call to $0.005
def call_ai(prompt: str):
    return cloud_llm.send(prompt)
```

### 🔧 Manual Usage (Advanced)
If you want more control, you can use the `Processor` directly:

```python
from tokenguard.core.processor import TokenGuardProcessor

processor = TokenGuardProcessor()
# This will return a shrunken prompt if the original is too expensive
safe_prompt, request_id = processor.process("your very long prompt here...")
```

---

## 📁 Project Structure

- `core/`: The brain of the system (token counting, budget checking).
- `compression/`: Logic for shrinking prompts using local models.
- `decorators/`: The easy-to-use `@guard` tool.
- `observer/`: The logging system that tracks your savings.
- `tests/`: Automated checks to make sure everything works correctly.

---

## 🛡️ Privacy & Security

We take your data seriously:
- **Local Compression**: Your "shrunken" prompts never leave your own machine during compression.
- **Privacy Mode**: You can turn off prompt logging to keep your data out of the log files (`TOKENGUARD_ENABLE_PROMPT_LOGGING=false`).
- **Input Limits**: We automatically block prompts larger than 1,000,000 characters to keep your server stable.

---

## 📄 License
MIT © [Amit Dinnimani](https://github.com/AmitDinnimani)
