from typing import Any, Union, Callable, Optional, cast, Literal, Type
from typing_extensions import override

from pydantic import BaseModel, Field, field_validator, ValidationError
from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump

from .base import Event, MessageEvent


class OfficalAccountEvent(Event):
    """ 公众号 事件 """


class OfficalAccountMessageEvent(MessageEvent, OfficalAccountEvent):
    """ 公众号 用户消息事件 """
    msg_data_id: Optional[str] = Field(default=None, alias="MsgDataId")
    """ 消息的数据ID（消息如果来自文章时才有） `MsgDataId` """
    msg_article_id: Optional[str] = Field(default=None, alias="Idx")
    """ 消息的文章ID（消息如果来自文章时才有） `Idx` """


class SubscribeEvent(OfficalAccountEvent):
    """ 公众号 用户关注事件 """
    message_type: Literal["event"] = "event"
    event: Literal["subscribe"] = "subscribe"

    event_key: Optional[str] = Field(alias="EventKey")
    """ 带参数的公众号二维码，二维码的参数值 `EventKey` """
    ticket: Optional[str] = Field(alias="Ticket")
    """ 二维码的 ticket，可用来换取二维码图片 `Ticket` """


class UnSubscribeEvent(OfficalAccountEvent):
    """ 公众号 用户取消关注事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["unsubscribe"] = Field(alias="Event")


class MenuClickEvent(OfficalAccountEvent):
    """ 公众号 菜单点击事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["CLICK"] = Field(alias="Event")

    event_key: str = Field(alias="EventKey")
    """ 事件KEY值，与自定义菜单接口中KEY值对应 `EventKey` """
