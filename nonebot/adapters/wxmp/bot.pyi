from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Type,
    Union,
)

from nonebot.adapters import Bot as BaseBot

from .config import BotInfo
from .event import Event
from .file import File
from .message import (
    Message,
    MessageSegment,
)

if TYPE_CHECKING:  # noqa: PYI002
    from .adapter import Adapter

class Bot(BaseBot):
    adapter: "Adapter"
    bot_info: BotInfo
    official_timeout: float
    _access_token: Optional[str]
    _expires_in: Optional[int]

    def __init__(self, adapter: "Adapter", self_id: str, bot_info: BotInfo, official_timeout: float): ...
    async def send(self, event: Event, message: Union[str, Message, MessageSegment], **kwargs) -> Any: ...
    async def handle_event(self, event: Event): ...
    async def get_access_token(self, force_refresh: bool = False) -> str: ...
    async def call_json_api(self, api: str, method="POST", **data: Any) -> dict: ...
    async def upload_temp_media(self, file: File) -> str: ...
    async def get_temp_media(self, media_id: str) -> bytes: ...
    async def set_tpying(self, command: Literal["Typing", "CancelTyping"], user_id: str) -> None: ...
    async def download_file(self, url: str) -> bytes: ...
    async def send_custom_message(
        self,
        user_id: str,
        message: Union[Message, MessageSegment, str],
    ) -> dict: ...
    async def reply_message(
        self,
        event: Type[Event],
        message: Union[Message, MessageSegment, str],
    ) -> None: ...
    async def menu_create(self, data: dict) -> dict:
        """创建自定义菜单

        用法：[官方文档](https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Querying_Custom_Menus.html)
        """
