import os
from pprint import pprint

import requests

tg_sec = os.environ['TELEGRAM_SEC']
bot_token = os.environ['TELEGRAM_TOKEN']
test_url = "https://bot.devenney.io/{}/roll".format(tg_sec)

def get_url(method):
    return "https://api.telegram.org/bot{}/{}".format(bot_token,method)


r = requests.get(get_url("setWebhook"), data={"url": test_url})
r = requests.get(get_url("getWebhookInfo"))
pprint(r.status_code)
pprint(r.json())
