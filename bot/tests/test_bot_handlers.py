import asyncio
import datetime as dt
from types import SimpleNamespace

import pytest

# Attempt to import python-telegram-bot. If not present, tests will be skipped.
telegram = pytest.importorskip("telegram")
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.main import start, handle_text, MINI_APP_URL
from backend.app.utils import openrouter
from backend.app.core import config


class DummyMessage:
    def __init__(self, text: str | None = None):
        self.text = text
        self.reply_text_calls = []

    async def reply_text(self, text: str, reply_markup=None):
        self.reply_text_calls.append(SimpleNamespace(text=text, reply_markup=reply_markup))


class DummyUpdate:
    def __init__(self, text: str | None = None):
        self.message = DummyMessage(text)


class DummyContext(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_start_sends_greeting_with_mini_app_button():
    update = DummyUpdate()
    context = DummyContext()

    await start(update, context)

    assert update.message.reply_text_calls, "start handler did not send a message"
    call = update.message.reply_text_calls[0]
    assert "Welcome to the Ontario Tax bot" in call.text
    assert "This is not professional tax advice." in call.text
    assert isinstance(call.reply_markup, InlineKeyboardMarkup)
    button = call.reply_markup.inline_keyboard[0][0]
    assert isinstance(button, InlineKeyboardButton)
    assert button.url == MINI_APP_URL


@pytest.mark.asyncio
async def test_handle_text_uses_openrouter_when_api_key(monkeypatch):
    update = DummyUpdate("Tax planning strategies")
    context = DummyContext()

    monkeypatch.setattr(config.settings, "OPENROUTER_API_KEY", "test")
    mock_chat = pytest.importorskip("unittest").mock.AsyncMock(return_value="AI reply")
    monkeypatch.setattr(openrouter, "chat_completion", mock_chat)

    await handle_text(update, context)

    mock_chat.assert_awaited_once()
    call = update.message.reply_text_calls[0]
    assert call.text == "AI reply\n\nThis is not professional tax advice."


@pytest.mark.asyncio
async def test_handle_text_fallback_loads_tax_data(monkeypatch):
    update = DummyUpdate("rrsp strategy")
    context = DummyContext()

    monkeypatch.setattr(config.settings, "OPENROUTER_API_KEY", "")

    year = dt.datetime.now().year
    called = {}

    async def fake_chat_completion(*args, **kwargs):
        raise AssertionError("OpenRouter should not be called in fallback mode")

    monkeypatch.setattr(openrouter, "chat_completion", fake_chat_completion)

    def fake_loader(y):
        called["year"] = y
        return {
            "federal_tax_brackets": [{"rate": 0.1, "upto": 50000}],
            "ontario_tax_brackets": [{"rate": 0.05, "upto": 40000}],
        }

    from bot import main as bot_main

    monkeypatch.setattr(bot_main, "load_tax_year_data", fake_loader)

    await handle_text(update, context)

    assert called["year"] == year
    call = update.message.reply_text_calls[0]
    assert f"{year} Federal tax brackets" in call.text
    assert "10.00% up to $50,000" in call.text
    assert "Ontario tax brackets: 5.00% up to $40,000" in call.text
    assert call.text.endswith("This is not professional tax advice.")
