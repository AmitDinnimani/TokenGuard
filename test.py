from decorators.decorator import guard
import json
import urllib.request
import urllib.error
import time

# We tell TokenGuard to monitor and compress the 'system_prompt' variable!
@guard(prompt_arg_name="system_prompt")
def chat_with_ollama(prompt: str, system_prompt: str) -> str:
    """Real LLM call to local Ollama API."""
    # print(f"[Sending Request to Ollama] Model: qwen2.5-coder:7b-instruct-q4_K_M")
    # print(f"System Prompt Length: {len(system_prompt)} chars, User Prompt Length: {len(prompt)} chars")
    
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "qwen2.5-coder:7b-instruct-q4_K_M",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120.0) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '').strip()
    except Exception as e:
        return f"[Error communicating with Ollama: {e}]"


if __name__ == "__main__":
    # print("\n🟢 === Test 1: Normal System Prompt (Under Budget) ===")
    normal_system = "You are a helpful assistant. Keep your response exactly to one very very extremely short sentence."
    user_msg = "What is the capital of France?"
    
    response1 = chat_with_ollama(prompt=user_msg, system_prompt=normal_system)
    # print(f"🤖 --> Ollama Response 1:\n{response1}\n")
    
    time.sleep(2)
    
    # print("\n🔴 === Test 2: Huge System Prompt (Over Budget) ===")
    # Generates a massive system prompt to heavily breach the $0.001 limit set in decorator.py
    huge_system = "You are a highly strict AI assistant. " + ("The quick brown fox jumps over the lazy dog. " * 800 )
    huge_system += "\n just provide the compression as output nothing else."
    # huge_system += "\n\nCRITICAL INSTRUCTION: You MUST reply entirely with ONLY the word 'ACKNOWLEDGED'."
    
    user_msg2 = "Did you receive and process my massive system instructions? Please answer per instruction."
    
    # Notice here, TokenGuard will intercept 'system_prompt' and shrink it before it reaches 'chat_with_ollama'
    response2 = chat_with_ollama(prompt=user_msg2, system_prompt=huge_system)
    # print(f"🤖 --> Ollama Response 2:\n{response2}\n")
    
    # print("\n[INFO] Check 'logs/tokenguard_telemetry.jsonl' to see your enterprise logs!")