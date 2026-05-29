(# Chatbox — Ollama Streaming

This project provides a simple CLI chat that streams responses from an Ollama model.


**Run instructions for `src/chatbox/main.py`:**

- **Set Ollama URL:** add an environment variable `OLLAMA_URL` (for example in a `.env` file at the project root) pointing to your Ollama server endpoint.

- **Start the chat (streaming) — preferred (uses `uv` helper):**

```bash
# preferred: use the repo `uv` helper (recommended if present in this workspace)
uv run python -m chatbox.main --thinking=true
uv run python -m chatbox.main --thinking=false
```

- **Usage:** type messages at the prompt. Type `exit` to end the chat session.

- **Notes:**
	- The CLI has been simplified to use Ollama only; Gemini/provider switching has been removed.
	- The provider implementation streams text chunks; word spacing is preserved in streamed output.
	- If the model accidentally emits JSON, the provider prints raw text. You can add extra parsing if you prefer to auto-extract a `chat` field.

**Files of interest:**

- `src/chatbox/main.py` — CLI entrypoint and chat loop.
- `src/chatbox/app/ollama/ollama_provider.py` — async streaming provider implementation for Ollama.

**Troubleshooting:**

- If imports cannot be resolved in your editor, ensure the project root is on `PYTHONPATH` (the CLI temporarily adjusts `sys.path` at runtime to import local providers).
- Check `app.log` for runtime logs.
)

