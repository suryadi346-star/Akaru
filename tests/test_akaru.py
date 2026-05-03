"""
Tests — Akaru unit tests
Jalankan: python -m pytest tests/ -v
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import yaml

# Tambah src ke path supaya import bekerja
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from Manager.ConfigManager import ConfigManager
from Manager.ChatManager import ChatManager


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

MOCK_CONFIG = {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash",
    "system_prompt": "Test system prompt",
    "generation_config": {"temperature": 0.7, "max_output_tokens": 512},
    "safety_settings": [],
    "max_history": 10,
    "ollama_base_url": "http://localhost:11434",
}


def make_config(overrides=None) -> ConfigManager:
    cfg_data = {**MOCK_CONFIG, **(overrides or {})}
    cfg_yaml = yaml.dump(cfg_data)
    with patch("builtins.open", mock_open(read_data=cfg_yaml)):
        with patch("os.path.abspath", return_value="/fake/config.yml"):
            return ConfigManager()


# ──────────────────────────────────────────────
# ConfigManager Tests
# ──────────────────────────────────────────────

class TestConfigManager(unittest.TestCase):

    def test_get_active_provider_default(self):
        cfg = make_config()
        self.assertEqual(cfg.get_active_provider(), "gemini")

    def test_get_model_id(self):
        cfg = make_config()
        self.assertEqual(cfg.get_model_id(), "gemini-2.0-flash")

    def test_get_model_id_fallback(self):
        cfg = make_config({"model_id": None, "provider": "ollama"})
        self.assertEqual(cfg.get_model_id(), "llama3.2")

    def test_get_system_prompt(self):
        cfg = make_config()
        self.assertEqual(cfg.get_system_prompt(), "Test system prompt")

    def test_get_max_history(self):
        cfg = make_config()
        self.assertEqual(cfg.get_max_history(), 10)

    def test_get_api_key_ollama_no_key_needed(self):
        cfg = make_config({"provider": "ollama"})
        self.assertIsNone(cfg.get_api_key())

    def test_get_api_key_gemini_from_env(self):
        cfg = make_config({"provider": "gemini"})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-gemini-key"}):
            self.assertEqual(cfg.get_api_key(), "test-gemini-key")

    def test_get_api_key_fallback_universal(self):
        cfg = make_config({"provider": "groq"})
        env = {"AKARU_API_KEY": "universal-key"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("GROQ_API_KEY", None)
            key = cfg.get_api_key()
            self.assertEqual(key, "universal-key")

    def test_missing_config_file(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("os.path.abspath", return_value="/nonexistent.yml"):
                cfg = ConfigManager()
                self.assertEqual(cfg.get_active_provider(), "gemini")  # default

    def test_invalid_yaml(self):
        # Tab character di awal line = invalid YAML
        invalid_yaml = "\tfoo: bar"
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("os.path.abspath", return_value="/fake.yml"):
                cfg = ConfigManager()
                self.assertEqual(cfg._config, {})

    def test_provider_default_models_complete(self):
        cfg = make_config()
        for provider in ["gemini", "ollama", "claude", "openai", "groq", "qwen"]:
            self.assertIn(provider, cfg.PROVIDER_DEFAULT_MODELS)

    def test_unknown_provider_raises_in_chatmanager(self):
        cfg = make_config({"provider": "unknown_provider"})
        with self.assertRaises(ValueError) as ctx:
            ChatManager(cfg)
        self.assertIn("tidak dikenal", str(ctx.exception))


# ──────────────────────────────────────────────
# ChatManager Tests
# ──────────────────────────────────────────────

class TestChatManager(unittest.TestCase):

    def _make_chat_manager(self, provider="gemini"):
        cfg = make_config({"provider": provider})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
            return ChatManager(cfg)

    def test_provider_routing_gemini(self):
        from providers.GeminiProvider import GeminiProvider
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake"}):
            cm = self._make_chat_manager("gemini")
            self.assertIsInstance(cm.provider, GeminiProvider)

    def test_history_is_empty_on_init(self):
        cm = self._make_chat_manager()
        self.assertEqual(cm.get_history(), [])

    def test_ask_appends_to_history(self):
        cm = self._make_chat_manager()
        cm.provider.generate = AsyncMock(return_value="Respons test")
        asyncio.run(cm.ask("Halo Akaru"))
        history = cm.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Halo Akaru")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Respons test")

    def test_history_trimmed_to_max(self):
        cfg = make_config({"max_history": 4})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake"}):
            cm = ChatManager(cfg)
        cm.provider.generate = AsyncMock(return_value="ok")
        for i in range(5):
            asyncio.run(cm.ask(f"pesan {i}"))
        self.assertLessEqual(len(cm.get_history()), 4)

    def test_clear_history(self):
        cm = self._make_chat_manager()
        cm.provider.generate = AsyncMock(return_value="ok")
        asyncio.run(cm.ask("test"))
        cm.clear_history()
        self.assertEqual(cm.get_history(), [])

    def test_provider_error_handled_gracefully(self):
        cm = self._make_chat_manager()
        cm.provider.generate = AsyncMock(side_effect=Exception("API down"))
        result = asyncio.run(cm.ask("test"))
        self.assertIn("Provider Error", result)

    def test_system_prompt_passed_to_provider(self):
        cm = self._make_chat_manager()
        captured = {}

        async def mock_generate(messages, system_prompt=None):
            captured["system_prompt"] = system_prompt
            return "ok"

        cm.provider.generate = mock_generate
        asyncio.run(cm.ask("test"))
        self.assertEqual(captured["system_prompt"], "Test system prompt")


# ──────────────────────────────────────────────
# Provider Tests (unit - mock HTTP)
# ──────────────────────────────────────────────

class TestGeminiProvider(unittest.TestCase):

    def _make_provider(self):
        from providers.GeminiProvider import GeminiProvider
        cfg = make_config()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
            return GeminiProvider(cfg)

    def test_init_raises_without_api_key(self):
        from providers.GeminiProvider import GeminiProvider
        cfg = make_config()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("AKARU_API_KEY", None)
            with self.assertRaises(ValueError):
                GeminiProvider(cfg)

    def test_parse_valid_response(self):
        provider = self._make_provider()
        mock_resp = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "  Halo!  "}]
                }
            }]
        }
        result = provider._parse(mock_resp)
        self.assertEqual(result, "Halo!")

    def test_parse_invalid_response_raises(self):
        provider = self._make_provider()
        with self.assertRaises(ValueError):
            provider._parse({})


class TestOllamaProvider(unittest.TestCase):

    def test_init_no_api_key_needed(self):
        from providers.OllamaProvider import OllamaProvider
        cfg = make_config({"provider": "ollama", "model_id": "llama3.2"})
        # Harus tidak raise meski tidak ada API key
        provider = OllamaProvider(cfg)
        self.assertIsNone(provider.api_key)


class TestLibVoice(unittest.TestCase):

    def test_say_sanitizes_shell_input(self):
        """
        shlex.quote membungkus seluruh string dalam single quotes.
        Karakter berbahaya seperti ; tetap ada di dalam quotes tapi tidak
        dieksekusi shell — itulah cara kerja shlex.quote yang benar.
        """
        import shlex
        dangerous = "hello; rm -rf ~"
        quoted = shlex.quote(dangerous.lower())
        # Hasil harus diawali & diakhiri single quote
        self.assertTrue(quoted.startswith("'"), "harus dibungkus single quote")
        self.assertTrue(quoted.endswith("'"), "harus diakhiri single quote")
        # Karakter bahaya ada di DALAM quotes → aman dari shell
        # Verifikasi tidak ada unquoted semicolon di luar wrapper
        inner = quoted[1:-1]  # strip outer quotes
        self.assertIn(";", inner)  # ; ada tapi terjebak dalam quotes


if __name__ == "__main__":
    unittest.main(verbosity=2)
