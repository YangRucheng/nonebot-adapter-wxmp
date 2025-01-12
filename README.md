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
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="python">
</p>

### 安装

```bash
pip install nonebot-adapter-wxmp
```
或
```bash
pip install git+https://github.com/YangRucheng/nonebot-adapter-wxmp.git#egg=nonebot-adapter-wxmp
```

### 加载适配器

```python
import nonebot
from nonebot.adapters.wxmp import Adapter as WxmpAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(WxmpAdapter)
```

### 配置

#### 配置 .env 文件

##### 配置 Driver

```dotenv
DRIVER=~fastapi+~httpx
```

##### 配置 Bot

```dotenv
WXMP_BOTS='
[
    {
        "appid": "", # 小程序 AppID 或 公众号开发者 ID，以 wx 开头
        "secret": "", # 小程序或公众号的密钥
    }
]
'
```

#### 配置消息推送

+ URL(服务器地址): `https://example.com/wxmp/revice/<app_id>` 或 `https://example.com/wxmp/revice/<app_id>/`  
+ 消息加密方式：明文模式  
+ 数据格式：推荐 JSON （公众号为XML）

### 适配情况

<div align="center">

|              | 小程序（事件推送） | 小程序（发送消息） | 公众号（事件推送） | 公众号（发送消息） |
| ------------ | ------------------ | ------------------ | ------------------ | ------------------ |
| 文字消息     | ✅                  | ✅                  | ✅                  | ❔                  |
| 图片消息     | ✅                  | ✅                  | ✅                  | ❔                  |
| 图文链接     | ❌                  | ✅                  | ✅                  | ❔                  |
| 小程序卡片   | ✅                  | ✅                  | ❌                  |                    |
| 语音消息     | ❌                  | ❌                  |                    |                    |
| 音乐消息     | ❌                  | ❌                  | ❌                  |                    |
| 视频消息     | ❌                  | ❌                  |                    |                    |
| 小视频消息   | ❌                  | ❌                  |                    |                    |
| 地理位置消息 | ❌                  | ❌                  |                    |                    |

</div>

❌官方不支持 · ✅已适配 · ❔未经测试

> 由于我没有已认证的 公众号/服务号，部分功能无法测试，已测试的事件在 `test/event.json` 中，如有问题请提 Issue！

### 参考文档

#### 微信开发文档

+ [公众号事件推送](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html)
+ [公众号发送消息](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Service_Center_messages.html#客服接口-发消息)
+ [小程序事件推送]()
+ [小程序发送消息](https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/kf-mgnt/kf-message/sendCustomMessage.html)

#### 其他补充信息

+ [不支持表情包](https://developers.weixin.qq.com/community/develop/doc/00000ee4eb8190937f227559f66c00)