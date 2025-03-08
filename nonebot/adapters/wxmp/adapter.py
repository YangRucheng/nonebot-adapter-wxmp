import asyncio
import hashlib
import json
import secrets
from typing import Any, ClassVar, Union, Optional
from urllib.parse import urljoin

import xmltodict
from pydantic import ValidationError
from typing_extensions import override
from nonebot.compat import PYDANTIC_V2
from yarl import URL

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter
from nonebot.drivers import (
    ASGIMixin,
    Driver,
    HTTPClientMixin,
    HTTPServerSetup,
    Request,
    Response,
)
from nonebot.utils import escape_tag

from .bot import Bot
from .config import Config
from .event import (
    MINIPROGRAM_EVENT_CLASSES,
    OFFICIAL_EVENT_CLASSES,
    Event,
)
from .exception import (
    ActionFailed,
    UnkonwnEventError,
)
from .store import OfficialReplyResult
from .utils import log


class Adapter(BaseAdapter):
    _result: ClassVar[OfficialReplyResult] = OfficialReplyResult()

    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.wxmp_config: Config = get_plugin_config(Config)
        self.tasks: set["asyncio.Task"] = set()
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        """适配器名称: `WXMP`"""
        return "WXMP"

    def setup(self) -> None:
        if not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} doesn't support asgi server!"
                f"{self.get_name()} Adapter need a asgi server driver to work."
            )

        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} "
                "doesn't support http client requests!"
                f"{self.get_name()} Adapter needs a HTTPClient Driver to work."
            )

        for bot_info in self.wxmp_config.wxmp_bots:
            self.setup_http_server(
                HTTPServerSetup(
                    path=URL(f"/wxmp/revice/{bot_info.appid}"),
                    method="POST",
                    name=f"{self.get_name()} {bot_info.appid} WebHook",
                    handle_func=self._handle_event,
                )
            )
            self.setup_http_server(
                HTTPServerSetup(
                    path=URL(f"/wxmp/revice/{bot_info.appid}/"),
                    method="POST",
                    name=f"{self.get_name()} {bot_info.appid} WebHook Slash",
                    handle_func=self._handle_event,
                )
            )
            if self.wxmp_config.wxmp_verify:
                self.setup_http_server(
                    HTTPServerSetup(
                        path=URL(f"/wxmp/revice/{bot_info.appid}"),
                        method="GET",
                        name=f"{self.get_name()} {bot_info.appid} Verify",
                        handle_func=self._handle_verify,
                    )
                )
                self.setup_http_server(
                    HTTPServerSetup(
                        path=URL(f"/wxmp/revice/{bot_info.appid}/"),
                        method="GET",
                        name=f"{self.get_name()} {bot_info.appid} Verify Slash",
                        handle_func=self._handle_verify,
                    )
                )

        self.driver.on_shutdown(self.shutdown)

        @self.on_ready
        async def _():
            for bot_info in self.wxmp_config.wxmp_bots:
                if not (bot := self.bots.get(bot_info.appid, None)):
                    bot = Bot(
                        self,
                        self_id=bot_info.appid,
                        bot_info=bot_info,
                        official_timeout=self.wxmp_config.wxmp_official_timeout,
                    )
                    self.bot_connect(bot)
                    log("INFO", f"<y>Bot {escape_tag(bot_info.appid)}</y> connected")

    async def shutdown(self) -> None:
        """关闭 Adapter"""
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )
        self.tasks.clear()

    @classmethod
    def parse_body(cls, data: Union[bytes, str]) -> dict:
        """解析微信公众平台的事件数据"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            res: dict = xmltodict.parse(data)
            if _res := res.get("xml", None):
                return _res
            else:
                return res

    async def _handle_event(self, request: Request) -> Response:
        """处理微信公众平台的事件推送"""
        url = URL(request.url)
        timestamp = url.query.get("timestamp", "")
        nonce = url.query.get("nonce", "")
        signature = url.query.get("signature", "")

        bot = self.bots.get(self._get_appid(url.path), None)

        if not bot or not isinstance(bot, Bot):
            return Response(404, content="Bot not found")

        if not request.content:
            return Response(400, content="Invalid request body")

        concat_string: str = "".join(sorted([bot.bot_info.token, timestamp, nonce]))
        sha1_signature = hashlib.sha1(concat_string.encode("utf-8")).hexdigest()
        if not secrets.compare_digest(sha1_signature, signature):
            return Response(403, content="Invalid signature")

        if bot.bot_info.callback:  # 转发事件推送到指定 URL
            await self._callback(str(bot.bot_info.callback), request)

        payload: dict = self.parse_body(request.content)
        return await self.dispatch_event(bot, payload, self.wxmp_config.wxmp_official_timeout)

    async def dispatch_event(self, bot: Bot, payload: dict, timeout: float) -> Response:
        """分发事件

        参数：
        - `bot`: Bot 对象
        - `payload`: 事件数据
        - `timeout`: 公众号响应超时时间
        """
        try:
            event = self.payload_to_event(bot, payload)
        except Exception as e:
            log("WARNING", f"Failed to parse event {escape_tag(repr(payload))}", e)
        else:
            task = asyncio.create_task(bot.handle_event(event=event))
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)

        if bot.bot_info.type == "official":
            try:
                resp = await self._result.get_resp(event_id=event.get_event_id(), timeout=timeout)
            except asyncio.TimeoutError:
                self._result.clear(event.get_event_id())
                return Response(200, content="success")
            else:
                return resp
        else:
            return Response(200, content="success")

    def payload_to_event(self, bot: Bot, payload: dict) -> Event:
        """将微信公众平台的事件数据转换为 Event 对象"""
        if bot.bot_info.type == "miniprogram":
            for cls in MINIPROGRAM_EVENT_CLASSES:
                try:
                    if PYDANTIC_V2:
                        return cls.model_validate(payload)
                    else:
                        return cls.validate(payload)
                except ValidationError:
                    pass
        elif bot.bot_info.type == "official":
            for cls in OFFICIAL_EVENT_CLASSES:
                try:
                    if PYDANTIC_V2:
                        return cls.model_validate(payload)
                    else:
                        return cls.validate(payload)
                except ValidationError:
                    pass
        else:
            raise ValueError(f"Unknown bot type: {bot.bot_info.type}")
        raise UnkonwnEventError(payload)

    async def _handle_verify(self, request: Request) -> Response:
        """响应微信公众平台的签名验证"""
        url = URL(request.url)
        signature = url.query.get("signature", "")
        echostr = url.query.get("echostr", "")
        timestamp = url.query.get("timestamp", "")
        nonce = url.query.get("nonce", "")

        bot = self.bots.get(self._get_appid(url.path), None)

        if not bot or not isinstance(bot, Bot):
            return Response(404, content="Bot not found")

        concat_string: str = "".join(sorted([timestamp, nonce, bot.bot_info.token]))
        sha1_signature = hashlib.sha1(concat_string.encode("utf-8")).hexdigest()

        if secrets.compare_digest(sha1_signature, signature):
            return Response(200, content=echostr)
        else:
            return Response(403, content="Invalid signature")

    def _get_appid(self, path: str) -> str:
        """从链接中获取 Bot 的 AppID"""
        return path.rstrip("/").split("/")[-1]

    async def _callback(self, url: str, request: Request) -> None:
        """把事件推送转发到指定 URL"""
        try:
            await self.request(
                Request(
                    method=request.method,
                    url=url,
                    headers=request.headers,
                    content=request.content,
                )
            )
        except Exception:
            pass

    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Response:
        """调用微信公众平台 API"""
        access_token = await bot.get_access_token()
        body: Optional[Any] = data.get("json", data.get("data", data.get("body", None)))

        request = Request(
            method=data.get("method", "POST"),
            url=urljoin("https://api.weixin.qq.com", api),
            params={
                "access_token": access_token,
            }
            | data.get("params", {}),
            headers=data.get("headers", {}),
            content=json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None,
            files=data.get("files", None),
        )
        resp = await self.request(request)

        if resp.status_code != 200 or not resp.content:
            raise ActionFailed(resp)

        return resp
