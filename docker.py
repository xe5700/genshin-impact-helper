#!/usr/bin/env python3
import datetime
import json
import logging
import os
import random
import time
from typing import List

import telegram
import telegram.ext
from crontab import CronTab

from genshin import Sign, SignInfo, RoleData
from utils import str2bool
from functools import wraps, partial

time_format = "%Y-%m-%d %M:%S"
cookies: List[str] = []


# noinspection PyTypeChecker


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
    for result in results:
        logging.info(f"\n{result}")
    if tg_bot:
        tg_results = []
        for iii, result in enumerate(results):
            iii: int
            tg_results.append(f"昵称:{roles[iii].nickname}\n" \
                              f"UID:{roles[iii].uid}\n" \
                              f"服务器区域:{roles[iii].region}\n" \
                              + result)
            tg_bot.sendMessage(result)
        logging.info(f"Pushed message to telegram")


def signin_all():
    for i in cookies:
        sign_in(i)


def tg_cmd(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: TgBot = args[0]
        update: telegram.Update = args[1]
        context: telegram.ext.CallbackContext = args[2]
        if update.message.chat_id in self.chat_ids:
            return func(*args, **kwargs)
        else:
            return
    return wrapper


class TgBot:
    bot: telegram.Bot
    chat_ids: List[str]

    def __init__(self, token, chat_ids):
        self.bot = telegram.Bot(token=token)
        self.chat_ids = chat_ids
        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher

    @tg_cmd
    def status(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        for cookie in cookies:
            sinfo = SignInfo(cookie)
            jsigninfos = sinfo.run()
            for i, signinf in enumerate(jsigninfos):
                role = sinfo.roles_data[i]
                signdata = signinf["data"]
                result = f"昵称:{role.nickname}\n" \
                         f"UID:{role.uid}\n" \
                         f"服务器区域:{role.region}\n" \
                         f'签到总天数:{signdata["total_sign_day"]}\n' \
                         f'今日已签到:{signdata["is_sign"]}'
                update.message.reply_text(text=result)

    @tg_cmd
    def signin(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        signin_all()

    def sendMessage(self, msg):
        for i in self.chat_ids:
            chat = self.bot.get_chat(chat_id=i)
            chat.send_message(msg)

    def load(self):
        CommandHandler = telegram.ext.CommandHandler
        CallbackQueryHandler = telegram.ext.CallbackQueryHandler

        BotCmd = telegram.BotCommand
        cmd_signin = BotCmd(command="signin", description="执行签到任务")
        cmd_status = BotCmd(command="status", description="查看签到状态")
        cmds = self.bot.commands
        cmds.append(cmd_signin)
        cmds.append(cmd_status)

        handler_signin = CommandHandler('signin', self.signin)
        handler_status = CommandHandler('status', self.status)
        self.dispatcher.add_handler(handler_signin)
        self.dispatcher.add_handler(handler_status)
        self.updater.start_polling()


tg_bot: TgBot


def main():
    global tg_bot
    env = os.environ
    cron_dict_update = env["CRON_DICT_UPDATE"]
    cookies_env = json.loads(env["COOKIES"])
    if str2bool(env["USE_TELEGRAM"]):
        tg_bot = TgBot(token=env["TG_TOKEN"], chat_ids=json.loads(env["TG_CHAT_IDS"]))
        tg_bot.load()
    if type(cookies_env) == dict:
        cookies.append(cookies_env)
    else:
        for i in cookies_env:
            cookies.append(i)
    signin_all()
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
        signin_all()
        next_run_time()


if __name__ == "__main__":
    main()
