from typing import Optional

from nonebot.exception import (
    AdapterException,
    ActionFailed as BaseActionFailed,
    NetworkError as BaseNetworkError,
    ApiNotAvailable as BaseApiNotAvailable,
)


class WxmpAdapterException(AdapterException):
    def __init__(self):
        super().__init__("WXMP")


class NetworkError(BaseNetworkError, WxmpAdapterException):
    """
    :说明:

      网络错误。

    :参数:

      * ``retcode: Optional[int]``: 错误码
    """

    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class ActionFailed(BaseActionFailed, WxmpAdapterException):
    """
    :说明:

      API 请求返回错误信息。

    :参数:

      * ``retcode: Optional[int]``: 错误码
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.info = kwargs

    def __repr__(self):
        return (
            "<ActionFailed " + ", ".join(f"{k}={v}" for k, v in self.info.items()) + ">"
        )

    def __str__(self):
        return self.__repr__()


class ApiNotAvailable(BaseApiNotAvailable, WxmpAdapterException):
    pass


class EventNotAvailable(BaseApiNotAvailable, WxmpAdapterException):
    pass
