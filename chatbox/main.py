import argparse
import asyncio
import os
import sys
from typing import Awaitable, Callable

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if APP_DIR not in sys.path:
    # Ensure local app providers can be imported when running as a module.
    sys.path.insert(0, APP_DIR)

from gemini.provider import chat as gemini_chat
from ollama.ollama_provider import chat as ollama_chat

ChatFn = Callable[[str, int, bool], Awaitable[object]]

PROVIDERS: dict[str, ChatFn] = {
    "gemini": gemini_chat,
    "ollama": ollama_chat,
}


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError("Expected a boolean value: true/false")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chatbox command line interface")
    parser.add_argument(
        "--provider",
        choices=sorted(PROVIDERS.keys()),
        default="gemini",
        help="LLM provider to use (gemini or ollama).",
    )
    parser.add_argument(
        "--thinking",
        type=parse_bool,
        default=False,
        help="Enable or disable thinking mode (true/false).",
    )
    return parser


async def run_chat(provider: str, thinking: bool) -> None:
    chat_fn = PROVIDERS[provider]
    print("Chatbot started (type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = await chat_fn(user_input, thinking=thinking)
        print("Bot:", reply.chat)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    asyncio.run(run_chat(args.provider, args.thinking))


if __name__ == "__main__":
    main()
