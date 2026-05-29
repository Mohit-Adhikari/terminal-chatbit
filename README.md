# Chatbox

A simple command-line chatbot that can talk through either Google Gemini or a local Ollama server.

## Features

- Interactive terminal chat loop
- Provider selection: `gemini` or `ollama`
- Optional thinking mode
- Structured responses validated with Pydantic

## Requirements

- Python 3.12 or later
- `uv` recommended for dependency management and running the app
- Internet access and a valid Gemini API key for the `gemini` provider
- A running Ollama instance for the `ollama` provider

## Setup

Clone the repository, then install dependencies:

```bash
uv sync
```

If you prefer a virtual environment manually, install the dependencies listed in `pyproject.toml` and make sure the project is available on your Python path.

## Configuration

Create a `.env` file in the project root for the provider you want to use.

### Gemini

Set your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

### Ollama

Set the Ollama endpoint:

```env
OLLAMA_URL=http://localhost:11434/api/chat
```

Make sure Ollama is running locally and that the model referenced in the code is installed and available.

## Run

Start the chatbot from the repository root:

```bash
uv run python -m chatbox.main
```

By default, the app uses Gemini. You can choose a provider and enable thinking mode with CLI flags:

```bash
uv run python -m chatbox.main --provider gemini --thinking false
uv run python -m chatbox.main --provider ollama --thinking true
```

## Usage

After the chatbot starts, type a message and press Enter. Type `exit` to end the session.

## Logging

Runtime logs are written to `app.log` in the project root.

## Troubleshooting

- If Gemini requests fail, confirm `GEMINI_API_KEY` is set in your environment.
- If Ollama requests fail, confirm the Ollama server is running and the URL points to the correct chat endpoint.
- If you see import errors, run the command from the repository root so the local package layout resolves correctly.

## Project Structure

```text
src/
	chatbox/
		main.py
		app/
			gemini/
			ollama/
			schema/
```
