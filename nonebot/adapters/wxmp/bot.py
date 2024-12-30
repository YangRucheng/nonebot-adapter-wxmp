from typing import Union, Any, Optional, Type, TYPE_CHECKING, cast, Literal
from typing_extensions import override
import httpx
import json
import time

from nonebot.message import handle_event
from nonebot.utils import logger_wrapper
from nonebot.adapters import Bot as BaseBot
from nonebot.drivers import Request, Response
from nonebot.exception import (
    ActionFailed,
    NetworkError,
    ApiNotAvailable,
)

from .event import *
from .config import BotInfo
from .message import Message, MessageSegment

if TYPE_CHECKING:
    from .adapter import Adapter


log = logger_wrapper("WXMP")


class Bot(BaseBot):

    @override
    def __init__(self, adapter: "Adapter", self_id: str, bot_info: BotInfo):
        super().__init__(adapter, self_id)
        self.bot_info: BotInfo = bot_info

        self._access_token: Optional[str] = None
        self._expires_in: Optional[int] = None

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        """ 发送消息 """
        return await self.send_custom_message(event.user_id, message)

    async def handle_event(self, event: Type[Event]):
        """ 处理事件 """
        await handle_event(self, event)

    async def _get_access_token(self) -> str:
        """ 获取微信公众平台的 access_token """
        now = time.time()
        if (self._expires_in or 0) > now:
            return self._access_token

        request = Request(
            method="POST",
            url="https://api.weixin.qq.com/cgi-bin/stable_token",
            json={
                "grant_type": "client_credential",
                "appid": self.bot_info.appid,
                "secret": self.bot_info.secret,
                "force_refresh": False,
            },
        )
        resp = await self.adapter.request(request)
        if resp.status_code != 200 or not resp.content:
            raise NetworkError(
                f"Get authorization failed with status code {resp.status_code}."
                " Please check your config."
            )
        res: dict = json.loads(resp.content)
        self._expires_in = now + res["expires_in"]
        self._access_token = res["access_token"]
        return self._access_token

    async def send_custom_message(self, user_id: str, message: Message):
        """ 发送 客服消息 """
        if isinstance(message, str):
            message = Message(MessageSegment.text(message))
        elif isinstance(message, MessageSegment):
            message = Message(message)
        elif not isinstance(message, Message):
            raise ValueError("Unsupported message type")

        for segment in message:
            segment = cast(MessageSegment, segment)
            if segment.type == "text":
                return await self.call_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "text",
                        "text": {"content": segment.data["text"]}
                    },
                )
            elif segment.type == "image":
                media_id = await self.upload_temp_media("image", segment.data["file"])
                return await self.call_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "image",
                        "image": {"media_id": media_id}
                    },
                )
            elif segment.type == "link":
                return await self.call_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "link",
                        "link": {
                            "title": segment.data["title"],
                            "description": segment.data["description"],
                            "url": segment.data["url"],
                            "thumb_url": segment.data["thumb_url"],
                        },
                    },
                )
            elif segment.type == "miniprogrampage":
                media_id = await self.upload_temp_media("image", segment.data["thumb_media"])
                return await self.call_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "miniprogrampage",
                        "miniprogrampage": {
                            "title": segment.data["title"],
                            "pagepath": segment.data["page_path"],
                            "thumb_media_id": media_id,
                        },
                    },
                )
            elif segment.type == "voice":
                media_id = await self.upload_temp_media("voice", segment.data["voice"])
                return await self.call_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "voice",
                        "voice": {
                            "media_id": media_id,
                        },
                    },
                )
            else:
                raise NotImplementedError()

    async def upload_temp_media(self, type: Literal["image", "voice", "video", "thumb"], media: bytes) -> str:
        """ 上传临时素材 

        小程序：仅支持 image
        公众号：支持 image, voice, video, thumb
        """
        access_token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=f"https://api.weixin.qq.com/cgi-bin/media/upload",
                params={
                    "access_token": access_token,
                    "type": type,
                },
                files={
                    "media": ("nonebot-upload-image.png", media, "image/png"),
                },
            )
            if resp.status_code != 200:
                raise NetworkError(
                    f"Get media failed with status code {resp.status_code}."
                )
            res: dict = resp.json()
        log("INFO", f"Upload media: {res}")
        return res["media_id"]

    async def get_temp_media(self, media_id: str) -> bytes:
        """ 获取临时素材 """
        access_token = await self._get_access_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url=f"https://api.weixin.qq.com/cgi-bin/media/get",
                params={
                    "access_token": access_token,
                    "media_id": media_id,
                },
            )
            if resp.status_code != 200:
                raise NetworkError(
                    f"Get media failed with status code {resp.status_code}."
                )
            return resp.content

    async def set_tpying(self, command: Literal["Typing", "CancelTyping"], user_id: str):
        """ 设置用户输入状态 """
        return await self.call_api(
            "/message/custom/typing",
            json={
                "touser": user_id,
                "command": command,
            },
        )
