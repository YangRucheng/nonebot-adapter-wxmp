from typing import Union, Any, Optional, Type, TYPE_CHECKING, cast, Literal
from typing_extensions import override
from pathlib import Path
import json
import time

from nonebot.message import handle_event
from nonebot.utils import logger_wrapper
from nonebot.adapters import Bot as BaseBot
from nonebot.drivers import Request, Response
from nonebot.drivers import (
    Request,
    Response,
)

from .event import *
from .utils import log
from .config import BotInfo
from .message import Message, MessageSegment
from .exception import NetworkError, ActionFailed

if TYPE_CHECKING:
    from .adapter import Adapter


class Bot(BaseBot):
    adapter: "Adapter"

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

    async def _get_access_token(self, force_refresh: bool = False) -> str:
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
                "force_refresh": force_refresh,
            },
        )
        resp = await self.adapter.request(request)
        if resp.status_code != 200 or not resp.content:
            raise ActionFailed(retcode=resp.status_code, info=str(resp.content))
        res: dict = json.loads(resp.content)
        self._expires_in = now + res["expires_in"]
        self._access_token = res["access_token"]
        return self._access_token

    async def call_json_api(self, api: str, **data: Any) -> dict:
        """ 调用微信公众平台 Json API """
        resp: Response = await self.call_api(api=api, **data)
        res: dict = json.loads(resp.content)
        if res.get("errcode", 0) != 0:
            raise ActionFailed(retcode=res["errcode"], info=res)
        return res

    async def send_custom_message(self, user_id: str, message: Message | MessageSegment | str) -> dict:
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
                return await self.call_json_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "text",
                        "text": {"content": segment.data["text"]}
                    },
                )
            elif segment.type == "image":
                if segment.data["media_id"]:
                    media_id = segment.data["media_id"]
                elif segment.data["file"]:
                    media_id = await self.upload_temp_media("image", segment.data["file"])
                elif segment.data["file_path"]:
                    file_path = cast(Path, segment.data["file_path"])
                    media_id = await self.upload_temp_media("image", file_path.read_bytes())
                elif segment.data["file_url"]:
                    file_url = cast(str, segment.data["file_url"])
                    media_id = await self.upload_temp_media("image", await self.download_file(file_url))
                else:
                    raise ValueError("At least one of `media_id`, `file`, `file_path`, `file_url` is required")

                return await self.call_json_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "image",
                        "image": {"media_id": media_id}
                    },
                )
            elif segment.type == "link":
                if self.bot_info.type != "miniprogram":
                    raise ValueError("link type is only supported in miniprogram")

                return await self.call_json_api(
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
                if segment.data["thumb_media_id"]:
                    media_id = segment.data["thumb_media_id"]
                elif segment.data["thumb_media"]:
                    media_id = await self.upload_temp_media("image", segment.data["thumb_media"])
                elif segment.data["thumb_media_path"]:
                    file_path = cast(Path, segment.data["thumb_media_path"])
                    media_id = await self.upload_temp_media("image", file_path.read_bytes())
                else:
                    raise ValueError("At least one of `thumb_media_id`, `thumb_media`, `thumb_media_path` is required")

                data = {
                    "title": segment.data["title"],
                    "pagepath": segment.data["page_path"],
                    "thumb_media_id": media_id,
                }

                return await self.call_json_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "miniprogrampage",
                        "miniprogrampage": data if self.bot_info.type == "miniprogram" else data | {
                            "appid": segment.data["appid"],
                        },
                    },
                )
            elif segment.type == "voice":
                if self.bot_info.type != "official":
                    raise ValueError("voice type is only supported in official account")

                if segment.data["media_id"]:
                    media_id = segment.data["media_id"]
                elif segment.data["file"]:
                    media_id = await self.upload_temp_media("voice", segment.data["file"])
                elif segment.data["file_path"]:
                    file_path = cast(Path, segment.data["file_path"])
                    media_id = await self.upload_temp_media("voice", file_path.read_bytes())
                else:
                    raise ValueError("At least one of `media_id`, `file`, `file_path` is required")

                return await self.call_json_api(
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
        res = await self.call_json_api(
            "/media/upload",
            params={
                "type": type,
            },
            files={
                "media": ("nonebot-upload-image.png", media, "image/png"),
            },
        )
        log("INFO", f"Upload media: {res}")
        return res["media_id"]

    async def get_temp_media(self, media_id: str) -> bytes:
        """ 获取临时素材 """
        resp: Response = await self.call_api(
            "/media/get",
            params={
                "media_id": media_id,
            },
        )
        return resp.content

    async def set_tpying(self, command: Literal["Typing", "CancelTyping"], user_id: str) -> dict:
        """ 设置用户输入状态 """
        return await self.call_json_api(
            "/message/custom/typing",
            json={
                "touser": user_id,
                "command": command,
            },
        )

    async def download_file(self, url: str) -> bytes:
        """ 下载文件 """
        resp: Response = await self.adapter.request(Request("GET", url))
        return resp.content
