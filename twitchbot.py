# bot.py
import os # for importing env vars for the bot to use
from twitchio.ext import commands
import re


ACCESS_TOKEN='6w9u27lxr0pa6uj2g8sdimah2mv5x7'
CLIENT_ID='qzmzp78jr9jauyfp6nyorwps16pv9v'
BOT_NICK='eldenring_bot'
BOT_PREFIX='!'
CHANNEL='eldenringai'

from twitchio.ext import commands


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=ACCESS_TOKEN, prefix='?', initial_channels=['eldenringai'])

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        
        #ws = self.ws  # this is only needed to send messages within event_ready
        #await ws.send_privmsg("eldenring_bot", f"/me has landed!")

    @commands.command()
    async def update_title(self, ctx: commands.Context):
        if not ctx.author.name in ['eldenringai', 'nightbot']:
            return
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        num_run = 0
        with open('obs_log.txt', 'r') as f:
            for line in f.readlines():
                match = re.search(r"Num resets: (\d+)", line)
                if not match is None:
                    num_run = int(match[1])
        with open('lowest_boss_hp.txt', 'r') as f:
            try:
                lowest_boss_hp = int(float(f.read()) * 100)
            except:
                lowest_boss_hp = 100
        await ctx.send('!title A.I. fights Tree Sentinel Attempt: {} Lowest Boss HP: {}% !code !highlight'.format(num_run, lowest_boss_hp))
    

bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.