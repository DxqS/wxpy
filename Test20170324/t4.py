# coding:utf-8
'''
Created on 2017/3/26.

@author: Dxq
'''
import datetime
import logging
import re
from functools import wraps

from wxpy import *

bot = Bot(cache_path=True, console_qr=-2)
bot.messages.max_history = 3000

# 防止登错账号
if bot.self.nick_name == '游否':
    raise ValueError('Wrong User!')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# 初始化图灵机器人 (需填写自己的图灵机器人API KEY, 申请: http://www.tuling123.com/)
tuling = Tuling()

# 使用 wxid 找到需要管理的微信群
group_ids = ('6411313640@chatroom', '6788356306@chatroom')
groups = list()
for wxid in group_ids:
    groups.append(bot.groups().search(wxid=wxid)[0])

# 定义远程管理员 (用于远程管理)，使用备注名更安全
remote_admin = ensure_one(bot.friends().search(remark_name='youfou'))


# 自动选择未满的群
def get_group():
    groups.sort(key=len, reverse=True)

    for _group in groups:
        if len(_group) < 490:
            return _group
    else:
        logger.warning('群都满啦！')
        return groups[-1]


# 验证入群口令
def valid(msg):
    return 'wxpy' in msg.text.lower()


# 邀请入群
def invite(user):
    group = get_group()
    if user in group:
        logger.info('{} is already in {}'.format(user, group))
        user.send('你已加入 {}'.format(group.nick_name))
    else:
        logger.info('inviting {} to {}'.format(user, group))
        group.add_members(user, use_invitation=True)


# 限制频
# 率: 指定周期内超过消息条数，直接回复"[奸笑]"
def freq_limit(period_secs=10, limit_msgs=3):
    def decorator(func):
        @wraps(func)
        def wrapped(msg):
            now = datetime.datetime.now()
            period = datetime.timedelta(seconds=period_secs)
            recent_received = 0
            for m in msg.bot.messages[::-1]:
                if m.sender == msg.sender:
                    if now - m.create_time > period:
                        break
                    recent_received += 1

            if recent_received > limit_msgs:
                return '[奸笑]'
            return func(msg)

        return wrapped

    return decorator


# 响应好友请求
@bot.register(msg_types=FRIENDS)
def new_friends(msg):
    logger.info('accepting {}'.format(msg.card))
    user = msg.card.accept()
    if valid(msg):
        invite(user)
    else:
        user.send('Hello {}，你忘了填写加群口令呢，快回去找找口令吧'.format(user.name))


# 响应好友消息
@bot.register(Friend, msg_types=TEXT)
@freq_limit()
def exist_friends(msg):
    # 验证消息
    if valid(msg):
        invite(msg.sender)
    else:
        tuling.do_reply(msg)


# 在其他群中回复被 @ 的消息，限制频率
@bot.register(Group, TEXT)
@freq_limit()
def reply_other_group(msg):
    if msg.chat not in groups and msg.is_at:
        tuling.do_reply(msg)


# 远程踢人，命令: @<机器人> 移出 @<需要被移出的人>
@bot.register(groups, TEXT)
def remote_kick(msg):
    if not (msg.is_at and msg.chat.is_owner and msg.member == remote_admin and '移出' in msg.text):
        return
    try:
        name_to_kick = re.search(r'移出\s*@(.+?)(?:\u2005?\s*$)', msg.text).group(1)
    except AttributeError:
        remote_admin.send('无法解析命令:\n{}'.format(msg.text))
        return

    member_to_kick = ensure_one(msg.chat.search(name_to_kick))

    if member_to_kick in (bot.self, remote_admin):
        remote_admin.send('不能移出 [{}]'.format(member_to_kick.nick_name))
        return
    else:
        member_to_kick.remove()
        return '已移出 [{}]'.format(name_to_kick)


welcome_text = '''\U0001F389 欢迎 @{} 加入交流！
\U0001F4D6 提问前请看 http://wxpy.readthedocs.io/zh/latest/faq.html
\U0001F601 为避免影响交流，除群主外，请勿在本群内使用机器人'''


# 新人欢迎消息
@bot.register(groups, NOTE)
def welcome(msg):
    try:
        new_member_name = re.search(r'邀请"(.+?)"|"(.+?)"通过', msg.text).group(1)
    except AttributeError:
        return

    return welcome_text.format(new_member_name)


# 堵塞线程，并进入 Python 命令行
embed()