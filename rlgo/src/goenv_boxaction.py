
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

        self.iter_count = 0

        self.corpus = data_from_jsonl(corpus_path)

        self.rewarder = MaskedGoReward()

    def _get_next_seed_code(self):
        self.state = next(self.corpus)["code"]

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

        total_nodes = self._get_total_nodes(old_state)
        if total_nodes < 2:
            index = 1
        else:
            index = round((total_nodes - 2) * action[0].item())
            index = 1 + index

        new_code, reward, cost = MaskedGoReward().get_code_reward_cost(self.state, index)

        self.state = new_code
        observation = self._state_to_observation(self.state)

        if reward > cost:
            self.iter_count = 0
            terminated = True
        else:
            if self.iter_count < 10:
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
        print(f"old_state:\n {old_state}")
        print(f'*'*50)
        print(f"new_state:\n {self.state}")
        print(f'*'*50)
        print(f"action_result: {action_result}")
        print(f'='*50)

        return action_result
    
    def reset(self, seed=None):
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

