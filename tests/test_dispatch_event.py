import asyncio
from pathlib import Path

import nonebot.adapters

nonebot.adapters.__path__.append(str(Path(__file__).resolve().parents[1] / "nonebot" / "adapters"))

from nonebot.adapters.wxmp.adapter import Adapter


class _DummyBotInfo:
    type = "official"


class _DummyBot:
    bot_info = _DummyBotInfo()

    async def handle_event(self, event):
        raise AssertionError("handle_event should not be called when payload parsing fails")


def test_dispatch_event_parse_error_for_official_bot_returns_success():
    adapter = object.__new__(Adapter)
    adapter.tasks = set()

    def _raise_parse_error(bot, payload):
        raise ValueError("parse failed")

    adapter.payload_to_event = _raise_parse_error

    response = asyncio.run(adapter.dispatch_event(bot=_DummyBot(), payload={}, timeout=0.01))

    assert response.status_code == 200
    assert response.content == "success"
    assert not adapter.tasks
