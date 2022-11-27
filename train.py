from stable_baselines3 import PPO, A2C
from sb3_contrib import RecurrentPPO, QRDQN
#from stable_baselines3.common.evaluation import evaluate_policy
import os
from EldenEnv import EldenEnv
import time


RESUME = False
TIMESTEPS = 6000 * 10
HORIZON_WINDOW = 3000


if not RESUME:
	ts = time.time()
	models_dir = f"models/{int(ts)}/"
	logdir = f"logs/{int(ts)}/"

	if not os.path.exists(models_dir):
		os.makedirs(models_dir)

	if not os.path.exists(logdir):
		os.makedirs(logdir)
else:
	models_dir = f"models/1668613762/"
	logdir = f"logs/1668613762/"


env = EldenEnv(logdir, resume=RESUME, stream_pc_ip='192.168.4.67')

if not RESUME:
	model = A2C('MultiInputPolicy',
						env,
						tensorboard_log=logdir,
						n_steps=HORIZON_WINDOW,
						verbose=1,
						device='cpu')
	iters = 0
else:
	model_path = f"{models_dir}/864000.zip"
	model = RecurrentPPO.load(model_path, env=env)
	iters = 864000 / TIMESTEPS


while True:
	iters += 1
	model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="A2C", log_interval=1)
	model.save(f"{models_dir}/{TIMESTEPS*iters}")