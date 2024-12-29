from typing import Union, Any, Optional, Type, TYPE_CHECKING, cast
from typing_extensions import override
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
        if isinstance(event, MiniprogramMessageEvent) \
                or isinstance(event, OfficalAccountMessageEvent):
            return await self.send_custom_message(event.user_id, message)
        else:
            raise ApiNotAvailable()

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
                    touser=user_id,
                    msgtype="text",
                    text={"content": segment.data["text"]},
                )
            elif segment.type == "image":
                raise ApiNotAvailable("Image message is not supported in miniprogram")
            elif segment.type == "link":
                raise ApiNotAvailable("Link message is not supported in miniprogram")
            elif segment.type == "miniprogrampage":
                raise ApiNotAvailable("Miniprogram page message is not supported in miniprogram")
