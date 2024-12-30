from typing import Type, Union, Mapping, Iterable, Optional, Self
from typing_extensions import override
from pathlib import Path

from nonebot.adapters import Message as BaseMessage, MessageSegment as BaseMessageSegment


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
    def text(cls, text: str) -> Self:
        """ 文本消息段 
        小程序：支持
        公众号：支持
        """
        return cls("text", {"text": text})

    @classmethod
    def image(cls, file: Union[bytes, Path, str]) -> Self:
        """ 图片消息段 
        说明: file 可以是 bytes 或 路径

        小程序：支持
        公众号：支持
        """
        if isinstance(file, bytes):
            return cls("image", {
                "file": file,
            })
        elif isinstance(file, str) or isinstance(file, Path):
            with open(file, "rb") as f:
                return cls("image", {
                    "file": f.read(),
                })
        else:
            raise ValueError("file must be bytes or str(path)")

    @classmethod
    def link(cls, title: str, description: str, url: str, thumb_url: str) -> Self:
        """ 链接消息段 

        小程序：支持
        公众号：不支持
        """
        return cls("link", {
            "title": title,
            "description": description,
            "url": url,
            "thumb_url": thumb_url,
        })

    @classmethod
    def miniprogrampage(cls, title: str, page_path: str, thumb_media: Union[bytes, Path, str]) -> Self:
        """ 小程序卡片消息段 

        小程序：支持
        公众号：不支持
        """
        if isinstance(thumb_media, str) or isinstance(thumb_media, Path):
            with open(thumb_media, "rb") as f:
                thumb_media = f.read()

        return cls("miniprogrampage", {
            "title": title,
            "page_path": page_path,
            "thumb_media": thumb_media,
        })

    @classmethod
    def voice(cls, file: Union[bytes, Path, str]) -> Self:
        """ 语音消息段 

        小程序：不支持
        公众号：支持
        """
        if isinstance(file, str) or isinstance(file, Path):
            with open(file, "rb") as f:
                file = f.read()

        return cls("voice", {
            "voice": file,
        })

    def __iter__(self):
        """ """
        yield self


class Message(BaseMessage[MessageSegment]):
    """ 消息 """

    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        return MessageSegment.text(msg)
