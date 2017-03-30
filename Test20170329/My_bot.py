# coding:utf-8
'''
Created on 2017/3/29.

@author: Dxq
'''
from wxpy import *
import time
import random
from threading import Thread

bot = Bot(cache_path=True)
ts = int(time.time())
remote_admin = ensure_one(bot.friends().search(remark_name="孙大款"))
wxpy_group = ensure_one(bot.groups(True).search(wxid="6411313640@chatroom"))
yf = ensure_one(bot.groups().search("游大神解答"))
groups = [wxpy_group, yf]


@bot.register(Friend, TEXT)
def auto_reply(msg):
    HOUR = int(time.strftime("%H", time.localtime(ts)))
    if msg.sender != remote_admin:
        if HOUR < 9 or HOUR >= 22:
            msg.sender.send("您好，主人还在休息。如有急事，请电联18768120187")


@bot.register(wxpy_group, TEXT, except_self=False)
def sync_special(msg):
    if msg.member.name == "游否" or msg.member.nick_name == "游否":
        sync_message_in_groups(msg, groups, prefix="游大神說：", raise_for_unsupported=False, run_async=True)


def uptime():
    if bot.alive:
        live_time = int(time.time()) - ts
        hour = int(live_time) // 3600
        mins = int(live_time - hour * 3600) // 60
        sec = int(live_time - 3600 * hour - 60 * mins)
        return "报告主人，我已正常运行{}小时{}分{}秒".format(hour, mins, sec)


def report_uptime():
    while True:
        time.sleep(int(random.randrange(1000, 2000)))
        remote_admin.send(uptime())


report_thread = Thread(target=report_uptime(), daemon=True)
report_thread.start()
bot.join()
