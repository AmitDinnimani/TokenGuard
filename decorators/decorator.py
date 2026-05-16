import logging
import inspect
import functools
from typing import Optional, Any, Callable, Dict, Tuple
from core.processor import TokenGuardProcessor
from config.config import Config

logger = logging.getLogger("TokenGuard.Decorator")
processor = TokenGuardProcessor()

def guard(limit: Optional[float] = None, prompt_arg_name: Optional[str] = None):
    """
    TokenGuard Decorator. Supports both sync and async functions.
    Intelligently identifies the prompt argument using signature inspection.
    """
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        
        @functools.wraps(func)
        def _get_wrapper():
            if inspect.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs) -> Any:
                    # Extract limit if passed as kwarg, else use decorator default
                    call_limit = kwargs.pop('limit', limit)
                    
                    call_args = sig.bind(*args, **kwargs)
                    call_args.apply_defaults()
                    
                    prompt, key = _find_prompt(call_args.arguments, prompt_arg_name)
                    if not prompt:
                        return await func(*args, **kwargs)

                    final_prompt, req_id = await processor.process_async(prompt, dynamic_limit=call_limit)
                    
                    # Inject final prompt back into arguments
                    call_args.arguments[key] = final_prompt
                    
                    # Reconstruct args/kwargs without 'limit'
                    result = await func(*call_args.args, **call_args.kwargs)
                    _record_completion(req_id, result)
                    return result
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs) -> Any:
                    call_limit = kwargs.pop('limit', limit)

                    call_args = sig.bind(*args, **kwargs)
                    call_args.apply_defaults()
                    
                    prompt, key = _find_prompt(call_args.arguments, prompt_arg_name)
                    if not prompt:
                        return func(*args, **kwargs)

                    final_prompt, req_id = processor.process(prompt, dynamic_limit=call_limit)
                    
                    call_args.arguments[key] = final_prompt
                    
                    result = func(*call_args.args, **call_args.kwargs)
                    _record_completion(req_id, result)
                    return result
                return sync_wrapper

        return _get_wrapper()

    def _find_prompt(arguments: Dict[str, Any], arg_name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Locates the prompt value and its key in the arguments dictionary."""
        # 1. Search by explicit name
        if arg_name and arg_name in arguments:
            return arguments[arg_name], arg_name
        
        # 2. Search by default name 'prompt'
        if 'prompt' in arguments:
            return arguments['prompt'], 'prompt'
            
        # 3. Fallback: First string argument that isn't 'self' or 'cls'
        for k, v in arguments.items():
            if k not in ('self', 'cls') and isinstance(v, str):
                return v, k
                
        return None, None

    def _record_completion(req_id, result):
        try:
            output_tokens, _ = processor.tokenizer.count(str(result))
            processor.observer.record_completion(req_id, output_tokens)
        finally:
            processor.observer.finalize_request(req_id)

    if callable(limit):
        f = limit
        limit = None
        return decorator(f)
        
    return decorator