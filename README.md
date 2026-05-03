
# Akaru — The Shadow Architect

![AeroCore AI Logo](assets/logo.png)



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


<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Background gradient -->
  <defs>
    <linearGradient id="shadowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a0f"/>
      <stop offset="50%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#2d1b4e"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Base circle -->
  <circle cx="100" cy="100" r="95" fill="url(#shadowGrad)" stroke="#7b61ff" stroke-width="1.5"/>

  <!-- Geometric A -->
  <path d="M100 45 L65 145 L85 145 L92 120 L108 120 L115 145 L135 145 Z" 
        fill="none" stroke="#7b61ff" stroke-width="3" stroke-linejoin="round"/>
  <line x1="88" y1="105" x2="112" y2="105" stroke="#7b61ff" stroke-width="3" stroke-linecap="round"/>

  <!-- Network nodes -->
  <circle cx="70" cy="70" r="3" fill="#00d4aa" filter="url(#glow)"/>
  <circle cx="130" cy="70" r="3" fill="#00d4aa" filter="url(#glow)"/>
  <circle cx="100" cy="160" r="3" fill="#ff6b9d" filter="url(#glow)"/>
  <line x1="70" y1="70" x2="85" y2="90" stroke="#00d4aa" stroke-width="0.5" opacity="0.6"/>
  <line x1="130" y1="70" x2="115" y2="90" stroke="#00d4aa" stroke-width="0.5" opacity="0.6"/>

  <!-- Subtle waveform -->
  <path d="M60 175 Q80 170, 100 175 T140 175" 
        fill="none" stroke="#7b61ff" stroke-width="1" opacity="0.5"/>
 
  <!-- Terminal cursor -->
  <rect x="155" y="155" width="8" height="2" fill="#00d4aa" opacity="0.8">
    <animate attributeName="opacity" values="0.8;0.3;0.8" dur="1.5s" repeatCount="indefinite"/>
  </rect>
</svg>
# Akaru
