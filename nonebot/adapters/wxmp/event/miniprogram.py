from typing import Any, Union, Callable, Optional, cast, Literal, Type
from typing_extensions import override

from pydantic import BaseModel, Field, field_validator, ValidationError
from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump

from ..message import Message, MessageSegment
from .base import Event, MessageEvent


class MiniprogramEvent(Event):
    """ 小程序 事件 """


class MiniprogramMessageEvent(MessageEvent, MiniprogramEvent):
    """ 小程序 客服消息事件 """


class UserEnterEvent(MiniprogramEvent):
    """ 用户进入客服会话事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["user_enter_tempsession"] = Field(alias="Event")
    session_from: str = Field(alias="SessionFrom")
    """ 会话来源，开发者在客服会话按钮设置的 session-from 属性 """
