from pearl.utils.functional_utils.train_and_eval.online_learning import run_episode
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


import torch
import numpy as np
import datetime
import pickle

set_seed(0)


from goenv_boxaction import MaskedGoEnv

set_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

corpus_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment_token_size_filtered_10.jsonl"
env = MaskedGoEnv(corpus_path)

#########################
checkpoint_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/saved_model_test/rctd3_fixed_reward_cost_checkpoint_20240910_131902_episodes_1500_final.bin"
with open(checkpoint_path, 'rb') as f:
    loaded_rctd3_agent = pickle.load(f)
#########################

number_of_episodes = 5
print_every_x_episodes = 1

total_steps = 0
total_episodes = 0
while True:
    if total_episodes >= number_of_episodes:
        break
    old_total_steps = total_steps
    episode_info, episode_total_steps = run_episode(
        loaded_rctd3_agent,
        env,
        learn=False,
        exploit=False,
    )
    total_steps += episode_total_steps
    total_episodes += 1
    if total_episodes % print_every_x_episodes == 0:
        print(
                f"episode {total_episodes}, step {total_steps}, agent={loaded_rctd3_agent}, env={env}",
            )
        for key in episode_info:
                print(f"{key}: {episode_info[key]}")