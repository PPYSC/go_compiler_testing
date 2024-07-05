
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
        self.observation_space = BoxSpace.from_gym(spaces.Box(low=0, high=127, shape=(10000,), dtype=np.int32))

        self.action_space = BoxActionSpace.from_gym(spaces.Box(low=0, high=1000, shape=(1,), dtype=np.int32))

        self.state = None

    def _observation_tenser2ndarray(self, observation):
        return observation.numpy()

    def step(self, action):
        observation = self._observation_tenser2ndarray(self.observation_space.sample())
        reward = 0.0
        terminated = (random.randint(0, 10) < 5)
        truncated = False

        action_result = ActionResult(observation, reward, terminated, truncated, cost = 0.0)

        return action_result
    
    def reset(self, seed=None):
        

        observation = self._observation_tenser2ndarray(self.observation_space.sample())

        return observation, self.action_space