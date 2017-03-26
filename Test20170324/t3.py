# coding:utf-8
'''
Created on 2017/3/26.

@author: Dxq
'''
from wxpy import *

bot = Bot()

tuling = Tuling('你的 API KEY (http://www.tuling123.com/)')
my_friend = ensure_one(bot.friends().search('好友的名称'))


@bot.register(my_friend, TEXT)
def tuling_reply(msg):
    tuling.do_reply(msg)


bot.start()