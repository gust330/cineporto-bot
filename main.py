#!/usr/bin/env python3
"""Main entry point for CinePorto Bot."""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load local .env or fallback to ~/.hermes/.env
load_dotenv()
if not os.getenv("TELEGRAM_BOT_TOKEN"):
    load_dotenv(os.path.expanduser("~/.hermes/.env"))

from cineporto.bot import CinePortoBot
from cineporto.cli import main as cli_main


def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ["--daemon", "--bot"]:
        # Run CLI query mode
        return cli_main()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Aviso: TELEGRAM_BOT_TOKEN não encontrado em .env nem em ~/.hermes/.env")
        print("Para testar no terminal via linha de comandos, execute:")
        print("  python3 main.py \"Nome do Filme\"")
        print("Ou defina TELEGRAM_BOT_TOKEN no ficheiro .env")
        return 1

    bot = CinePortoBot(token=token)
    bot.run_polling()
    return 0


if __name__ == "__main__":
    sys.exit(main())
