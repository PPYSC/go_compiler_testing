
import random
import gymnasium as gym

import torch

from gymnasium import spaces
import numpy as np

from pearl.api.action_result import ActionResult
from pearl.utils.instantiations.spaces.box import BoxSpace
from pearl.utils.instantiations.spaces.box_action import BoxActionSpace

class MaskedGoEnv:
    def __init__(self):
        self.observation_space = spaces.Box(low=-1, high=127, shape=(10000,), dtype=np.float32)
        self.action_space = BoxActionSpace.from_gym(spaces.Box(low=0, high=1000, shape=(1,), dtype=np.int32))
        self.state = None
        self.count = 0

    def _state_to_observation(self, state):
        ascii_values = np.array([ord(c) for c in state])
        if len(ascii_values) < 10000:
            padded_ascii_values = np.pad(ascii_values, (0, 10000 - len(ascii_values)), 'constant', constant_values=(-1,))
        else:
            padded_ascii_values = ascii_values[:10000]
        return padded_ascii_values.astype(np.float32)
    
    def _observation_to_state(self, observation):
        characters = [chr(int(value)) for value in obs if int(value) != -1]
        return ''.join(characters)

    def step(self, action):
        

        observation = self.observation_space.sample()
        reward = 0.0
        terminated = (random.randint(0, 10) < 5)
        truncated = False

        print(f'======action: {action}============')

        action_result = ActionResult(observation, reward, terminated, truncated, cost = 0.0)

        return action_result
    
    def reset(self, seed=None):


        observation = self.observation_space.sample()

        return observation, self.action_space

m = MaskedGoEnv()
code = "package main\nfunc helloworld() {\n\tprintln(\"Hello World!\")\n}"
print(code)
obs = m._state_to_observation(code)
print('='*50)
print(len(obs))
ans = m._observation_to_state(obs)
print('='*50)
print(ans)

