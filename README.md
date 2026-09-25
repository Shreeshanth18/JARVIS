# JARVIS

JARVIS is a PyQt desktop assistant with live system telemetry, typed commands, microphone input, speech output, local desktop actions, Wikipedia lookup, and optional OpenAI responses.

## Run

```powershell
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-key-here"
python MAIN.PY
```

The API key is optional for local commands. Without it, general questions return a clear provider-unavailable response instead of fabricated data. Keep the key in the process environment and do not paste it into source files or commit it.

Useful commands include `cpu`, `memory`, `disk`, `system info`, `open <path>`, `open youtube`, `screenshot`, `create file`, `read file`, and `wiki <topic>`.