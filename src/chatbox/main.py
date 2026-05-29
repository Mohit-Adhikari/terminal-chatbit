import argparse
import asyncio
import logging
import os
import sys


APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "app"))
if APP_DIR not in sys.path:
    # Ensure local app providers can be imported when running as a module.
    sys.path.insert(0, APP_DIR)

from ollama.ollama_provider import chat as ollama_chat  # type: ignore[reportMissingImports]


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.ERROR)

    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)


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
        "--thinking",
        type=parse_bool,
        default=False,
        help="Enable or disable thinking mode (true/false).",
    )
    return parser


async def run_chat(thinking: bool) -> None:
    logger.info("Starting chat loop with provider=ollama thinking=%s", thinking)
    print("Chatbot started (type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        logger.info("The user question was: %s",user_input)
        if user_input.lower() == "exit":
            logger.info("User ended chat session")
            break
        print("Bot: ", end="", flush=True)
        async for chunk in ollama_chat(user_input, thinking=thinking):
            print(chunk, end="", flush=True)
        print()


def main(argv: list[str] | None = None) -> None:
    setup_logging()
    args = build_parser().parse_args(argv)
    asyncio.run(run_chat(args.thinking))


if __name__ == "__main__":
    main()
