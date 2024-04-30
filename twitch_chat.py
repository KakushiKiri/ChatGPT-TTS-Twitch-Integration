import os
from twitchio.ext import commands

class Twitch_Manager(commands.Bot):
    def __init__(self):
        try:
            super().__init__(token=os.getenv('TWITCH_API_KEY'), prefix='!', initial_channels=('KakushiKiri'))
        except:
            exit('ERROR -- You Dummy, you have the wrong Twitch API Key')

if __name__ == '__main__':
    twitch = Twitch_Manager()