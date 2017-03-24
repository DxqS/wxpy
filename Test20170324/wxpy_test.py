from wxpy import *

bot = Bot()
my_friend = bot.friends().search('Kaiser')


# print(my_friend)
# my_friend.send('Hello WeChat!')


@bot.register()
def print_others(msg):
    print(msg)


@bot.register(my_friend)
def reply_my_friend(msg):
    return 'hello,{},My Boss is busy now,please call him later.'.format(msg.sender.name)


# 获得 Logger
logger = get_wechat_logger(receiver=bot)

# 发送警告
logger.warning('这是一条 WARNING 等级的日志！')

# 捕获可能发生的异常，并发送
try:
    1 / 0
except:
    logger.exception('又出错啦！')

embed()
