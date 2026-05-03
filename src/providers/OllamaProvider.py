"""
OllamaProvider — Local LLM via Ollama REST API.
Tidak butuh API key. Jalan di localhost.
Support: llama3, mistral, qwen2.5, gemma2, phi3, dll.
"""

import aiohttp
from typing import List, Dict, Optional

from providers.BaseProvider import BaseProvider


class OllamaProvider(BaseProvider):

    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get_ollama_base_url()

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        url = f"{self.base_url}/api/chat"

        # Build messages dengan system prompt di depan
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": self.model_id,
            "messages": payload_messages,
            "stream": False,
            "options": self.config.get_generation_config(),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"Ollama error {resp.status}: {body}")
                data = await resp.json()
                return data["message"]["content"].strip()
