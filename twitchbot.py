import os
import re
import nltk
import json
import random
import requests
import threading
import tensorflow as tf

from twitchio.ext import commands
from twitchio.ext import routines
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


with open('twitch_creds.json', 'r') as f:
    j_obj = json.loads(f.read())

BOT_ACCESS_TOKEN = j_obj['BOT_ACCESS_TOKEN']
BOT_CLIENT_ID = j_obj['BOT_CLIENT_ID']
BOT_PREFIX='?'
CHANNEL='eldenringai'
CHANNEL_ID='837561294'
BOT_CLIENT_SECRET = j_obj['BOT_CLIENT_SECRET']
CHANNEL_CLIENT_ID = j_obj['CHANNEL_CLIENT_ID']
CHANNEL_ACCESS_TOKEN = j_obj['CHANNEL_ACCESS_TOKEN']


nltk.download('popular', quiet=True) #downloads packages

with open('eldenringai.txt', 'r', errors='ignore') as f:
    raw=f.read()

sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

lemmer = nltk.stem.WordNetLemmatizer()
LOGDIR = 'logs'


def get_min_boss_hp():
    newest_log = 0
    for directory in os.listdir(LOGDIR):
        if int(directory) > newest_log:
            newest_log = int(directory)

    experiment_dir = os.path.join(LOGDIR, str(newest_log))
    min_boss_hp = 1
    for ppo_dir in os.listdir(experiment_dir):
        ppo_path = os.path.join(experiment_dir, ppo_dir)
        for event_file in os.listdir(ppo_path):
            for e in tf.compat.v1.train.summary_iterator(os.path.join(ppo_path, event_file)):
                for v in e.summary.value:
                    try:
                        if v.tag == 'boss_hp' and v.simple_value < min_boss_hp:
                            min_boss_hp = v.simple_value
                    except:
                        pass
    return min_boss_hp


def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text))

def response(user_response):
    robot_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robot_response=robot_response+"Thanks for the question. Maybe try again later..."
        return robot_response
    else:
        robot_response = robot_response+sent_tokens[idx]
        return robot_response


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=BOT_ACCESS_TOKEN, prefix=BOT_PREFIX, initial_channels=[CHANNEL])
        self.attempt = 0
        self.lowest_boss_hp = 1
        self.random_question_list = [
            'What actions can the bot take?',
            'How does the code work?',
            'How is the bot trained?',
            'How does the flask server work?',
            'What is the goal of the project?',
            'How does the environment reset function work?',
            'How does the environment step function work?',
            'When did the project start?',
            'How does the reward generator work?',
            'How do you get the player HP?',
            'How do you get the boss HP?',
            'How does the HSV filter work?'
        ]


    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        self.hello.start('Test')

    
    # This routine will run every 5 seconds for 5 iterations.
    @routines.routine(seconds=5)
    async def hello(self, arg: str):
        num_run = 0
        with open('obs_log.txt', 'r') as f:
            for line in f.readlines():
                match = re.search(r"Attempt: (\d+)", line)
                if not match is None:
                    num_run = int(match[1])
        if num_run == 0:
            return
        if num_run != self.attempt:
            self.attempt = num_run

            with open('lowest_boss_hp.txt', 'r') as f:
                try:
                    self.lowest_boss_hp = int(float(f.read()) * 100)
                except:
                    self.lowest_boss_hp = 100

            url = "https://api.twitch.tv/helix/channels?broadcaster_id=" + CHANNEL_ID
            headers = \
            {
                "Client-Id": CHANNEL_CLIENT_ID,
                "Authorization": "Bearer " + CHANNEL_ACCESS_TOKEN,
                "Content-Type": "application/json"
            }
            data = {}
            data["title"] = "A.I. fights Tree Sentinel Attempt: {} !code !howtoaskaquestion".format(self.attempt)
            response = requests.patch(url=url, headers=headers, data=json.dumps(data))
            print(response)
            #await self.connected_channels[0].send('!title A.I. fights Tree Sentinel Attempt: {} !code !howtoaskaquestion'.format(self.attempt))
    

    @commands.command()
    async def askaquestion(self, ctx: commands.Context, *argv):
        q = ""
        for arg in argv:
            q += arg + ' '

        with open('twitchbot_log.txt', 'a') as f:
            f.write(f"Author: {ctx.author.name} Question: {q}\n")
        user_response=q
        bot_response = response(user_response)
        sent_tokens.remove(user_response)
        await ctx.send(f"@{ctx.author.name} {bot_response}")


    @commands.command()
    async def randomquestion(self, ctx: commands.Context):
        random_q = self.random_question_list[random.randint(0, len(self.random_question_list) - 1)]
        user_response=random_q
        bot_response = response(user_response)
        sent_tokens.remove(user_response)
        await ctx.send(f'?askaquestion {random_q}')
        await ctx.send(f'@eldenringai {bot_response}')


while True:
    try:
        bot = Bot()
        bot.run()
    except Exception as e:
        print(str(e))