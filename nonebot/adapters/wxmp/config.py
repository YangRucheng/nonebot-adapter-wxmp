from pydantic import Field, HttpUrl, BaseModel
from typing import Literal


class BotInfo(BaseModel):
    appid: str = Field()
    token: str = Field()  # 事件推送令牌
    secret: str = Field()  # 接口调用凭证
    type: Literal["official", "miniprogram"] = Field(default="miniprogram")  # 机器人类型 小程序/公众号：miniprogram / official
    approve: bool = Field(default=False)  # 是否已通过微信认证
    callback: HttpUrl = Field(default=None)  # 是否将事件推送转发到指定 URL


class Config(BaseModel):
    wxmp_bots: list[BotInfo] = Field(default_factory=list)
    wxmp_verify: bool = Field(default=True)  # 是否开启消息签名验证
    wxmp_official_timeout: float = Field(default=4)  # 公众号响应超时时间
