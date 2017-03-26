# coding:utf-8
'''
Created on 2017/3/26.

@author: Dxq
'''
from xml.etree import ElementTree as ETree
from wxpy import *

bot = Bot(cache_path=True)


@bot.register(msg_types=NOTE)
def get_revoked(msg):
    revoked = ETree.fromstring(msg.raw['Content']).find('revokemsg')
    if revoked:
        revoked_msg = bot.messages.search(id=int(revoked.find('msgid').text))[0]
        bot.file_helper.send(revoked_msg)

bot.start()
