
import os
import gym
import time
import numpy as np
import gym.spaces as spaces
from EldenEnv import EldenEnv
from rtgym import RealTimeGymInterface


ts = time.time()
models_dir = f"models/{int(ts)}/"
logdir = f"logs/{int(ts)}/"

if not os.path.exists(models_dir):
	os.makedirs(models_dir)

if not os.path.exists(logdir):
	os.makedirs(logdir)


class MyRealTimeInterface(RealTimeGymInterface):

    def __init__(self):
        self.elden_env = EldenEnv(logdir)

    def get_observation_space(self):
        return self.elden_env.observation_space

    def get_action_space(self):
        return self.elden_env.action_space

    def get_default_action(self):
        return 4

    def send_control(self, control):
        self.observation, self.reward, self.done, self.info = self.elden_env.step(control)

    def reset(self):
        self.elden_env.reset()

    def get_obs_rew_terminated_info(self):
        return self.observation, self.reward, self.done, self.info

    def wait(self):
        pass