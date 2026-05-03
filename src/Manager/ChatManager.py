"""
ChatManager — routing multi-provider, history management, system prompt injection.
"""

import asyncio
from typing import List, Dict, Optional

from Manager.ConfigManager import ConfigManager
from providers.GeminiProvider import GeminiProvider
from providers.OllamaProvider import OllamaProvider
from providers.ClaudeProvider import ClaudeProvider
from providers.OpenAIProvider import OpenAIProvider
from providers.GroqProvider import GroqProvider
from providers.QwenProvider import QwenProvider


class ChatManager:
    """
    Single entry point untuk semua interaksi AI.
    Routing ke provider berdasarkan config.yml.
    Menjaga conversation history + system prompt injection.
    """

    PROVIDER_MAP = {
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "groq":   GroqProvider,
        "qwen":   QwenProvider,
    }

    def __init__(self, config: ConfigManager):
        self.config = config
        self.history: List[Dict[str, str]] = []
        self.provider = self._init_provider()

    def _init_provider(self):
        provider_name = self.config.get_active_provider()
        cls = self.PROVIDER_MAP.get(provider_name)
        if not cls:
            raise ValueError(
                f"Provider '{provider_name}' tidak dikenal. "
                f"Pilihan: {list(self.PROVIDER_MAP.keys())}"
            )
        return cls(self.config)

    def _trim_history(self):
        """Jaga history agar tidak overflow context window."""
        max_h = self.config.get_max_history()
        # Pastikan trim ke angka genap supaya pair user-assistant tetap utuh
        if len(self.history) > max_h:
            excess = len(self.history) - max_h
            # Buang dari awal, pastikan mulai dari pesan user (index genap)
            if excess % 2 != 0:
                excess += 1
            self.history = self.history[excess:]

    async def ask(self, prompt: str) -> str:
        """
        Kirim pesan ke provider aktif dengan full history context.
        """
        self.history.append({"role": "user", "content": prompt})
        self._trim_history()

        try:
            response = await self.provider.generate(
                messages=self.history,
                system_prompt=self.config.get_system_prompt(),
            )
        except Exception as e:
            error_msg = f"[Provider Error] {e}"
            self.history.append({"role": "assistant", "content": error_msg})
            return error_msg

        self.history.append({"role": "assistant", "content": response})
        return response

    def clear_history(self):
        self.history.clear()

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.history)
