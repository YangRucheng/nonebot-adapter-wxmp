import re
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional, Type, TypedDict, Union, cast

from pydantic import HttpUrl
from typing_extensions import override

from nonebot.adapters import (
    Message as BaseMessage,
)
from nonebot.adapters import (
    MessageSegment as BaseMessageSegment,
)

from .exception import UnkonwnEventError

if TYPE_CHECKING:
    from .event import MessageEvent


class MessageSegment(BaseMessageSegment["Message"]):
    """ 消息段 """

    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def __str__(self) -> str:
        if self.type == "text":
            return self.data["text"]
        return ""

    @override
    def is_text(self) -> bool:
        return self.type == "text"

    @classmethod
    def text(
        cls,
        text: str,
    ) -> "Text":
        """ 文本消息段

        参数：
        - `text` 文本内容
        """
        return Text("text", {"text": text})

    @classmethod
    def image(
        cls,
        file: Optional[bytes] = None,
        file_path: Optional[Path] = None,
        file_url: Optional[HttpUrl] = None,
        media_id: Optional[str] = None,
    ) -> "Image":
        """ 图片消息段

        参数：
        - `file` 图片文件的二进制数据
        - `file_path` 图片文件的本地路径
        - `file_url` 图片文件的网络 URL
        - `media_id` 微信公众平台 MediaID
        """
        if not file and not file_path and not file_url and not media_id:
            raise ValueError("At least one of `file`, `file_path`, `file_url`, `media_id` is required")

        return Image("image", {
            "file": file,
            "file_path": file_path,
            "file_url": file_url,
            "media_id": media_id,
        })

    @classmethod
    def link(
        cls,
        title: str,
        description: str,
        url: str,
        thumb_url: Optional[str] = None,
    ) -> "Link":
        """ 链接消息段

        参数：
        - `title` 标题
        - `description` 描述
        - `url` 网页链接 URL
        - `thumb_url` 缩略图 URL
        """
        return Link("link", {
            "title": title,
            "description": description,
            "url": url,
            "thumb_url": thumb_url,
        })

    @classmethod
    def miniprogrampage(
        cls,
        title: str,
        page_path: str,
        thumb_media: Optional[bytes] = None,
        thumb_url: Optional[str] = None,
        thumb_media_path: Optional[Path] = None,
        thumb_media_id: Optional[str] = None,
        appid: Optional[str] = None,
    ) -> "Miniprogrampage":
        """ 小程序卡片消息段

        参数：
        - `title` 标题
        - `page_path` 小程序页面路径
        - `thumb_media` 缩略图的二进制数据
        - `thumb_url` 缩略图的网络 URL
        - `thumb_media_path` 缩略图的本地路径
        - `thumb_media_id` 微信公众平台 MediaID
        - `appid` 小程序 AppID （小程序留空，公众号必须填与公众号关联的小程序 AppID）
        """
        return Miniprogrampage("miniprogrampage", {
            "title": title,
            "page_path": page_path,
            "thumb_media": thumb_media,
            "thumb_url": thumb_url,
            "thumb_media_path": thumb_media_path,
            "thumb_media_id": thumb_media_id,
            "appid": appid,
        })

    @classmethod
    def voice(
        cls,
        file: Optional[bytes] = None,
        file_path: Optional[Path] = None,
        media_id: Optional[str] = None,
        format: Optional[str] = None,
    ) -> "Voice":
        """ 语音消息段

        参数：
        - `file` 语音文件的二进制数据
        - `file_path` 语音文件的本地路径
        - `media_id` 微信公众平台 MediaID
        - `format` 语音格式
        """
        return Voice("voice", {
            "file": file,
            "file_path": file_path,
            "media_id": media_id,
            "format": format,
        })

    @classmethod
    def video(
        cls,
        file: Optional[bytes] = None,
        file_path: Optional[Path] = None,
        media_id: Optional[str] = None,
        thumb: Optional[bytes] = None,
        thumb_path: Optional[Path] = None,
        thumb_media_id: Optional[str] = None,
        title: str = "",
        description: str = "",
    ) -> "Video":
        """ 视频消息段

        参数：
        - `file` 视频文件的二进制数据
        - `file_path` 视频文件的本地路径
        - `media_id` 微信公众平台 MediaID
        - `thumb` 缩略图的二进制数据
        - `thumb_path` 缩略图的本地路径
        - `thumb_media_id` 微信公众平台 MediaID
        - `title` 视频标题
        - `description` 视频描述
        """
        return Video("video", {
            "file": file,
            "file_path": file_path,
            "media_id": media_id,
            "thumb": thumb,
            "thumb_path": thumb_path,
            "thumb_media_id": thumb_media_id,
            "title": title,
            "description": description,
        })

    @classmethod
    def location(
        cls,
        location_x: float,
        location_y: float,
        scale: int,
        label: str,
    ) -> "Location":
        """ 位置消息段

        参数：
        - `location_x` 地理位置纬度
        - `location_y` 地理位置经度
        - `scale` 地图缩放比例
        - `label` 地理位置信息
        """
        return Location("location", {
            "location_x": location_x,
            "location_y": location_y,
            "scale": scale,
            "label": label,
        })

    @classmethod
    def emjoy(
        cls,
        emjoy_type: "EmjoyType",
    ) -> "Emjoy":
        """ 表情消息段

        参数：
        - `emjoy` 表情类型
        """
        return Emjoy("emjoy", {
            "emjoy": emjoy_type,
        })


class _TextData(TypedDict):
    text: str


class Text(MessageSegment):
    """ 文本 消息段 """
    data: _TextData


class _ImageData(TypedDict):
    file: Optional[bytes]
    file_path: Optional[Path]
    file_url: Optional[HttpUrl]
    media_id: Optional[str]


class Image(MessageSegment):
    """ 图片 消息段 """
    data: _ImageData


class _LinkData(TypedDict):
    title: str
    description: str
    url: str
    thumb_url: Optional[str]


class Link(MessageSegment):
    """ 图文链接 消息段 """
    data: _LinkData


class _MiniProgramPageData(TypedDict):
    title: str
    page_path: str
    thumb_media: Optional[bytes]
    thumb_url: Optional[str]
    thumb_media_path: Optional[Path]
    thumb_media_id: Optional[str]
    appid: Optional[str]


class Miniprogrampage(MessageSegment):
    """ 小程序卡片 消息段 """
    data: _MiniProgramPageData


class _VoiceData(TypedDict):
    file: Optional[bytes]
    file_path: Optional[Path]
    media_id: Optional[str]
    format: Optional[str]


class Voice(MessageSegment):
    """ 音频 消息段 """
    data: _VoiceData


class _VideoData(TypedDict):
    file: Optional[bytes]
    file_path: Optional[Path]
    media_id: Optional[str]
    thumb: Optional[bytes]
    thumb_path: Optional[Path]
    thumb_media_id: Optional[str]
    title: str
    description: str


class Video(MessageSegment):
    """ 视频 消息段 """
    data: _VideoData


class _LocationData(TypedDict):
    location_x: float
    location_y: float
    scale: int
    label: str


class Location(MessageSegment):
    """ 位置 消息段 """
    data: _LocationData


class EmjoyType(Enum):
    """ 行内表情

    注意：这是人工测试出来的，官方没有对照表，更新可能不及时
    """
    微笑 = "/::)"
    撇嘴 = "/::~"
    色 = "/::B"
    发呆 = "/::|"
    得意 = "/:8-)"
    流泪 = "/::<"
    害羞 = "/::$"
    闭嘴 = "/::X"
    睡 = "/::Z"
    大哭 = "/::'("
    尴尬 = "/::-|"
    发怒 = "/::@"
    调皮 = "/::P"
    呲牙 = "/::D"
    惊讶 = "/::O"
    难过 = "/::("
    囧 = "[Blush]"
    抓狂 = "/::Q"
    吐 = "/::T"
    偷笑 = "/:,@P"
    愉快 = "/:,@-D"
    白眼 = "/::d"
    傲慢 = "/:,@o"
    困 = "/:|-)"
    惊恐 = "/::!"
    憨笑 = "/::>"
    悠闲 = "/::,@"
    咒骂 = "/::-S"
    疑问 = "/:?"
    嘘 = "/:,@x"
    晕 = "/:,@@"
    衰 = "/:,@!"
    骷髅 = "/:!!!"
    敲打 = "/:xx"
    再见 = "[Bye]"
    擦汗 = "/:wipe"
    抠鼻 = "/:dig"
    鼓掌 = "/:handclap"
    坏笑 = "/:B-)"
    右哼哼 = "/:@>"
    鄙视 = "/:>-|"
    委屈 = "/:P-("
    快哭了 = "/::'|"
    阴险 = "/:X-)"
    亲亲 = "/::*"
    可怜 = "/:8*"
    笑脸 = "[Happy]"
    生病 = "[Sick]"
    脸红 = "[Flushed]"
    破涕为笑 = "[Lol]"
    恐惧 = "[Terror]"
    失望 = "[LetDown]"
    无语 = "[Duh]"
    嘿哈 = "[Hey]"
    捂脸 = "[Facepalm]"
    奸笑 = "[Smirk]"
    机智 = "[Smart]"
    皱眉 = "[Concerned]"
    耶 = "[Yeah!]"
    吃瓜 = "[Onlooker]"
    加油 = "[GoForIt]"
    汗 = "[Sweats]"
    天啊 = "[OMG]"
    Emm = "[Emm]"
    社会社会 = "[Respect]"
    旺柴 = "[Doge]"
    好的 = "[NoProb]"
    打脸 = "[MyBad]"
    哇 = "[Wow]"
    翻白眼 = "[Boring]"
    六六六 = "[Awesome]"
    让我看看 = "[LetMeSee]"
    叹气 = "[Sigh]"
    苦涩 = "[Hurt]"
    裂开 = "[Broken]"
    嘴唇 = "/:showlove"
    爱心 = "/:heart"
    心碎 = "/:break"
    拥抱 = "/:hug"
    强 = "/:strong"
    弱 = "/:weak"
    握手 = "/:share"
    胜利 = "/:v"
    抱拳 = "[Salute]"
    勾引 = "/:jj"
    拳头 = "/:@@"
    OK = "/:ok"
    合十 = "[Worship]"
    啤酒 = "/:beer"
    咖啡 = "/:coffee"
    蛋糕 = "/:cake"
    玫瑰 = "/:rose"
    凋谢 = "/:fade"
    菜刀 = "/:pd"
    炸弹 = "/:bome"
    便便 = "/:shit"
    月亮 = "/:moon"
    太阳 = "/:sun"
    庆祝 = "[Party]"
    礼物 = "[gift]"
    红包 = "[Packet]"
    發 = "[Rich]"
    福 = "[Blessing]"
    烟花 = "[Fireworks]"
    爆竹 = "[Firecracker]"
    猪头 = "/:pig"
    跳跳 = "/:jump"
    发抖 = "/:shake"
    转圈 = "/:circle"

    @override
    def __repr__(self):
        return f"[{self.name}]"


class _EmjoyData(TypedDict):
    emjoy: EmjoyType


class Emjoy(MessageSegment):
    """ 表情（行内） 消息段 """
    data: _EmjoyData


class Message(BaseMessage[MessageSegment]):
    """ 消息 """

    @override
    @classmethod
    def get_segment_class(cls) -> Type[MessageSegment]:
        """ 获取消息段类 """
        return MessageSegment

    @override
    @staticmethod
    def _construct(msg: str) -> Iterable[MessageSegment]:
        """ 将文本消息构造成消息段数组 """
        parts = re.split("({0})".format(
            '|'.join(
                re.escape(emjoy.value) for emjoy in EmjoyType if emjoy.value
            )
        ), msg)
        for part in parts:
            if not part:
                continue
            if part in EmjoyType._value2member_map_:
                yield MessageSegment.emjoy(EmjoyType(part))
            else:
                yield MessageSegment.text(part)

    @override
    def __add__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return super().__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return super().__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    def extract_plain_text(self) -> str:
        """ 提取消息中的纯文本 """
        return "".join(
            seg.data["text"]
            for seg in self
            if seg.type == "text"
        )

    @classmethod
    def from_event(cls, event: MessageEvent) -> "Message":
        """ 从消息事件转为消息序列 """
        if event.message_type == "text":
            text = getattr(event, "content")
            message: list[MessageSegment] = list(cls._construct(text))
            return cls(message)

        elif event.message_type == "image":
            return cls(MessageSegment.image(
                media_id=getattr(event, "media_id"),
                file_url=getattr(event, "pic_url"),
            ))

        elif event.message_type == "miniprogrampage":
            return cls(MessageSegment.miniprogrampage(
                title=getattr(event, "title"),
                page_path=getattr(event, "page_path"),
                appid=getattr(event, "appid"),
                thumb_media_id=getattr(event, "thumb_media_id"),
                thumb_url=getattr(event, "thumb_url"),
            ))

        elif event.message_type == "video":
            return cls(MessageSegment.video(
                media_id=getattr(event, "media_id"),
                thumb_media_id=getattr(event, "thumb_media_id"),
            ))

        elif event.message_type == "voice":
            return cls(MessageSegment.voice(
                media_id=getattr(event, "media_id"),
                format=getattr(event, "format"),
            ))

        elif event.message_type == "location":
            return cls(MessageSegment.location(
                location_x=float(getattr(event, "location_x")),
                location_y=float(getattr(event, "location_y")),
                scale=getattr(event, "scale"),
                label=getattr(event, "label"),
            ))

        else:
            raise UnkonwnEventError(dict(event))

    def merge_segments(self) -> "Message":
        """ 合并相邻的文本消息段，并转义行内表情 """
        message: list[MessageSegment] = []

        for segm in self:
            if not len(message):
                message.append(segm)
                continue

            if segm.type not in ["emjoy", "text"]:
                message.append(segm)
                continue

            if message[-1].type != "text":
                if segm.type == "text":
                    message.append(segm)
                elif segm.type == "emjoy":
                    segm = cast(Emjoy, segm)
                    message.append(MessageSegment.text(segm.data["emjoy"].value))
            else:
                if segm.type == "text":
                    message[-1].data["text"] += segm.data["text"]
                elif segm.type == "emjoy":
                    segm = cast(Emjoy, segm)
                    message[-1].data["text"] += segm.data["emjoy"].value

        return self.__class__(message)
