from nonebot.adapters.wxmp import Adapter as WxmpAdapter

import nonebot

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(WxmpAdapter)

# 在这里加载插件
nonebot.load_plugins("plugins")  # 本地插件

if __name__ == "__main__":
    nonebot.run(
        forwarded_allow_ips="*",
    )
