import datetime
import random
from typing import Literal, Optional

from pydantic import ConfigDict, Field
from typing_extensions import override

from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump

from .message import Message


class Event(BaseEvent):
    to_user_id: str = Field(alias="ToUserName")
    """ 接收者的 OpenId `ToUserName` """
    user_id: str = Field(alias="FromUserName")
    """ 发送者的 OpenId `FromUserName` """
    timestamp: int = Field(alias="CreateTime")
    """ 消息发送时间戳 `CreateTime` """
    message_type: Literal["event", "text", "image", "miniprogrampage", "video", "location", "voice"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """

    model_config = ConfigDict(extra='ignore')

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp)

    @override
    def is_tome(self) -> bool:
        """ 平台只有私聊，所以直接返回 True """
        return True

    @override
    def get_type(self) -> Literal["message", "notice"]:
        raise NotImplementedError

    @override
    def get_message(self) -> Optional["Message"]:
        raise NotImplementedError

    @override
    def get_event_name(self) -> str:
        return self.__class__.__name__

    @override
    def get_event_description(self) -> str:
        raise NotImplementedError

    @override
    def get_user_id(self) -> str:
        return self.user_id

    @override
    def get_session_id(self) -> str:
        return f"{self.user_id}_{self.to_user_id}"

    def get_event_id(self) -> str:
        """ 随机生成 event_id """
        if event_id := getattr(self, "_event_id", None):
            return event_id
        else:
            self._event_id = f"{self.get_session_id()}_{random.randint(int(10e5), int(10e20))}"
            return self._event_id


class NoticeEvent(Event):
    """ 通知事件 """
    event: str = Field(alias="Event")
    """ 事件类型 `Event` """

    @override
    def get_type(self) -> Literal["notice"]:
        return "notice"

    @override
    def get_event_description(self) -> str:
        return str(model_dump(self))


class MessageEvent(Event):
    """ 消息事件 """
    message_type: Literal["text", "image", "miniprogrampage", "video", "location", "voice"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    message_id: int = Field(alias="MsgId")
    """ 消息 ID `MsgId` """

    @property
    def reply(self) -> None:
        return None

    @property
    def message(self) -> "Message":
        return self.get_message()

    @override
    def get_type(self) -> Literal["message"]:
        return "message"

    @override
    def get_message(self) -> "Message":
        if message := getattr(self, "_message", None):
            return message
        else:
            self._message = Message.from_event(self)
            return self._message

    @override
    def get_event_description(self) -> str:
        keys = ('to_user_id', 'user_id', 'time', 'message_type', 'message_id', 'message')
        return str({key: getattr(self, key) for key in keys})


class MiniprogramEvent(Event):
    """ 小程序事件 """


class OfficalEvent(Event):
    """ 公众号事件 """


class UserEnterEvent(MiniprogramEvent, NoticeEvent):
    """ 用户进入客服会话事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["user_enter_tempsession"] = Field(alias="Event")
    session_from: str = Field(alias="SessionFrom")
    """ 会话来源，开发者在客服会话按钮设置的 session-from 属性 """

    @override
    def get_type(self) -> Literal["meta_event", "message", "notice", "request"]:
        return "notice"


class AuthorizationChangeEvent(MiniprogramEvent, NoticeEvent):
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


class KfCloseSessionEvent(MiniprogramEvent, NoticeEvent):
    """ 客服关闭会话事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["kf_close_session"] = Field(alias="Event")
    kf_account: str = Field(alias="KfAccount")
    close_type: str = Field(alias="CloseType")


class TextMessageEvent(MessageEvent, MiniprogramEvent, OfficalEvent):
    message_type: Literal["text"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    content: str = Field(alias="Content")
    """ 文本消息内容 `Content` """


class ImageMessageEvent(MessageEvent, MiniprogramEvent, OfficalEvent):
    message_type: Literal["image"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    pic_url: str = Field(alias="PicUrl")
    """ 图片链接 `PicUrl` """
    media_id: str = Field(alias="MediaId")
    """ 图片消息媒体 id `MediaId` """


class MiniprogramPathMessageEvent(MiniprogramEvent, MessageEvent):
    message_type: Literal["miniprogrampage"] = Field(alias="MsgType")
    """ 消息类型 `MsgType` """
    title: str = Field(alias="Title")
    """ 小程序消息标题 `Title` """
    appid: str = Field(alias="AppId")
    """ 小程序 AppID `AppId` """
    page_path: str = Field(alias="PagePath")
    """ 小程序页面路径 `PagePath` """
    thumb_url: str = Field(alias="ThumbUrl")
    """ 小程序消息封面图片 `ThumbUrl` """
    thumb_media_id: str = Field(alias="ThumbMediaId")
    """ 小程序消息封面图片媒体 id `ThumbMediaId` """


class SubscribeEvent(OfficalEvent, NoticeEvent):
    """ 公众号 用户关注事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["subscribe"] = Field(alias="Event")

    event_key: Optional[str] = Field(default=None, alias="EventKey")
    """ 带参数的公众号二维码，二维码的参数值 `EventKey` """
    ticket: Optional[str] = Field(default=None, alias="Ticket")
    """ 二维码的 ticket，可用来换取二维码图片 `Ticket` """


class UnSubscribeEvent(OfficalEvent, NoticeEvent):
    """ 公众号 用户取消关注事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["unsubscribe"] = Field(alias="Event")


class MenuClickEvent(OfficalEvent, NoticeEvent):
    """ 公众号 菜单点击事件 """
    message_type: Literal["event"] = Field(alias="MsgType")
    event: Literal["CLICK"] = Field(alias="Event")

    event_key: str = Field(alias="EventKey")
    """ 事件KEY值，与自定义菜单接口中KEY值对应 `EventKey` """


class VedioMessageEvent(OfficalEvent, MessageEvent):
    """ 公众号 视频消息事件 """
    message_type: Literal["video"] = Field(alias="MsgType")

    media_id: str = Field(alias="MediaId")
    """ 视频消息媒体 id `MediaId` """
    thumb_media_id: str = Field(alias="ThumbMediaId")
    """ 视频消息缩略图的媒体 id `ThumbMediaId` """


class LocationEvent(OfficalEvent, MessageEvent):
    """ 公众号 地理位置消息事件 """
    message_type: Literal["location"] = Field(alias="MsgType")

    location_x: str = Field(alias="Location_X")
    """ 地理位置维度 `Location_X` """
    location_y: str = Field(alias="Location_Y")
    """ 地理位置经度 `Location_Y` """
    scale: str = Field(alias="Scale")
    """ 地图缩放大小 `Scale` """
    label: str = Field(alias="Label")
    """ 地理位置信息 `Label` """


class VoiceMessageEvent(OfficalEvent, MessageEvent):
    """ 公众号 语音消息事件 """
    message_type: Literal["voice"] = Field(alias="MsgType")

    media_id: str = Field(alias="MediaId")
    """ 语音消息媒体 id `MediaId` """
    format: str = Field(alias="Format")
    """ 语音格式 `Format` """
    recognition: Optional[str] = Field(alias="Recognition")
    """ 语音识别结果 `Recognition` """


MINIPROGRAM_EVENT_CLASSES: list[type[MiniprogramEvent]] = [
    UserEnterEvent,
    AuthorizationChangeEvent,
    KfCloseSessionEvent,
    TextMessageEvent,
    ImageMessageEvent,
    MiniprogramPathMessageEvent,
]

OFFICIAL_EVENT_CLASSES: list[type[OfficalEvent]] = [
    SubscribeEvent,
    UnSubscribeEvent,
    MenuClickEvent,
    TextMessageEvent,
    ImageMessageEvent,
    VedioMessageEvent,
    LocationEvent,
    VoiceMessageEvent,
]

MESSAGE_EVENT_CLASSES: list[type[MessageEvent]] = [
    TextMessageEvent,
    ImageMessageEvent,
    MiniprogramPathMessageEvent,
    VedioMessageEvent,
    LocationEvent,
    VoiceMessageEvent,
]

__all__ = [
    "Event",
    "NoticeEvent",
    "MessageEvent",
    "MiniprogramEvent",
    "OfficalEvent",

    "UserEnterEvent",
    "AuthorizationChangeEvent",
    "KfCloseSessionEvent",
    "TextMessageEvent",
    "ImageMessageEvent",
    "MiniprogramPathMessageEvent",
    "SubscribeEvent",
    "UnSubscribeEvent",
    "MenuClickEvent",
    "VedioMessageEvent",
    "LocationEvent",
    "VoiceMessageEvent",

    "MINIPROGRAM_EVENT_CLASSES",
    "OFFICIAL_EVENT_CLASSES",
    "MESSAGE_EVENT_CLASSES",
]
