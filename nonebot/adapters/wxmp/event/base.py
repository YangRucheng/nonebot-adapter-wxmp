from typing import Any, Union, Callable, Optional, cast, Literal, Type, TYPE_CHECKING
from pydantic import Field, ConfigDict, ValidationError
from typing_extensions import override
import datetime

from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump

from ..message import Message, MessageSegment
from ..utils import log
from ..exception import ActionFailed, NetworkError, ApiNotAvailable, EventNotAvailable


class Event(BaseEvent):
    to_user_id: str = Field(alias="ToUserName")
    """ 接收者的 OpenId `ToUserName` """
    user_id: str = Field(alias="FromUserName")
    """ 发送者的 OpenId `FromUserName` """
    timestamp: int = Field(alias="CreateTime")
    """ 消息发送时间戳 `CreateTime` """
    message_type: str = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    event: Optional[str] = Field(default=None, alias="Event")

    model_config = ConfigDict(extra='ignore')

    def handle_origin_data(self, payload: Optional[dict] = None):
        """ 处理原始数据 """
        pass

    @override
    def get_type(self) -> str:
        return self.message_type

    @override
    def get_event_name(self) -> str:
        return self.__class__.__name__

    @override
    def get_event_description(self) -> str:
        return str(model_dump(self))

    @override
    def get_message(self) -> Message:
        raise NotImplementedError

    @override
    def get_plaintext(self) -> str:
        raise NotImplementedError

    @override
    def get_user_id(self) -> str:
        return str(self.user_id)

    @override
    def get_session_id(self) -> str:
        return f"{self.__class__.__name__}_{self.message_type}_{self.user_id}_{self.to_user_id}"

    @override
    def is_tome(self) -> bool:
        return True  # 客服消息无群聊

    @property
    def time(self) -> datetime.datetime:
        """ 消息发送时间 """
        return datetime.datetime.fromtimestamp(self.timestamp)

    @classmethod
    def payload_to_event(cls, payload: dict) -> "Event":
        """ 将 payload 转换为 Event 对象的子类 """
        deepest_event = None
        deepest_depth = -1

        def dfs(current_cls: Type[Event], current_depth):
            nonlocal deepest_event, deepest_depth
            event = None
            for subclass in current_cls.__subclasses__():
                dfs(subclass, current_depth + 1)
            try:
                event = current_cls.model_validate(payload)
                event.handle_origin_data(payload=payload)  # 处理原始事件
            except ValidationError as e:
                pass
            else:
                if current_depth > deepest_depth:
                    deepest_event = event
                    deepest_depth = current_depth

        dfs(cls, 0)
        if deepest_event:
            return deepest_event
        else:
            log("ERROR", f"Payload: {payload} Cls: {cls}")
            raise NotImplementedError


class MessageEvent(Event):
    """ 消息事件 """
    message_type: Literal["text", "image", "miniprogrampage", "voice", "video", "shortvideo", "location", "link"] = Field(alias="MsgType")
    """ 事件类型 
    - `text`: 文本消息 支持小程序和公众号
    - `image`: 图片消息 支持小程序和公众号
    - `link` 链接消息 支持小程序和公众号
    
    - `miniprogrampage`: 小程序卡片消息 仅支持小程序
    - `voice` 语音消息 仅支持公众号
    - `video` 视频消息 仅支持公众号
    - `shortvideo` 小视频消息 仅支持公众号
    - `location` 地理位置消息 仅支持公众号
    """
    message_id: int = Field(alias="MsgId")
    """ 消息 ID `MsgId` """
    original_message: Optional[Message] = Field(default=None)
    """ 原始消息内容 """
    message: Optional[Message] = Field(default=None)
    """ 消息内容 """

    @override
    def handle_origin_data(self, payload: dict) -> None:
        """ 处理消息内容 """
        segm: MessageSegment | None = None
        if self.message_type == "text":
            segm = MessageSegment.text(
                text=payload.get("Content"),
            )
        elif self.message_type == "image":
            segm = MessageSegment.image(
                file_url=payload.get("PicUrl"),
                media_id=payload.get("MediaId"),
            )
        elif self.message_type == "miniprogrampage":
            segm = MessageSegment.miniprogrampage(  # no test
                title=payload.get("Title"),
                appid=payload.get("AppId"),
                page_path=payload.get("PagePath"),
                thumb_media=payload.get("ThumbUrl"),
            )
        elif self.message_type == "voice":
            segm = MessageSegment.voice(
                media_id=payload.get("MediaId"),
                format=payload.get("Format"),
            )
        elif self.message_type == "link":
            segm = MessageSegment.link(
                title=payload.get("Title"),
                description=payload.get("Description"),
                url=payload.get("Url"),
            )
        else:
            # TODO video, shortvideo, location
            raise EventNotAvailable

        self.message = Message([segm]) if segm else Message([])

    @property
    def original_message(self) -> Message:
        return self.message

    @override
    def get_message(self) -> Message:
        return self.message

    @override
    def get_plaintext(self) -> str:
        return "".join(segment.data.get("text", "") for segment in self.message)

    def get_type(self) -> str:
        return "message"
