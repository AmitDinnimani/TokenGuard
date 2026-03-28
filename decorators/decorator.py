from functools import wraps
from core.processor import TokenGuardProcessor

# Instantiate a global processor with a strict limit for demo purposes ($0.001)
processor = TokenGuardProcessor(limit=0.001)

def guard(limit: float = None, prompt_arg_name: str = None):
    """
    TokenGuard Decorator.
    Intercepts function calls, validates cost budget based on tokens, compresses if necessary, and logs telemetry.
    Can be used with or without arguments: @guard, @guard(limit=0.05), @guard(prompt_arg_name="system_prompt")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prompt = None
            prompt_idx = -1
            
            # Identify where the prompt is. Look for explicit kwarg, implicit 'prompt' kwarg, or fallback to first arg.
            if prompt_arg_name and prompt_arg_name in kwargs:
                prompt = kwargs[prompt_arg_name]
            elif not prompt_arg_name and 'prompt' in kwargs:
                prompt = kwargs['prompt']
            elif len(args) > 0 and isinstance(args[0], str):
                prompt = args[0]
                prompt_idx = 0
            
            if not prompt:
                return func(*args, **kwargs)

            # Delegate to processor orchestrator
            final_prompt, req_id = processor.process(prompt, dynamic_limit=limit)
            
            # Reconstruct function arguments substituting the uncompressed text with the final prompt
            new_args = list(args)
            if prompt_idx >= 0:
                new_args[prompt_idx] = final_prompt
            elif prompt_arg_name:
                kwargs[prompt_arg_name] = final_prompt
            else:
                kwargs['prompt'] = final_prompt
                
            print(f"🚀 [TokenGuard] Executing target function: {func.__name__}()\n")
            result = func(*new_args, **kwargs)
            
            # Post-execution output processing metric tracking
            result_str = str(result)
            output_tokens, _ = processor.tokenizer.count(result_str)
            
            processor.observer.record_completion(req_id, output_tokens)
            processor.observer.finalize_request(req_id)
            
            return result
        return wrapper
    
    # Enable usage of @guard without () safely
    if callable(limit):
        func = limit
        limit = None
        return decorator(func)
        
    return decorator