from stable_baselines3 import PPO
import os
from EldenEnv import EldenEnv
import time


ts = time.time()
models_dir = f"models/{int(ts)}/"
logdir = f"logs/{int(ts)}/"

if not os.path.exists(models_dir):
	os.makedirs(models_dir)

if not os.path.exists(logdir):
	os.makedirs(logdir)

env = EldenEnv(logdir)
env.reset()

model = PPO('MlpPolicy', env, verbose=2, tensorboard_log=logdir)

TIMESTEPS = 100000000
iters = 0
while True:
	iters += 1
	model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
	model.save(f"{models_dir}/{TIMESTEPS*iters}")