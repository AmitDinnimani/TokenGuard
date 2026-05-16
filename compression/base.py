from abc import ABC, abstractmethod
from typing import Optional

class AbstractCompressor(ABC):
    """
    Abstract Base Class for all TokenGuard compression strategies.
    Implementations must provide both sync and async compression methods.
    """
    
    @abstractmethod
    def compress(self, text: str) -> Optional[str]:
        """Synchronously compress the input text."""
        pass

    @abstractmethod
    async def compress_async(self, text: str) -> Optional[str]:
        """Asynchronously compress the input text."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the compression service is reachable and responsive."""
        pass

    @abstractmethod
    async def is_healthy_async(self) -> bool:
        """Asynchronously check if the compression service is healthy."""
        pass
