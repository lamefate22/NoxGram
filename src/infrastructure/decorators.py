from src.infrastructure.logger import log
from asyncio import iscoroutinefunction
from typing import Callable
import functools


def debug(mask_call_info: bool = False):
    """Debugging decorator for detailed logging."""
    def decorator(func) -> Callable:
        def get_call_info(*args, **kwargs) -> str:
            if mask_call_info:
                return "masked"

            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            return ", ".join(args_repr + kwargs_repr)

        if iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                call_info = get_call_info(*args, **kwargs)
                log.debug(f"entering: {func.__name__} ({call_info})")
                try:
                    result = await func(*args, **kwargs)
                    log.debug(f"exiting: {func.__name__} (returned {repr(result) if not mask_call_info else 'masked'})")
                    return result
                except Exception:
                    log.exception("exception raised while calling async function: {}".format(func.__name__))
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                call_info = get_call_info(*args, **kwargs)
                log.debug(f"entering: {func.__name__} ({call_info})")
                try:
                    result = func(*args, **kwargs)
                    log.debug(f"exiting: {func.__name__} (returned {repr(result) if not mask_call_info else 'masked'})")
                    return result
                except Exception:
                    log.exception("exception raised while calling sync function: {}".format(func.__name__))
                    raise
            return sync_wrapper
    return decorator
