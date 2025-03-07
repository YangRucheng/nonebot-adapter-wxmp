<div align="center">

# NoneBot-Adapter-WXMP

_✨ 微信公众平台客服 协议适配 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/YangRucheng/nonebot-adapter-wxmp/master/LICENSE">
    <img src="https://img.shields.io/github/license/YangRucheng/nonebot-adapter-wxmp" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-adapter-wxmp">
    <img src="https://img.shields.io/pypi/v/nonebot-adapter-wxmp" alt="pypi">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-adapter-wxmp">
    <img src="https://img.shields.io/pypi/dm/nonebot-adapter-wxmp" alt="pypi download">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="python">
</p>

## 安装

适配器安装

```bash
nb adapter install nonebot-adapter-wxmp
```

从PyPI 安装
```bash
pip install nonebot-adapter-wxmp
```
或从 GitHub 仓库安装
```bash
pip install git+https://github.com/YangRucheng/nonebot-adapter-wxmp.git#egg=nonebot-adapter-wxmp
```

## 加载适配器

```python
import nonebot
from nonebot.adapters.wxmp import Adapter as WxmpAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(WxmpAdapter)
```

## 配置 .env 文件

#### 配置 Driver

```dotenv
DRIVER=~fastapi+~httpx
```

#### 配置 Bot

```dotenv
WXMP_BOTS='
[
    {
        "appid": "", # 小程序 AppID 或 公众号开发者 ID，以 wx 开头
        "token": "", # 服务器验证时需要
        "secret": "", # 小程序或公众号的密钥
        "type": "miniprogram", # 填 miniprogram / official
        "callback": "" # 转发到其他 URL
    },
    {
        "appid": "", # 小程序 AppID 或 公众号开发者 ID，以 wx 开头
        "token": "", # 服务器验证时需要
        "secret": "", # 小程序或公众号的密钥
        "type": "official", # 填 miniprogram / official
        "approve": false, # 公众号是否微信认证
        "callback": ""
    }
]

WXMP_OFFICIAL_TIMEOUT=4  # 公众号被动回复超时时间，请根据服务器响应速度填写，必须小于5
WXMP_VERIFY=true  # 是否响应签名验证
'
```

## 配置消息推送

+ URL(服务器地址): `https://example.com/wxmp/revice/<app_id>` 或 `https://example.com/wxmp/revice/<app_id>/`  
+ 消息加密方式：明文模式  
+ 数据格式：推荐 JSON （公众号为 XML）

## 适配情况

<div align="center">

|              | 小程序（事件推送） | 小程序（发送客服消息） | 公众号（事件推送） | 公众号（发送客服消息） | 公众号（被动回复消息） |
| ------------ | ------------------ | ---------------------- | ------------------ | ---------------------- | ---------------------- |
| 文字消息     | ✅                  | ✅                      | ✅                  | ✅                      | ✅                      |
| 图片消息     | ✅                  | ✅                      | ✅                  | ✅                      | ✅                      |
| 图文链接     | ❌                  | ✅                      | ✅                  | ❌                      | ❌                      |
| 小程序卡片   | ✅                  | ✅                      | ❌                  | ❔                      | ❌                      |
| 语音消息     | ❌                  | ❌                      | ✅                  | ✅                      | ✅                      |
| 音乐消息     | ❌                  | ❌                      | ❌                  |                        |                        |
| 视频消息     | ❌                  | ❌                      | ✅                  | ✅                      | ✅                      |
| 小视频消息   | ❌                  | ❌                      | ❌                  | ❌                      | ❌                      |
| 地理位置消息 | ❌                  | ❌                      | ✅                  | ❌                      | ❌                      |
| 图文消息     | ❌                  | ❌                      | ❌                  |                        |                        |
| 菜单消息     | ❌                  | ❌                      | ❌                  |                        | ❌                      |

</div>

✅已适配 · ❌官方不支持或疑似不支持 · ❔暂未测试或暂未适配

## 参考文档

#### 微信开发文档

+ [公众号事件推送](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html)
+ [公众号发送消息](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Service_Center_messages.html#客服接口-发消息)
+ [公众号被动回复](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html)
+ [小程序事件推送](https://developers.weixin.qq.com/miniprogram/dev/framework/server-ability/message-push.html)
+ [小程序发送消息](https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/sendCustomMessage.html)
+ [测试公众号](https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index)

#### 其他补充信息

+ [不支持表情包](https://developers.weixin.qq.com/community/develop/doc/00000ee4eb8190937f227559f66c00)

## 一些注意事项

+ 公众号未微信认证时，不能发送客服消息，只能使用被动回复。
+ 被动回复必须在5秒内响应，超时自动回复空内容。

## 开源协议

[MIT LICENSE](https://github.com/YangRucheng/nonebot-adapter-wxmp/blob/main/LICENSE)