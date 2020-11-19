#!/usr/bin/env python3

import json
import logging
import random
from typing import List

from crontab import CronTab
import time
import os
from .genshin import Sign, makeResult


def sign_in(_cookies: str):
    seconds = random.randint(60, 1200)
    code = -1
    logging.info(f'Sleep for {seconds} seconds ...')
    time.sleep(seconds)

    try:
        jdict = Sign(_cookies).run()
        jstr = json.dumps(jdict, ensure_ascii=False)
        code = jdict['retcode']
    except Exception as e:
        jstr = str(e)

    result = makeResult('Failed', jstr)
    # 0:        success
    # -5003:    already signed in
    if code in [0, -5003]:
        result = makeResult('Success', jstr)
    logging.info(result)


def signin_all(_cookies: List[str]):
    for i in _cookies:
        sign_in(i)


if __name__ == "__main__":
    env = os.environ
    cron_dict_update = env["CRON_DICT_UPDATE"]
    cookies_env = json.loads(env["COOKIES"])
    cookies = []
    if type(cookies_env) == dict:
        cookies.append(json.dumps(cookies_env))
    else:
        for i in cookies_env:
            cookies.append(json.dumps(i))
    signin_all(cookies)
    cron = CronTab(cron_dict_update, loop=True, random_seconds=True)
    while True:
        ct = cron.next(default_utc=False)
        time.sleep(ct)
        print("开始签到")
        signin_all(cookies)
        print("签到完成")

