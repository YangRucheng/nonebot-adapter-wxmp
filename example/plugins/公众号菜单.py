from nonebot import get_driver, logger
from nonebot.adapters.wxmp import Bot as WxmpBot

driver = get_driver()


@driver.on_bot_connect
async def _(
    bot: WxmpBot,
):
    logger.info("公众号菜单")
    await bot.create_menu({
        "button": [
            {
                "name": "小程序",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "事件[1]",
                        "key": "click_event_key_1"
                    }, {
                        "type": "click",
                        "name": "事件[2]",
                        "key": "click_event_key_2"
                    }]
            },
            {
                "name": "网页",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "事件[3]",
                        "key": "click_event_key_3"
                    }, {
                        "type": "click",
                        "name": "事件[4]",
                        "key": "click_event_key_4"
                    }]
            }]
    })
