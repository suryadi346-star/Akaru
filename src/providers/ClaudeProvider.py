"""
ClaudeProvider — Anthropic Claude via Messages API.
Free tier: claude-haiku-4-5 (murah)
Pro: claude-sonnet-4-20250514
"""

import aiohttp
import json
from typing import List, Dict, Optional

from providers.BaseProvider import BaseProvider


class ClaudeProvider(BaseProvider):

    BASE_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(self, config):
        super().__init__(config)
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY tidak ditemukan di environment variables."
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
        }

        gen_cfg = self.config.get_generation_config()
        max_tokens = gen_cfg.get("max_output_tokens", 1024)

        payload: Dict = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "messages": messages,
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.BASE_URL, headers=headers, json=payload
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"Claude error {resp.status}: {body}")
                data = await resp.json()
                return data["content"][0]["text"].strip()
