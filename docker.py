#!/usr/bin/env python3
import datetime
import json
import logging
import os
import random
import time
from typing import List

import telegram
from crontab import CronTab

from genshin import Sign, SignInfo, RoleData
from utils import str2bool

time_format = "%Y-%m-%d %M:%S"
# noinspection PyTypeChecker
tg_bot: telegram.Bot = None
tg_chatids: List[str] = []


def sign_in(_cookies: str):
    seconds = random.randint(60, 600)
    code = -1
    logging.info(f'Sleep for {seconds} seconds ...')
    # time.sleep(seconds)
    jdict: dict
    results = []
    roles: List[RoleData] = []
    try:
        jdicts = Sign(_cookies).run()
        sinfo = SignInfo(_cookies)
        jsigninfos = sinfo.run()
        roles = sinfo.roles_data
        for iii, jdict in enumerate(jdicts):
            jsigninfo = jsigninfos[iii]
            code = jdict['retcode']
            signdata = jsigninfo["data"]
            result = f'代码: {code}\n' \
                     f'原因: {jdict["message"]}\n' \
                     f'签到天数: {signdata["total_sign_day"]}'
            # 0:        success
            # -5003:    already signed in
            if code in [0, -5003]:
                result = "\n签到成功\n" + result
            else:
                result = "\n签到失败\n" + result
            results.append(result)
    except Exception as e:
        jstr = str(e)
        logging.error(e)
    logging.info(json.dumps(results, ensure_ascii=False))
    if tg_bot:
        tg_results = []
        for iii, result in enumerate(results):
            iii: int
            tg_results.append(f"昵称:{roles[iii].nickname}\n" \
                              f"UID:{roles[iii].uid}\n" \
                              f"服务器区域:{roles[iii].region}\n" \
                              + result)
        for chat_id in tg_chatids:
            chat = tg_bot.get_chat(chat_id=chat_id)
            for result in tg_results:
                chat.send_message(result)


def signin_all(_cookies: List[str]):
    for i in _cookies:
        sign_in(i)


if __name__ == "__main__":
    env = os.environ
    cron_dict_update = env["CRON_DICT_UPDATE"]
    cookies_env = json.loads(env["COOKIES"])
    cookies = []
    if str2bool(env["USE_TELEGRAM"]):
        tg_bot = telegram.Bot(token=env["TG_TOKEN"])
        tg_chatids = json.loads(env["TG_CHAT_IDS"])
    if type(cookies_env) == dict:
        cookies.append(cookies_env)
    else:
        for i in cookies_env:
            cookies.append(i)
    signin_all(cookies)
    cron = CronTab(cron_dict_update, loop=True, random_seconds=True)


    def next_run_time():
        nt = datetime.datetime.now().strftime(time_format)
        delayt = cron.next(default_utc=False)
        nextrun = datetime.datetime.now() + datetime.timedelta(seconds=delayt)
        nextruntime = nextrun.strftime(time_format)
        print(f"Current running datetime: {nt}")
        print(f"Next run datetime: {nextruntime}")


    next_run_time()
    while True:
        ct = cron.next(default_utc=False)
        time.sleep(ct)
        print("Starting signing")
        signin_all(cookies)
        next_run_time()
