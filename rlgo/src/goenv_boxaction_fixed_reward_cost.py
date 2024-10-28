
import itertools
import random
import gymnasium as gym

import torch

from gymnasium import spaces
import numpy as np

from data_io.file_io import data_from_jsonl
from reward import MaskedGoReward
from go_tree_sitter.go_parser import GoParser

from pearl.api.action_result import ActionResult
from pearl.utils.instantiations.spaces.box_action import BoxActionSpace

class MaskedGoEnv:
    def __init__(self, corpus_path):
        self.observation_space = spaces.Box(low=-1, high=127, shape=(10000,), dtype=np.float32)
        self.action_space = BoxActionSpace.from_gym(spaces.Box(low=0, high=1, shape=(1,), dtype=np.int32))
        
        self.parser = GoParser()

        self.state = None
        self.prob0 = None
        self.prob1 = None

        self.iter_count = 0

        self.corpus = itertools.cycle(data_from_jsonl(corpus_path))

        self.rewarder = MaskedGoReward()

    def _get_next_seed_code(self):
        self.state = next(self.corpus)["code"]
        self.prob0, self.prob1 = self.rewarder.get_reward_cost(self.state)

    def _get_total_nodes(self, code):
        def count_nodes(node):
            count = 1
            for child in node.children:
                count += count_nodes(child)
            return count
        
        tree = self.parser.parse(code)
        root_node = tree.root_node
        total_nodes = count_nodes(root_node)
        return total_nodes

    def _state_to_observation(self, state):
        ascii_values = np.array([ord(c) for c in state])
        if len(ascii_values) < 10000:
            padded_ascii_values = np.pad(ascii_values, (0, 10000 - len(ascii_values)), 'constant', constant_values=(-1,))
        else:
            padded_ascii_values = ascii_values[:10000]
        return padded_ascii_values.astype(np.float32)
    
    def _observation_to_state(self, observation):
        characters = [chr(int(value)) for value in observation if int(value) != -1]
        return ''.join(characters)

    def step(self, action):
        old_state = self.state
        old_prob0 = self.prob0
        old_prob1 = self.prob1

        total_nodes = self._get_total_nodes(old_state)
        if total_nodes < 2:
            index = 1
        else:
            index = round((total_nodes - 2) * action[0].item())
            index = 1 + index

        new_state, prob0, prob1 = MaskedGoReward().get_code_reward_cost(old_state, index)

        self.state = new_state
        self.prob0 = prob0
        self.prob1 = prob1

        observation = self._state_to_observation(self.state)

        #reward = (prob0 - old_prob0) - (prob1 - old_prob1)
        reward = (prob0**2)/(prob0**2+prob1**2) - (old_prob0**2)/(old_prob0**2+old_prob1**2)

        cost = 0.0
        if prob0 <= old_prob0:
            cost += 1.0
        if prob1 >= old_prob1:
            cost += 1.0

        if (old_prob0 != -10 and old_prob1 != 10) and (prob0 == -10 and prob1 == 10):
            reward = -100
            self.iter_count = 0
            terminated = True
        elif "func" not in new_state:
            reward = -100
            self.iter_count = 0
            terminated = True
        else:
            if self.iter_count < 9:
                self.iter_count += 1
                terminated = False
            else:
                self.iter_count = 0
                terminated = True

        truncated = False

        action_result = ActionResult(observation, reward, terminated, truncated, cost=cost)

        print(f'='*50)
        print(f"action: {action},  index: {index}")
        print(f'*'*50)
        print(f"old_state:\nprob0: {old_prob0}, prob1: {old_prob1}\n{old_state}")
        print(f'*'*50)
        print(f"new_state:\nprob0: {prob0}, prob1: {prob1}\n{new_state}")
        print(f'*'*50)
        print(f"action_result: {action_result}")
        print(f'='*50)

        return action_result
    
    def reset(self, seed=None):
        if seed is not None:
            for i in range(seed + 1):
                self._get_next_seed_code()
        else:
            self._get_next_seed_code()
            
        observation = self._state_to_observation(self.state)

        return observation, self.action_space



'''
m = MaskedGoEnv("./data/data_71421_token_size_filtered.jsonl")
code = "package main\nfunc helloworld() {\n\tprintln(\"Hello World!\")\n}"
def count_nodes(node):
    count = 1
    for child in node.children:
        count += count_nodes(child)
    return count

   
tree = m.parser.parse(code)
root_node = tree.root_node
total_nodes = count_nodes(root_node)
print(total_nodes)

'''

