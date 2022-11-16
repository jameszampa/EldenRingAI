from stable_baselines3 import PPO
from sb3_contrib import RecurrentPPO
#from stable_baselines3.common.evaluation import evaluate_policy
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
TIMESTEPS = 30 * 120 * 10

HORIZON_WINDOW = 30 * 120 * 2
model = RecurrentPPO('MultiInputLstmPolicy',
					 env,
					 tensorboard_log=logdir,
					 n_steps=HORIZON_WINDOW,
					 device="cuda:1",
					 verbose=2)

iters = 0
while True:
	iters += 1
	model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"RecurrentPPO")
	model.save(f"{models_dir}/{TIMESTEPS*iters}")