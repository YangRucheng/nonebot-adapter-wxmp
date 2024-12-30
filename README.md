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

## 安装

```bash
pip install nonebot-adapter-wxmp
```

## 加载适配器

```python
import nonebot
from nonebot.adapters.wxmp import Adapter as WxmpAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(WxmpAdapter)
```

## 配置

### 配置 .env

```dotenv
WXMP_BOTS='
[
    {
        "appid": "",
        "token": "", 
        "secret": "",
        "enable_verify": true
    }
]
'
```

## 使用

### 消息推送

URL(服务器地址): `https://example.com/wxmp/revice/<app_id>`
Token(令牌)：随意
消息加密方式：明文模式
数据格式：JSON

## 开发进度

### 小程序客服消息

- [x] 文字消息
- [x] 图片消息
- [x] 图文链接
- [x] 小程序卡片
  
### 公众号客服消息

- [x] 文字消息
- [x] 图片消息
- [ ] 语音消息
- [ ] 视频消息
- [ ] 音乐消息