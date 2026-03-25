import json
import os

def calculate_input_cost(token_len):
    return token_len * 0.00025

def calculate_output_cost(token_len):
    return token_len * 0.002

def calculate_compression_ratio(original_tokens, compressed_tokens):
    if original_tokens == 0:
        return 0.0
    return compressed_tokens / original_tokens

def calculate_total_cost(input_cost, output_cost):
    return input_cost + output_cost

def calculate_total_tokens(input_tokens, output_tokens):
    return input_tokens + output_tokens

def calculate_tokens_saved(original_tokens, compressed_tokens):
    return original_tokens - compressed_tokens

def calculate_cost_saved(original_cost, compressed_cost):
    return original_cost - compressed_cost

def load_existing_metadata():
    if os.path.exists("metadata.json"):
        try:
            with open("metadata.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
            
    return {
        "total_tokens": 0,
        "total_cost": 0.0,
        "total_input_cost": 0.0,
        "total_output_cost": 0.0,
        "total_compressed_tokens": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens_saved": 0,
        "total_cost_saved": 0.0,
        "total_requests": 0,
        "successful_compressions": 0,
        "failed_compressions": 0
    }

def generate_updated_metadata(current_report):
    metadata = load_existing_metadata()
    
    orig_tokens = current_report["original_tokens"]
    final_in_tokens = current_report["final_input_tokens"]
    out_tokens = current_report["output_tokens"]
    
    orig_in_cost = calculate_input_cost(orig_tokens)
    final_in_cost = calculate_input_cost(final_in_tokens)
    out_cost = calculate_output_cost(out_tokens)
    
    metadata["total_tokens"] += calculate_total_tokens(final_in_tokens, out_tokens)
    metadata["total_cost"] += calculate_total_cost(final_in_cost, out_cost)
    metadata["total_input_cost"] += final_in_cost
    metadata["total_output_cost"] += out_cost
    
    if orig_tokens != final_in_tokens:
        metadata["total_compressed_tokens"] += orig_tokens
        
    metadata["total_input_tokens"] += final_in_tokens
    metadata["total_output_tokens"] += out_tokens
    
    metadata["total_tokens_saved"] += calculate_tokens_saved(orig_tokens, final_in_tokens)
    metadata["total_cost_saved"] += calculate_cost_saved(orig_in_cost, final_in_cost)
    
    metadata["total_requests"] += 1
    metadata["successful_compressions"] += current_report["successful_compressions"]
    metadata["failed_compressions"] += current_report["failed_compressions"]
    
    return metadata