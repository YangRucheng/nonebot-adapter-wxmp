from typing import Union, Any, Optional, Type, TYPE_CHECKING, cast, Literal
from typing_extensions import override
from xmltodict import unparse
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
from .file import File
from .config import BotInfo
from .utils import log, escape
from .exception import ActionFailed, OfficialReplyError
from .message import (
    Text,
    Link,
    Image,
    Voice,
    Video,
    Message,
    MessageSegment,
    Miniprogrampage,
)

if TYPE_CHECKING:
    from .adapter import Adapter


class Bot(BaseBot):
    adapter: "Adapter"

    @override
    def __init__(self, adapter: "Adapter", self_id: str, bot_info: BotInfo, official_timeout: float):
        super().__init__(adapter, self_id)

        # Bot 配置信息
        self.bot_info: BotInfo = bot_info
        self.official_timeout = official_timeout

        # Bot 鉴权信息
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
        if self.bot_info.type == "official" and not self.bot_info.approve:  # 未完成微信认证的公众号
            try:
                return await self.reply_message(event=event, message=message)
            except OfficialReplyError as e:
                return await self.send_custom_message(user_id=event.get_user_id(), message=message)

        else:  # 小程序、已认证的公众号 直接发客服消息
            return await self.send_custom_message(user_id=event.get_user_id(), message=message)

    async def handle_event(self, event: Type[Event]):
        """ 处理事件 """
        await handle_event(self, event)

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """ 获取微信公众平台的 access_token """
        now = int(time.time())
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

        if resp.status_code != 200:
            raise ActionFailed(resp)

        res: dict = json.loads(resp.content)

        self._expires_in = now + cast(int, res["expires_in"])
        self._access_token = cast(str, res["access_token"])
        return self._access_token

    async def call_json_api(self, api: str, **data: Any) -> dict:
        """ 调用微信公众平台 Json API """
        resp: Response = await self.call_api(api=api, **data)
        res: dict = json.loads(resp.content)

        if resp.status_code != 200 or res.get("errcode", res.get("errCode", 0)) != 0:
            raise ActionFailed(resp)
        return res

    async def upload_temp_media(self, file: File) -> str:
        """ 上传临时素材 \n
        返回 media_id
        """
        res = await self.call_json_api(
            "/media/upload",
            params={
                "type": file.file_type,
            },
            files={
                "media": (file.file_name, file.data),
            },
        )
        log("INFO", f"Upload media: {res}")
        return cast(str, res["media_id"])

    async def get_temp_media(self, media_id: str) -> bytes:
        """ 获取临时素材 """
        resp: Response = await self.call_api(
            "/media/get",
            params={
                "media_id": media_id,
            },
        )
        return resp.content

    async def set_tpying(self, command: Literal["Typing", "CancelTyping"], user_id: str) -> None:
        """ 设置用户输入状态 """
        await self.call_json_api(
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

    async def create_menu(self, data: dict) -> None:
        """ 创建自定义菜单

        用法：[官方文档](https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html)
        """
        await self.call_json_api(
            "/menu/create",
            json=data,
        )

    async def send_custom_message(self, user_id: str, message: Message | MessageSegment | str) -> dict:
        """ 发送 客服消息

        注意：
        公众号需要微信认证
        """
        if isinstance(message, str):
            message = Message(MessageSegment.text(message))
        elif isinstance(message, MessageSegment):
            message = Message(message)
        elif not isinstance(message, Message):
            raise ValueError("Unsupported message type")

        for segment in message:
            if isinstance(segment, Text):
                return await self.call_json_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "text",
                        "text": {"content": segment.data["text"]}
                    },
                )
            elif isinstance(segment, Image):
                if segment.data["media_id"]:
                    media_id = segment.data["media_id"]
                elif segment.data["file"]:
                    media_id = await self.upload_temp_media(File(file=segment.data["file"], file_type="image", file_name="nonebot_upload.png"))
                elif segment.data["file_path"]:
                    file_path = cast(Path, segment.data["file_path"])
                    media_id = await self.upload_temp_media(File(file_path=file_path, file_type="image", file_name="nonebot_upload.png"))
                elif segment.data["file_url"]:
                    file_url = cast(str, segment.data["file_url"])
                    media_id = await self.upload_temp_media(File(file=(await self.download_file(file_url)), file_type="image", file_name="nonebot_upload.png"))
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
            elif isinstance(segment, Link):
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
            elif isinstance(segment, Miniprogrampage):
                if segment.data["thumb_media_id"]:
                    media_id = segment.data["thumb_media_id"]
                elif segment.data["thumb_media"]:
                    media_id = await self.upload_temp_media(File(file=segment.data["thumb_media"], file_type="image", file_name="nonebot_upload.png"))
                elif segment.data["thumb_media_path"]:
                    file_path = cast(Path, segment.data["thumb_media_path"])
                    media_id = await self.upload_temp_media(File(file_path=file_path, file_type="image", file_name="nonebot_upload.png"))
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
                        "miniprogrampage": data | {
                            "appid": segment.data["appid"],
                        },
                    },
                )
            elif isinstance(segment, Voice):
                if segment.data["media_id"]:
                    media_id = segment.data["media_id"]
                elif segment.data["file"]:
                    media_id = await self.upload_temp_media(File(file=segment.data["file"], file_type="voice", file_name="nonebot_upload.amr"))
                elif segment.data["file_path"]:
                    file_path = cast(Path, segment.data["file_path"])
                    media_id = await self.upload_temp_media(File(file_path=file_path, file_type="voice", file_name="nonebot_upload.amr"))
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
            elif isinstance(segment, Video):
                if segment.data["media_id"]:
                    media_id = segment.data["media_id"]
                elif segment.data["file"]:
                    media_id = await self.upload_temp_media(File(file=segment.data["file"], file_type="video", file_name="nonebot_upload.mp4"))
                elif segment.data["file_path"]:
                    file_path = cast(Path, segment.data["file_path"])
                    media_id = await self.upload_temp_media(File(file_path=file_path, file_type="video"))
                else:
                    raise ValueError("At least one of `media_id`, `file`, `file_path` is required")

                return await self.call_json_api(
                    "/message/custom/send",
                    json={
                        "touser": user_id,
                        "msgtype": "video",
                        "video": {
                            "media_id": media_id,
                            "title": segment.data["title"],
                            "description": segment.data["description"],
                        },
                    },
                )

            else:
                raise NotImplementedError()

    async def reply_message(self, event: Type[Event], message: Message | MessageSegment | str) -> None:
        """ 公众号被动回复 [微信文档](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html)

        注意：
        - 需要在5秒内回复\n
        - 只能回复一次\n
        """
        if isinstance(message, str):
            message = Message(MessageSegment.text(message))
        elif isinstance(message, MessageSegment):
            message = Message(message)
        elif not isinstance(message, Message):
            raise ValueError("Unsupported message type")

        resp = {
            "ToUserName": event.user_id,
            "FromUserName": event.to_user_id,
            "CreateTime": int(time.time()),
        }

        MSG = "Passive replies have a shorter time limit, please upload in advance and use media_id"

        if len(message) > 1:
            log("WARNING", "Passive replies can only reply once, only the first message will be sent")

        segment = message[0]
        if isinstance(segment, Text):
            resp |= {
                "MsgType": "text",
                "Content": segment.data["text"]
            }

        elif isinstance(segment, Image):
            if segment.data["media_id"]:
                media_id = segment.data["media_id"]
            else:
                raise ValueError(MSG)

            resp |= {
                "MsgType": "image",
                "Image": {
                    "MediaId": media_id,
                }
            }

        elif isinstance(segment, Voice):
            if segment.data["media_id"]:
                media_id = segment.data["media_id"]
            else:
                raise ValueError(MSG)

            resp |= {
                "MsgType": "voice",
                "Voice": {
                    "MediaId": media_id,
                }
            }

        elif isinstance(segment, Video):
            if segment.data["media_id"]:
                media_id = segment.data["media_id"]
            else:
                raise ValueError(MSG)

            resp |= {
                "MsgType": "video",
                "Video": {
                    "MediaId": media_id,
                    "Title": segment.data["title"],
                    "Description": segment.data["description"],
                }
            }

        else:
            raise OfficialReplyError

        self.adapter._result.set_resp(
            event_id=event.get_event_id(),
            resp=Response(
                status_code=200,
                content=unparse({
                    "xml": resp,
                })
            )
        )
