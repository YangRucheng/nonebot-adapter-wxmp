from typing import Any, Union, Callable, Optional, cast, Literal, Type, TYPE_CHECKING
from typing_extensions import override
from pydantic import BaseModel, Field

from nonebot.adapters import Event as BaseEvent
from nonebot.utils import logger_wrapper
from nonebot.compat import model_dump

from ..message import Message, MessageSegment


log = logger_wrapper("WXMP")


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

    def handle_origin_data(self):
        """ 处理原始数据 """

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
        return True

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
                event.handle_origin_data()
            except Exception:
                pass
            else:
                if current_depth > deepest_depth:
                    deepest_event = event
                    deepest_depth = current_depth

        dfs(cls, 0)
        if deepest_event:
            return deepest_event
        else:
            log("ERROR", f"Payload: {payload}")
            raise NotImplementedError


class MessageEvent(Event):
    """ 消息事件 """
    message_type: Literal["text", "image", "miniprogrampage"] = Field(alias="MsgType")
    """ 事件类型 """
    message_id: int = Field(alias="MsgId")
    """ 消息 ID `MsgId` """
    message: Optional[Message] = Field(default=None, alias="__message__")
    """ 消息内容 """

    @override
    def handle_origin_data(self) -> None:
        """ 处理消息内容 """
        if self.message_type == "text":
            self.message = Message(MessageSegment.text(text=getattr(self, "Content")))
        elif self.message_type == "image":
            self.message = Message(MessageSegment.image(file=getattr(self, "PicUrl")))
        elif self.message_type == "miniprogrampage":
            self.message = Message(MessageSegment.miniprogrampage(
                title=getattr(self, "Title"),
                appid=getattr(self, "AppId"),
                page_path=getattr(self, "PagePath"),
                thumb_media=getattr(self, "ThumbUrl"),
            ))
        else:
            raise NotImplementedError

    @override
    def get_message(self) -> Message:
        return Message(self.message)

    @override
    def get_plaintext(self) -> str:
        return "".join(segment.data.get("text", "") for segment in self.message)

    def get_type(self) -> str:
        return "message"
