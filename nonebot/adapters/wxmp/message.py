from typing import Type, Union, Mapping, Iterable, Optional, Self
from typing_extensions import override

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
        """ 文本消息段 """
        return cls("text", {"text": text})

    @classmethod
    def image(cls, file: Union[bytes, str]) -> Self:
        """ 图片消息段 """
        return cls("image", {
            "file": file,
        })

    @classmethod
    def link(cls, title: str, description: str, url: str, thumb_url: str) -> Self:
        """ 链接消息段 """
        return cls("link", {
            "title": title,
            "description": description,
            "url": url,
            "thumb_url": thumb_url,
        })

    @classmethod
    def miniprogrampage(cls, title: str, appid: str, page_path: str, thumb_media: str) -> Self:
        """ 小程序卡片消息段 """
        return cls("miniprogrampage", {
            "title": title,
            "appid": appid,
            "page_path": page_path,
            "thumb_media": thumb_media,
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
