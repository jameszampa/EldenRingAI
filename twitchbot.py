# bot.py
import os # for importing env vars for the bot to use
import re
import nltk
import json
import random
from twitchio.ext import commands
from twitchio.ext import routines
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


with open('twitch_creds.json', 'r') as f:
    ACCESS_TOKEN = json.loads(f.read())['ACCESS_TOKEN']
BOT_PREFIX='?'
CHANNEL='eldenringai'


nltk.download('popular', quiet=True) #downloads packages

with open('eldenringai.txt', 'r', errors='ignore') as f:
    raw=f.read()

sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

lemmer = nltk.stem.WordNetLemmatizer()

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
        robot_response=robot_response+"Try another question..."
        return robot_response
    else:
        robot_response = robot_response+sent_tokens[idx]
        return robot_response


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=ACCESS_TOKEN, prefix=BOT_PREFIX, initial_channels=[CHANNEL])
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
                match = re.search(r"Num resets: (\d+)", line)
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
            
            await self.connected_channels[0].send('!title A.I. fights Tree Sentinel Attempt: {} Avg End Boss HP: {}% !code !howtoaskaquestion'.format(self.attempt, self.lowest_boss_hp))
    

    @commands.command()
    async def askaquestion(self, ctx: commands.Context, arg):
        with open('twitchbot_log.txt', 'a') as f:
            f.write(f"Author: {ctx.author.name} Question: {arg}\n")
        user_response=arg
        bot_response = response(user_response)
        sent_tokens.remove(user_response)
        await ctx.send(f"@{ctx.author.name} {bot_response}")


    @commands.command()
    async def randomquestion(self, ctx: commands.Context):
        random_q = self.random_question_list[random.randint(0, len(self.random_question_list) - 1)]
        user_response=random_q
        bot_response = response(user_response)
        sent_tokens.remove(user_response)
        await ctx.send(f'?askaquestion "{random_q}"')
        await ctx.send(f'@eldenringai {bot_response}')


bot = Bot()
bot.run()