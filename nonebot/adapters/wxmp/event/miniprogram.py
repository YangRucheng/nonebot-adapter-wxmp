from typing import Any, Union, Callable, Optional, cast, Literal, Type
from pydantic import Field

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


class AuthorizationChangeEvent(MiniprogramEvent):
    """ 授权用户信息变更事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    event: Literal["user_authorization_revoke"] = Field(alias="Event")
    """ 事件类型 `Event` """
    openid: str = Field(alias="OpenID")
    """ 用户 OpenID `OpenID` """
    appid: str = Field(alias="AppID")
    """ 小程序 AppID `AppID` """
    revoke_info: str = Field(alias="RevokeInfo")
    """ 取消授权的数据类型 `RevokeInfo` """


class KfCloseSessionEvent(MiniprogramEvent):
    """ 客服关闭会话事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["kf_close_session"] = Field(alias="Event")
    kf_account: str = Field(alias="KfAccount")
    close_type: str = Field(alias="CloseType")
