# coding:utf-8
'''
Created on 2017/3/28.

@author: Dxq
'''
from wxpy import *

bot = Bot(cache_path=True)
group = bot.groups().search("啦啦")[0]
print(group.get_avatar('1.jpg'))


@bot.register(group, TEXT, except_self=False)
def rr(msg):
    print(msg)
    print(msg.card)
    print(msg.sender.get_avatar('2.jpg'))
    return 'OK'


embed()

# self.self = Friend(self.core.loginInfo['User'], self)
#    self.file_helper = Chat(wrap_user_name('filehelper'), self)
#
#    self.messages = Messages(bot=self)
#    self.registered = Registered(self)
#
#    self.is_listening = False
#    self.listening_thread = None

# self.temp_dir = tempfile.TemporaryDirectory(prefix='wxpy_')
