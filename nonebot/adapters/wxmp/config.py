from pydantic import Field, HttpUrl, BaseModel
from typing import Literal


class BotInfo(BaseModel):
    appid: str = Field()
    token: str = Field()  # 事件推送令牌
    secret: str = Field()  # 接口调用凭证
    enable_verify: bool = False  # 是否启用响应事件推送验证
    type: Literal["official", "miniprogram"] = Field(default="miniprogram")  # 机器人类型 小程序/公众号：miniprogram / official
    callback: HttpUrl = Field(default=None)  # 是否将事件推送转发到指定 URL


class Config(BaseModel):
    wxmp_bots: list[BotInfo] = Field(default_factory=list)
