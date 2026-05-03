"""
BaseProvider — abstract interface untuk semua AI provider.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from Manager.ConfigManager import ConfigManager


class BaseProvider(ABC):
    """
    Semua provider harus implement generate().
    """

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get_api_key()
        self.model_id = config.get_model_id()

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate response dari list messages format:
        [{"role": "user"/"assistant", "content": "..."}]
        """
        ...
