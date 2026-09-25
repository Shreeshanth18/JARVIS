# JARVIS

JARVIS is a PyQt desktop assistant with live system telemetry, typed commands, microphone input, speech output, local desktop actions, Wikipedia lookup, and optional OpenAI responses.

## Run

```powershell
python -m pip install -r requirements.txt
# Create a local .env file and put your key there.
Copy-Item .env.example .env
Add-Content .env '$env:OPENAI_API_KEY = "paste-your-key-here"'
python MAIN.PY
```

JARVIS loads `.env` automatically at startup. `.env` is ignored by Git; never put a real key in `.env.example` or commit it. The API key is optional for local commands. Without it, general questions return a clear provider-unavailable response instead of fabricated data.

Useful commands include `cpu`, `memory`, `disk`, `system info`, `open <path>`, `open youtube`, `screenshot`, `create file`, `read file`, and `wiki <topic>`.