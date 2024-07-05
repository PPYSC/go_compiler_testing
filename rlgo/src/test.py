from pearl.utils.functional_utils.experimentation.set_seed import set_seed
from pearl.replay_buffers.sequential_decision_making.fifo_off_policy_replay_buffer import FIFOOffPolicyReplayBuffer
from pearl.utils.functional_utils.train_and_eval.online_learning import online_learning
from pearl.pearl_agent import PearlAgent

from pearl.user_envs.wrappers.gym_avg_torque_cost import GymAvgTorqueWrapper
from pearl.utils.instantiations.environments.gym_environment import GymEnvironment
import gymnasium as gym
from pearl.policy_learners.sequential_decision_making.td3 import TD3
from pearl.neural_networks.sequential_decision_making.actor_networks import VanillaContinuousActorNetwork
from pearl.neural_networks.sequential_decision_making.q_value_networks import VanillaQValueNetwork
from pearl.policy_learners.exploration_modules.common.normal_distribution_exploration import (
    NormalDistributionExploration,
)
from pearl.safety_modules.reward_constrained_safety_module import (
    RCSafetyModuleCostCriticContinuousAction,
)
from matplotlib import pyplot as plt
from goenv import MaskedGoEnv
from pearl.pearl_agent import PearlAgent

import torch
import numpy as np


env = GymEnvironment(GymAvgTorqueWrapper(gym.make("HalfCheetah-v4")))
env = MaskedGoEnv()

#print(isinstance(env.observation_space, Discrete))

observation, action_space = env.reset()


#print(type(observation))
print(observation)

action = action_space.sample()[0]

action_np = action.cpu().numpy()

actionresult = env.step(action)

print(actionresult)

#print(action)

#print(action_np)

ob = env.observation_space.sample()
#print(type(ob))
#print(ob)
#print(ob.int().numpy().dtype)


#print(env.observation_space.sample())
#print(env.action_space)