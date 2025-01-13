from typing import Any, Union, Callable, Optional, cast, Type, ClassVar
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import override
from yarl import URL
import xmltodict
import asyncio
import hashlib
import secrets
import json
import sys
import re

from nonebot import get_plugin_config
from nonebot.utils import logger_wrapper
from nonebot.exception import WebSocketClosed
from nonebot.utils import DataclassEncoder, escape_tag
from nonebot.drivers import (
    URL,
    Driver,
    Request,
    Response,
    WebSocket,
    ForwardDriver,
    ReverseDriver,
    HTTPServerSetup,
    WebSocketServerSetup,
)

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .event import *
from .utils import log
from .store import OfficialReplyResult
from .config import Config, BotInfo
from .exception import (
    ActionFailed,
    NetworkError,
    ApiNotAvailable,
    UnkonwnEventError,
)

from nonebot import get_plugin_config
from nonebot.drivers import (
    Request,
    Response,
    ASGIMixin,
    WebSocket,
    HTTPServerSetup,
    HTTPClientMixin,
    WebSocketServerSetup
)


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
        """ 适配器名称: `WXMP` """
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
                    name=f"{self.get_name()} {bot_info.appid} WebHook",
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
                        name=f"{self.get_name()} {bot_info.appid} Verify",
                        handle_func=self._handle_verify,
                    )
                )
            if not (bot := self.bots.get(bot_info.appid, None)):
                bot = Bot(self, self_id=bot_info.appid, bot_info=bot_info, official_timeout=self.wxmp_config.wxmp_official_timeout)
                self.bot_connect(bot)
                log("INFO", f"<y>Bot {escape_tag(bot_info.appid)}</y> connected")

        self.driver.on_shutdown(self.shutdown)

    async def shutdown(self) -> None:
        """ 关闭 Adapter """
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )
        self.tasks.clear()

    @classmethod
    def parse_body(cls, data: str) -> dict:
        """ 解析微信公众平台的事件数据 """
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            res: dict = xmltodict.parse(data)
            if _res := res.get("xml", None):
                return _res
            else:
                return res

    async def _handle_event(self, request: Request) -> Response:
        """ 处理微信公众平台的事件推送 """
        url = URL(request.url)
        timestamp = url.query.get("timestamp", "")
        nonce = url.query.get("nonce", "")
        signature = url.query.get("signature", "")

        bot: Bot = self.bots.get(self._get_appid(url.path), None)

        if not bot:
            return Response(404, content="Bot not found")

        if request.content:
            concat_string: str = ''.join(sorted([bot.bot_info.token, timestamp, nonce]))
            sha1_signature = hashlib.sha1(concat_string.encode('utf-8')).hexdigest()
            if not secrets.compare_digest(sha1_signature, signature):
                return Response(403, content="Invalid signature")
            else:
                if bot.bot_info.callback:  # 转发事件推送到指定 URL
                    await self._callback(bot.bot_info.callback, request)

                payload: dict = self.parse_body(request.content)
                return await self.dispatch_event(bot, payload, self.wxmp_config.wxmp_official_timeout)
        else:
            return Response(400, content="Invalid request body")

    async def dispatch_event(self, bot: Bot, payload: dict, timeout: float) -> Response:
        """ 分发事件 

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
            task = asyncio.create_task(
                bot.handle_event(event=event)
            )
            task.add_done_callback(self.tasks.discard)
            self.tasks.add(task)

        if bot.bot_info.type == "official":
            try:
                resp = await self._result.get_resp(event_id=event.get_event_id(), timeout=timeout)
            except asyncio.TimeoutError as e:
                self._result.clear(event.get_event_id())
                return Response(200, content="success")
            else:
                return resp
        else:
            return Response(200, content="success")

    def payload_to_event(self, bot: Bot,  payload: dict) -> type[Event]:
        """ 将微信公众平台的事件数据转换为 Event 对象 """
        if bot.bot_info.type == "miniprogram":
            for cls in MINIPROGRAM_EVENT_CLASSES:
                try:
                    return cls.model_validate(payload)
                except ValidationError:
                    pass
        elif bot.bot_info.type == "official":
            for cls in OFFICIAL_EVENT_CLASSES:
                try:
                    return cls.model_validate(payload)
                except ValidationError:
                    pass
        else:
            raise ValueError(f"Unknown bot type: {bot.bot_info.type}")
        raise UnkonwnEventError(payload)

    async def _handle_verify(self, request: Request) -> Response:
        """ 响应微信公众平台的签名验证 """
        url = URL(request.url)
        signature = url.query.get("signature", "")
        echostr = url.query.get("echostr", "")
        timestamp = url.query.get("timestamp", "")
        nonce = url.query.get("nonce", "")

        bot: Bot = self.bots.get(self._get_appid(url.path), None)

        if not bot:
            return Response(404, content="Bot not found")

        concat_string: str = ''.join(sorted([timestamp, nonce, bot.bot_info.token]))
        sha1_signature = hashlib.sha1(concat_string.encode('utf-8')).hexdigest()

        if secrets.compare_digest(sha1_signature, signature):
            return Response(200, content=echostr)
        else:
            return Response(403, content="Invalid signature")

    def _get_appid(self, path: str) -> str:
        """ 从链接中获取 Bot 的 AppID """
        return path.split('/')[-1]

    async def _callback(self, url: str, request: Request) -> None:
        """ 把事件推送转发到指定 URL """
        try:
            await self.request(
                Request(
                    method=request.method,
                    url=url,
                    headers=request.headers,
                    content=request.content,
                )
            )
        except Exception as e:
            pass

    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Response:
        """ 调用微信公众平台 API """
        access_token = await bot.get_access_token()
        body: Any | None = data.get("json", data.get("data", data.get("body", None)))

        request = Request(
            method=data.get("method", "POST"),
            url=f"https://api.weixin.qq.com/cgi-bin{api}",
            params={
                "access_token": access_token,
            } | data.get("params", {}),
            headers=data.get("headers", {}),
            content=json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None,
            files=data.get("files", None),
        )
        resp = await self.request(request)

        if resp.status_code != 200 or not resp.content:
            raise ActionFailed(resp)

        return resp
