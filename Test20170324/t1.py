# coding:utf-8
'''
Created on 2017/3/26.

@author: Dxq
'''


import logging

from wxpy import *

logging.basicConfig(level=logging.INFO)

bot = Bot(cache_path=True)

card_msg = None
no_card_notice = '名片尚未确认，请手动发送到文件传输助手'


# 第一步: 手动向自己的文件传输助手发送一次所需的名片
@bot.register(bot.file_helper, CARD, except_self=False)
def get_card_msg_to_send(msg):
    print(msg.card)
    global card_msg
    logging.info('获得了名片: {}'.format(msg.card.name))
    card_msg = msg


# 第二步: 转发名片 (请根据自己的需求定义)
@bot.register(Friend, TEXT)
def send_card(msg):
    # 若好友消息包含"名片"，则回复名片
    if '名片' in msg.text:
        if card_msg:
            msg.reply_raw_msg(
                card_msg.raw['MsgType'],
                card_msg.raw['Content'])
            logging.info('发送了名片: {}'.format(card_msg.card.name))
        else:
            logging.warning(no_card_notice)


logging.info(no_card_notice)

embed()