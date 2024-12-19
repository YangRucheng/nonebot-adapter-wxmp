from typing import Any, Union, Callable, Optional, cast, Literal, Type, TYPE_CHECKING
from typing_extensions import override
from pydantic import BaseModel, Field

from .miniprogram import MiniprogramEvent
from .offical import OfficalAccountEvent


class AuthorizationChangeEvent(MiniprogramEvent, OfficalAccountEvent):
    """ 授权用户信息变更事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    event: Literal["user_authorization_revoke"] = Field(alias="Event")
    """ 事件类型 `Event` """
    openid: str = Field(alias="OpenId")
    """ 用户 OpenId `OpenId` """
    appid: str = Field(alias="AppId")
    """ 公众号/小程序 AppId `AppId` """
    revoke_info: str = Field(alias="RevokeInfo")
    """ 取消授权的数据类型 `RevokeInfo` """
