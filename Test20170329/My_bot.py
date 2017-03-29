# coding:utf-8
'''
Created on 2017/3/29.

@author: Dxq
'''
from wxpy import *
import time
from threading import Thread

bot = Bot(cache_path=True)
ts = int(time.time())
remote_admin = ensure_one(bot.friends().search(remark_name="孙大款"))


@bot.register(Friend, TEXT)
def auto_reply(msg):
    HOUR = int(time.strftime("%H", time.localtime(ts)))
    if msg.sender != remote_admin:
        if HOUR < 9 or HOUR >= 22:
            msg.sender.send("您好，主人还在休息。如有急事，请电联18768120187")


def uptime():
    if bot.alive:
        live_time = int(time.time()) - ts
        hour = int(live_time) // 3600
        mins = int(live_time - hour * 3600) // 60
        sec = int(live_time - 3600 * hour - 60 * mins)
        return "报告主人，我已正常运行{}小时{}分{}秒".format(hour, mins, sec)


def report_uptime():
    while True:
        time.sleep(1800)
        remote_admin.send(uptime())


report_thread = Thread(target=report_uptime(), daemon=True)
report_thread.start()
bot.join()
