from typing import Type, Union, Mapping, Iterable, Optional, Self, TYPE_CHECKING
from typing_extensions import override
from pydantic import HttpUrl
from pathlib import Path
from enum import Enum

from .exception import *
from nonebot.adapters import (
    MessageSegment as BaseMessageSegment,
    Message as BaseMessage,
)
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


class Text(MessageSegment):
    """ 文本 消息段 """


class Image(MessageSegment):
    """ 图片 消息段 """


class Link(MessageSegment):
    """ 图文链接 消息段 """


class Miniprogrampage(MessageSegment):
    """ 小程序卡片 消息段 """


class Voice(MessageSegment):
    """ 音频 消息段 """


class Video(MessageSegment):
    """ 视频 消息段 """


class Location(MessageSegment):
    """ 位置 消息段 """


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
    睡 = ""
    大哭 = ""
    尴尬 = ""
    发怒 = ""
    调皮 = ""
    呲牙 = ""
    惊讶 = ""
    难过 = ""
    囧 = ""
    抓狂 = ""
    吐 = ""
    偷笑 = ""
    愉快 = ""
    白眼 = ""
    傲慢 = ""
    困 = ""
    惊恐 = ""
    憨笑 = ""
    悠闲 = ""
    咒骂 = ""
    疑问 = ""
    嘘 = ""
    晕 = ""
    衰 = ""
    骷髅 = ""
    敲打 = ""
    再见 = ""
    擦汗 = ""
    抠鼻 = ""
    鼓掌 = ""
    坏笑 = ""
    右哼哼 = ""
    鄙视 = ""
    委屈 = ""
    快哭了 = ""
    阴险 = ""
    亲亲 = ""
    可怜 = ""
    笑脸 = ""
    生病 = ""
    脸红 = ""
    破涕为笑 = ""
    恐惧 = ""
    失望 = ""
    无语 = ""
    嘿哈 = ""
    捂脸 = ""
    奸笑 = ""
    机智 = ""
    皱眉 = ""
    耶 = ""
    吃瓜 = ""
    加油 = ""
    汗 = ""
    天啊 = ""
    Emm = ""
    社会社会 = ""
    旺柴 = ""
    好的 = ""
    打脸 = ""
    哇 = ""
    翻白眼 = ""
    六六六 = ""
    让我看看 = ""
    叹气 = ""
    苦涩 = ""
    裂开 = ""
    嘴唇 = ""
    爱心 = ""
    心碎 = ""
    拥抱 = ""
    强 = ""
    弱 = ""
    握手 = ""
    胜利 = ""
    抱拳 = ""
    勾引 = ""
    拳头 = ""
    OK = ""
    合十 = ""
    啤酒 = ""
    咖啡 = ""
    蛋糕 = ""
    玫瑰 = ""
    凋谢 = ""
    菜刀 = ""
    炸弹 = ""
    便便 = ""
    月亮 = ""
    太阳 = ""
    庆祝 = ""
    礼物 = ""
    红包 = ""
    發 = ""
    福 = ""
    烟花 = ""
    爆竹 = ""
    猪头 = ""
    跳跳 = ""
    发抖 = ""
    转圈 = ""
    流汗 = ""
    西瓜 = ""
    左哼哼 = ""
    怄火 = ""
    哈欠 = ""
    奋斗 = ""
    鬼魂 = ""
    小狗 = ""
    篮球 = ""
    乒乓 = ""
    饭 = ""
    闪电 = ""
    刀 = ""
    足球 = ""
    瓢虫 = ""
    差劲 = ""
    爱你 = ""
    NO = ""
    爱情 = ""
    飞吻 = ""
    茶 = ""
    蜡烛 = ""
    酷 = ""
    饥饿 = ""
    折磨 = ""
    糗大了 = ""
    吓 = ""


class Emjoy(MessageSegment):
    """ 表情（行内） 消息段 """


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
        yield Text("text", {"text": msg})

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
    def from_event(cls, event: type["MessageEvent"]) -> "Message":
        """ 从消息事件转为消息序列 """
        if event.message_type == "text":
            return cls(MessageSegment.text(
                text=getattr(event, "content"),
            ))
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
