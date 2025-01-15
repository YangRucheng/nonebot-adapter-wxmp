from nonebot import on_message, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from pathlib import Path
import asyncio
import os

from nonebot.adapters.wxmp import MiniprogramEvent, MessageSegment, Bot, File


async def rule_test(
    event: MiniprogramEvent
):
    """ 小程序测试 """
    return True


@on_command("文本2", rule=rule_test, priority=0).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: MiniprogramEvent,
):
    await bot.send(
        event=event,
        message=MessageSegment.text("Hello, world!"),
    )


@on_command("链接2", rule=rule_test, priority=0).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: MiniprogramEvent,
):
    await bot.send(
        event=event,
        message=MessageSegment.link(
            title="Hello, world!",
            description="This is a test message.",
            url="https://github.com/YangRucheng/nonebot-adapter-wxmp",
            thumb_url="https://nonebot.dev/logo.png",
        )
    )


@on_command("小程序2", rule=rule_test, priority=0).handle()
async def handle_test(
    bot: Bot,
    mather: Matcher,
    event: MiniprogramEvent,
):
    """ 测试发送消息 """
    await bot.send(
        event=event,
        message=MessageSegment.miniprogrampage(
            title="Hello, world!",
            page_path="pages/home/home",
            thumb_media_path=Path("/app/res/demo.png"),
        )
    )


@on_command("图片2", rule=rule_test, priority=0).handle()
async def handle_test(
    bot: Bot,
    mather: Matcher,
    event: MiniprogramEvent,
):
    """ 测试发送消息 """
    await bot.send(
        event=event,
        message=MessageSegment.image(
            file_path=Path("/app/res/demo.png"),
        )
    )
