from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class BotInfo(BaseModel):
    appid: str
    token: str  # 事件推送令牌
    secret: str  # 接口调用凭证
    type: Literal["official", "miniprogram"] = Field(default="miniprogram")  # 机器人类型
    approve: bool = Field(default=False)  # 是否已通过微信认证
    callback: Optional[HttpUrl] = Field(default=None)  # 是否将事件推送转发到指定 URL


class Config(BaseModel):
    wxmp_bots: list[BotInfo] = Field(default_factory=list)
    wxmp_verify: bool = Field(default=True)  # 是否开启消息签名验证
    wxmp_official_timeout: float = Field(default=4)  # 公众号响应超时时间
