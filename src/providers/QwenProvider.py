"""
QwenProvider — Alibaba Qwen via DashScope API.
Free tier: qwen-turbo
Pro: qwen2.5-72b-instruct, qwen-max
"""

import aiohttp
from typing import List, Dict, Optional

from providers.BaseProvider import BaseProvider


class QwenProvider(BaseProvider):

    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def __init__(self, config):
        super().__init__(config)
        if not self.api_key:
            raise ValueError(
                "QWEN_API_KEY tidak ditemukan. Daftar di dashscope.aliyuncs.com"
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        gen_cfg = self.config.get_generation_config()
        payload = {
            "model": self.model_id,
            "messages": payload_messages,
            "temperature": gen_cfg.get("temperature", 0.7),
            "max_tokens": gen_cfg.get("max_output_tokens", 1024),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.BASE_URL, headers=headers, json=payload
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"Qwen error {resp.status}: {body}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
