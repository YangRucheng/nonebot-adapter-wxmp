from typing import Type, Union, Mapping, Iterable, Optional, Self
from typing_extensions import override
from pydantic import HttpUrl
from pathlib import Path

from nonebot.adapters import (
    MessageSegment as BaseMessageSegment,
    Message as BaseMessage,
)


class MessageSegment(BaseMessageSegment["Message"]):
    """ 消息段 """

    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def __str__(self) -> str:
        return self.data["text"]

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
        thumb_media_path: Optional[Path] = None,
        thumb_media_id: Optional[str] = None,
        appid: Optional[str] = None,
    ) -> "Miniprogrampage":
        """ 小程序卡片消息段 

        参数：
        - `title` 标题
        - `page_path` 小程序页面路径
        - `thumb_media` 缩略图的二进制数据
        - `thumb_media_path` 缩略图的本地路径
        - `thumb_media_id` 微信公众平台 MediaID
        - `appid` 小程序 AppID （小程序留空，公众号必须填与公众号关联的小程序 AppID）
        """
        return Miniprogrampage("miniprogrampage", {
            "title": title,
            "page_path": page_path,
            "thumb_media": thumb_media,
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

    @override
    def __add__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return Message(self) + (
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return (
            MessageSegment.text(other) if isinstance(other, str) else Message(other)
        ) + self


class Text(MessageSegment):
    """ 文本 消息段 """
    @override
    def __str__(self):
        return self.data["text"]


class Image(MessageSegment):
    """ 图片 消息段 """
    @override
    def __str__(self):
        return f"[image:{self.data['file']!r}]"


class Link(MessageSegment):
    """ 图文链接 消息段 """
    @override
    def __str__(self):
        return f"[link:{self.data['url']!r}]"


class Miniprogrampage(MessageSegment):
    """ 小程序卡片 消息段 """
    @override
    def __str__(self):
        return f"[miniprogrampage:{self.data['page_path']!r}]"


class Voice(MessageSegment):
    """ 音频 消息段 """
    @override
    def __str__(self):
        return f"[voice:{self.data['voice']!r}]"


class Message(BaseMessage[MessageSegment]):
    """ 消息 """

    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
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
