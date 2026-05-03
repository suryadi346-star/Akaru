"""
ConfigManager — loads config.yml dan env vars.
"""

import os
import yaml
from typing import Any, Dict, List, Optional, Union


class ConfigManager:
    CONFIG_PATH = "config.yml"

    # Provider default model map
    PROVIDER_DEFAULT_MODELS = {
        "gemini":  "gemini-2.0-flash",
        "ollama":  "llama3.2",
        "claude":  "claude-sonnet-4-20250514",
        "openai":  "gpt-4o-mini",
        "groq":    "llama3-70b-8192",
        "qwen":    "qwen2.5-72b-instruct",
    }

    def __init__(self, config_path: Optional[str] = None):
        self._path = config_path or os.path.abspath(self.CONFIG_PATH)
        self._config: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self._path, "r") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    return {}
                return data
        except FileNotFoundError:
            print(f"[ConfigManager] config.yml tidak ditemukan di {self._path}")
            return {}
        except yaml.YAMLError as e:
            print(f"[ConfigManager] YAML parse error: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def get_active_provider(self) -> str:
        return self.get("provider", "gemini").lower()

    def get_model_id(self) -> str:
        provider = self.get_active_provider()
        default = self.PROVIDER_DEFAULT_MODELS.get(provider, "unknown")
        return self.get("model_id") or default

    def get_api_key(self) -> Optional[str]:
        """
        Ambil API key dari env vars sesuai provider aktif.
        Urutan prioritas: env var spesifik provider → AKARU_API_KEY (universal fallback)
        """
        provider = self.get_active_provider()
        env_map = {
            "gemini": "GEMINI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "groq":   "GROQ_API_KEY",
            "qwen":   "QWEN_API_KEY",
            "ollama": None,  # Ollama local, tidak butuh key
        }
        env_var = env_map.get(provider)
        if env_var:
            key = os.getenv(env_var) or os.getenv("AKARU_API_KEY")
            return key
        return None  # Ollama

    def get_ollama_base_url(self) -> str:
        return self.get("ollama_base_url", "http://localhost:11434")

    def get_system_prompt(self) -> str:
        return self.get(
            "system_prompt",
            "Kamu adalah Akaru, AI asisten taktis yang to-the-point, kritis, dan efisien."
        )

    def get_generation_config(self) -> Dict[str, Any]:
        return self.get("generation_config", {})

    def get_safety_settings(self) -> List[Dict[str, str]]:
        return self.get("safety_settings", [])

    def get_max_history(self) -> int:
        return int(self.get("max_history", 20))
