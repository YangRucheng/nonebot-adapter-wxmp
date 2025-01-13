from nonebot import on_message, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from pathlib import Path
import asyncio
import os

from nonebot.adapters.wxmp import OfficalEvent, MessageSegment, Bot, File


async def rule_test(
    event: OfficalEvent
):
    """ 公众号事件 """
    return True


@on_command("文本", rule=rule_test).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: OfficalEvent,
):
    await bot.send(
        event=event,
        message="测试文本（被动回复消息）")

    await asyncio.sleep(10)
    await bot.send(
        event=event,
        message="测试文本（客服消息）")


@on_command("图片", rule=rule_test).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: OfficalEvent,
):
    media_id = await bot.upload_temp_media(File(file_path=Path(os.getcwd()) / "res/demo.png", file_type="image"))
    await bot.send(
        event=event,
        message=MessageSegment.image(
            media_id=media_id,
        )
    )

    await asyncio.sleep(10)
    await bot.send(
        event=event,
        message=MessageSegment.image(
            media_id=media_id,
        )
    )


@on_command("音频", rule=rule_test).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: OfficalEvent,
):
    media_id = await bot.upload_temp_media(File(file_path=Path(os.getcwd()) / "res/demo.mp3", file_type="voice"))
    await bot.send(
        event=event,
        message=MessageSegment.voice(
            media_id=media_id,
        )
    )

    await asyncio.sleep(10)
    await bot.send(
        event=event,
        message=MessageSegment.voice(
            media_id=media_id,
        )
    )


@on_command("视频", rule=rule_test).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: OfficalEvent,
):
    media_id = await bot.upload_temp_media(File(file_path=Path(os.getcwd()) / "res/demo.mp4", file_type="video"))
    await bot.send(
        event=event,
        message=MessageSegment.video(
            media_id=media_id,
            title="示例视频[被动消息]",
            description="这是一个示例视频",
        )
    )

    await asyncio.sleep(10)
    await bot.send(
        event=event,
        message=MessageSegment.video(
            media_id=media_id,
            title="示例视频[客服消息]",
            description="这是一个示例视频",
        )
    )


@on_command("小程序", rule=rule_test).handle()
async def handle(
    bot: Bot,
    mather: Matcher,
    event: OfficalEvent,
):
    media_id = await bot.upload_temp_media(File(file_path=Path(os.getcwd()) / "res/demo.png", file_type="image"))
    await bot.send(
        event=event,
        message=MessageSegment.miniprogrampage(
            title="示例小程序",
            appid="wx0ba7981861be3afc",
            page_path="pages/home/home",
            thumb_media_id=media_id,
        )
    )
