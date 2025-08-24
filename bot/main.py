"""Telegram bot entry point.

Provides a simple interface to explore Ontario tax information.  The bot can
either call OpenRouter for LLM generated responses or fall back to local tax
table summaries.
"""

from __future__ import annotations

import datetime as _dt
import logging
import os
from typing import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from backend.app.core.config import settings
from backend.app.utils.year_data_loader import load_tax_year_data
from backend.app.utils.openrouter import chat_completion


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://ontariotaxapp.com")
KEYWORDS: Iterable[str] = {"tax", "strategy", "rrsp", "rrif"}


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user and link to the mini app."""
    keyboard = [[InlineKeyboardButton("Open Mini App", url=MINI_APP_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Ontario Tax bot!\n"
        "Use this bot to explore RRSP/RRIF strategies and tax brackets.\n"
        "This is not professional tax advice.",
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help text."""
    await update.message.reply_text(
        "/start - introduction to the bot\n"
        "/help - show this message\n"
        "Send a message containing keywords like 'tax', 'strategy', 'RRSP', or 'RRIF'.\n"
        "This is not professional tax advice."
    )


def _format_brackets(brackets: list[dict]) -> str:
    parts = []
    for b in brackets:
        upto = f"${b['upto']:,}" if b.get("upto") else "∞"
        parts.append(f"{b['rate'] * 100:.2f}% up to {upto}")
    return "; ".join(parts)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to text messages with tax info or LLM responses."""
    text = update.message.text or ""
    lowered = text.lower()

    if any(k in lowered for k in KEYWORDS):
        if settings.OPENROUTER_API_KEY:
            try:
                user_query = text
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful Ontario tax assistant.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Provide tax strategy advice for '{user_query}' in Ontario, Canada. "
                            "Keep it concise and add disclaimers."
                        ),
                    },
                ]
                reply = await chat_completion(messages)
            except Exception:
                logger.exception("OpenRouter request failed")
                reply = (
                    "Sorry, I couldn't reach the tax service right now."
                )
        else:
            year = _dt.datetime.now().year
            data = load_tax_year_data(year)
            federal = _format_brackets(data.get("federal_tax_brackets", []))
            ontario = _format_brackets(data.get("ontario_tax_brackets", []))
            reply = (
                f"{year} Federal tax brackets: {federal}. "
                f"Ontario tax brackets: {ontario}."
            )
        reply += "\n\nThis is not professional tax advice."
    else:
        reply = (
            "I can chat about Ontario tax strategies. Mention tax topics like RRSP or RRIF.\n\n"
            "This is not professional tax advice."
        )

    await update.message.reply_text(reply)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a friendly message."""
    logger.exception("Unhandled exception: %s", context.error)
    if isinstance(update, Update) and update.effective_chat:
        await update.effective_chat.send_message(
            "Oops! Something went wrong. Please try again later."
        )


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.add_error_handler(error_handler)


if __name__ == "__main__":
    application.run_polling()

