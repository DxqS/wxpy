# coding:utf-8
'''
Created on 2017/3/28.

@author: Dxq
'''
#!/usr/bin/env python3
# coding: utf-8

import datetime
import logging
import re
# import sys
import time
from functools import wraps
from threading import Thread

# sys.path.insert(0, '..')
from wxpy import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

bot = Bot(cache_path=True)

# 记录登陆时间戳
login_timestamp = datetime.datetime.now()

# 防止登错账号
if bot.self.nick_name == '游否':
    raise ValueError('Wrong User!')

bot.groups(True)

# 使用 wxid 找到需要管理的微信群
group_ids = ('6411313640@chatroom', '6788356306@chatroom')
groups = list()
for wxid in group_ids:
    g = bot.groups().search(wxid=wxid)[0]
    g.update_group(members_details=True)
    groups.append(g)

# 定义远程管理员 (用于远程管理)，使用备注名更安全
remote_admin = ensure_one(bot.friends().search(remark_name='youfou'))

# 初始化聊天机器人
tuling = Tuling()

# 自动回答关键词

kw_replies = {
    'wxpy 项目主页:\ngithub.com/youfou/wxpy': (
        '项目', '主页', '官网', '网站', 'github', '地址', 'repo', '版本'
    ),
    'wxpy 在线文档:\nwxpy.readthedocs.io': (
        '请问', '文档', '帮助', '怎么', '如何', '请教', '安装', '说明'
    ),
    '必看: 常见问题 FAQ:\nwxpy.readthedocs.io/faq.html': (
        'faq', '常见', '问题', '问答', '什么'
    )
}


def uptime():
    if bot.alive:
        _uptime = datetime.datetime.now() - login_timestamp
        _uptime = str(_uptime).split('.')[0]
        return 'UPTIME: {}'.format(_uptime)


# 定时报告 uptime
def report_uptime():
    while True:
        time.sleep(600)
        remote_admin.send(uptime())


report_thread = Thread(target=report_uptime, daemon=True)
report_thread.start()


def reply_by_keyword(msg):
    for reply, keywords in kw_replies.items():
        for kw in keywords:
            if kw in msg.text.lower():
                logger.info('reply by keyword: \nask: "{}"\nreply: "{}"'.format(msg.text, reply))
                msg.reply(reply)
                return reply


# 验证入群口令
def valid(msg):
    return 'wxpy' in msg.text.lower()


# 自动选择未满的群
def get_group():
    groups.sort(key=len, reverse=True)

    for _group in groups:
        if len(_group) < 490:
            return _group
    else:
        logger.warning('群都满啦！')
        return groups[-1]


# 邀请入群
def invite(user):
    joined = list()
    for group in groups:
        if user in group:
            joined.append(group)
    if joined:
        joined_nick_names = '\n'.join(map(lambda x: x.nick_name, joined))
        logger.info('{} is already in\n{}'.format(user, joined_nick_names))
        user.send('你已加入了\n{}'.format(joined_nick_names))
    else:
        group = get_group()
        logger.info('inviting {} to {}'.format(user, group))
        group.add_members(user, use_invitation=True)


# 限制频率: 指定周期内超过消息条数，直接回复"[奸笑]"
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
                if not isinstance(msg.chat, Group) or msg.is_at:
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
        user.send('Hello {}，你忘了填写加群口令，快回去找找口令吧'.format(user.name))


# 响应好友消息，限制频率
@bot.register(Friend, msg_types=TEXT)
@freq_limit()
def exist_friends(msg):
    # 验证消息
    if valid(msg):
        invite(msg.sender)
    elif reply_by_keyword(msg):
        return
    elif msg.chat == remote_admin and 'uptime' in msg.text.lower():
        return uptime()
    else:
        tuling.do_reply(msg)


# 在其他群中回复被 @ 的消息，限制频率
@bot.register(Group, TEXT)
@freq_limit()
def reply_other_group(msg):
    if msg.chat not in groups and msg.is_at:
        tuling.do_reply(msg)


# 同步群信息
# 远程踢人命令: @<机器人> 移出 @<需要被移出的人>
@bot.register(groups)
def remote_kick(msg):
    if msg.is_at and msg.chat.is_owner and msg.member == remote_admin and '移出' in (msg.text or ''):
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
    else:
        sync_message_in_groups(msg, groups)


welcome_text = '''\U0001F389 欢迎 @{} 加入交流！
\U0001F601 为避免影响交流，除群主外，请勿在本群内使用机器人
\U0001f504 群消息同步处于试验阶段，欢迎提出建议
\U0001F4D6 提问前请查看 t.cn/R6VkJDy'''


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