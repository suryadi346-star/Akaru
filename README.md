
# Akaru — The Shadow Architect

![Akaru AI Logo](assets/logo.png)

> Multi-provider AI assistant. Voice & text. Runs on Termux.

---

## Providers

| Provider | Model Default | Free Tier | Key |
|----------|--------------|-----------|-----|
| **Gemini** | `gemini-2.0-flash` | ✅ | `GEMINI_API_KEY` |
| **Groq** | `llama3-70b-8192` | ✅ | `GROQ_API_KEY` |
| **Qwen** | `qwen-turbo` | ✅ | `QWEN_API_KEY` |
| **Ollama** | `llama3.2` | ✅ Local | — |
| **Claude** | `claude-sonnet-4-20250514` | ❌ | `ANTHROPIC_API_KEY` |
| **OpenAI** | `gpt-4o-mini` | ❌ | `OPENAI_API_KEY` |

---

## Instalasi

```bash
git clone https://github.com/suryadi346-star/Akaru.git
cd Akaru
pip install -r requirements.txt
cp .env.example .env
```

Isi `.env` sesuai provider yang dipilih:

```env
GEMINI_API_KEY=your_key_here
```

---

## Konfigurasi

Edit `config.yml` untuk ganti provider atau model:

```yaml
provider: "gemini"        # gemini | groq | qwen | ollama | claude | openai
model_id: "gemini-2.0-flash"
system_prompt: "Kamu adalah Akaru..."
```

Untuk Ollama (local), pastikan Ollama sudah jalan:

```bash
ollama serve
ollama pull llama3.2
```

---

## Menjalankan

```bash
cd src
python Akaru.py
```

Pilih mode:
- `[0]` Voice — input suara via Termux API
- `[1]` Text — input keyboard

Ketik `exit` atau `bye` untuk keluar.

---

## Termux Setup (Voice Mode)

```bash
pkg install termux-api
# Izinkan akses mikrofon saat diminta
```

---

## Testing

```bash
python -m pytest tests/ -v
```

24 test cases — ConfigManager, ChatManager, provider routing, security.

---

## Struktur Project

```
akaru/
├── src/
│   ├── Akaru.py              # Entry point
│   ├── Manager/
│   │   ├── ConfigManager.py  # Load config.yml & env vars
│   │   └── ChatManager.py    # Routing provider, history
│   ├── lib/
│   │   └── LibVoice.py       # TTS & STT (Termux)
│   └── providers/
│       ├── BaseProvider.py   # Abstract interface
│       ├── GeminiProvider.py
│       ├── OllamaProvider.py
│       ├── ClaudeProvider.py
│       ├── OpenAIProvider.py
│       ├── GroqProvider.py
│       └── QwenProvider.py
├── tests/
│   └── test_akaru.py
├── config.yml
├── .env.example
└── requirements.txt
```

---

## License

MIT — [suryadi346-star](https://github.com/suryadi346-star)

# Akaru
