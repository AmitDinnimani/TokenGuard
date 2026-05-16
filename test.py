import asyncio
import logging
import time
from decorators.decorator import guard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# 1. Sync Example
@guard(prompt_arg_name="system_prompt")
def sync_chat(prompt: str, system_prompt: str) -> str:
    return f"Sync Response for prompt length {len(system_prompt)}"

# 2. Async Example
@guard(prompt_arg_name="system_prompt")
async def async_chat(prompt: str, system_prompt: str) -> str:
    await asyncio.sleep(0.1) # Simulate async I/O
    return f"Async Response for prompt length {len(system_prompt)}"


async def main():
    print("--- Starting Production-Grade TokenGuard Demo ---\n")
    
    # Test 1: Sync call with small prompt
    print("Test 1: Sync Normal Prompt")
    res1 = sync_chat("Hello", "You are a helpful assistant.")
    print(f"Result 1: {res1}\n")
    
    # Test 2: Async call with small prompt
    print("Test 2: Async Normal Prompt")
    res2 = await async_chat("Hello", "You are a helpful assistant.")
    print(f"Result 2: {res2}\n")
    
    # Test 3: Async call with huge prompt (triggers compression)
    print("Test 3: Async Large Prompt (Budget Breach)")
    huge_system = "Instructions: " + ("DO NOT FORGET THIS. " * 1000)
    
    # We use a very small limit to force compression
    res3 = await async_chat("Hello", huge_system, limit=0.0001)
    print(f"Result 3: {res3}\n")
    
    print("Demo Complete. Telemetry logged to logs/tokenguard_telemetry.jsonl")

if __name__ == "__main__":
    asyncio.run(main())