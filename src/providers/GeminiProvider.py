"""
GeminiProvider — Google Gemini via REST API.
Bug fix dari versi Jarvis:
  - generation_config & safety_settings sekarang dikirim ke payload
  - system_prompt di-inject sebagai system_instruction
  - history di-convert ke format Gemini contents
"""

import aiohttp
from typing import List, Dict, Optional

from providers.BaseProvider import BaseProvider


class GeminiProvider(BaseProvider):

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, config):
        super().__init__(config)
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY tidak ditemukan di environment variables."
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        url = f"{self.BASE_URL}/{self.model_id}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Convert history ke format Gemini
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload: Dict = {"contents": contents}

        # Inject system prompt
        if system_prompt:
            payload["system_instruction"] = {
                "parts": [{"text": system_prompt}]
            }

        # Inject generation config (FIX dari bug lama)
        gen_cfg = self.config.get_generation_config()
        if gen_cfg:
            payload["generationConfig"] = gen_cfg

        # Inject safety settings
        safety = self.config.get_safety_settings()
        if safety:
            payload["safetySettings"] = safety

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"Gemini error {resp.status}: {body}")
                data = await resp.json()
                return self._parse(data)

    def _parse(self, data: dict) -> str:
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            raise ValueError(f"Gagal parse Gemini response: {e}\n{data}")
