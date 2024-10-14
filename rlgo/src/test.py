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


from goenv_boxaction_fixed_reward_cost import MaskedGoEnv

set_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

corpus_path = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment_token_size_filtered.jsonl"
env = MaskedGoEnv(corpus_path)

# setup RCTD3 algorithm, TD3 with reward constraint safety module
rctd3_agent = PearlAgent(
                    policy_learner=TD3(
                        state_dim=env.observation_space.shape[0],
                        action_space=env.action_space,
                        actor_hidden_dims= [256, 256],
                        critic_hidden_dims= [256, 256],
                        training_rounds= 1,
                        batch_size= 256,
                        actor_network_type= VanillaContinuousActorNetwork,
                        critic_network_type= VanillaQValueNetwork,
                        actor_soft_update_tau= 0.005,
                        critic_soft_update_tau= 0.005,
                        actor_learning_rate= 1e-3,
                        critic_learning_rate= 3e-4,
                        discount_factor= 0.99,
                        actor_update_freq= 2,
                        actor_update_noise= 0.2,
                        actor_update_noise_clip= 0.5,
                        exploration_module=NormalDistributionExploration(
                            mean=0.0,
                            std_dev=0.1,
                            ),
                    ),
                    replay_buffer=FIFOOffPolicyReplayBuffer(
                        capacity=100000,
                        has_cost_available=True
                    ),
                    safety_module=RCSafetyModuleCostCriticContinuousAction(
                        state_dim=env.observation_space.shape[0],
                        action_space=env.action_space,
                        critic_hidden_dims= [256, 256],
                        constraint_value=0.4,
                        lambda_constraint_ub_value=200.0,
                        lr_lambda=1e-3
                    ),
                ) 

# Run RCTD3 on the environment

number_of_episodes = 15000
print_every_x_episodes = 1
learn_after_episode = True

save_every_x_episodes = 2

check_point_prefix = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/saved_model/rctd3_fixed_reward_cost_checkpoint"


'''rctd3_info = online_learning(
    rctd3_agent,
    env,
    number_of_episodes=number_of_episodes,
    print_every_x_episodes=print_every_x_episodes,
    learn_after_episode=learn_after_episode,
)'''

total_steps = 0
total_episodes = 0
while True:
    if total_episodes >= number_of_episodes:
        break
    old_total_steps = total_steps
    episode_info, episode_total_steps = run_episode(
        rctd3_agent,
        env,
        learn=True,
        exploit=False,
        learn_after_episode=learn_after_episode,
        total_steps=old_total_steps,
    )
    total_steps += episode_total_steps
    total_episodes += 1
    if total_episodes % print_every_x_episodes == 0:
        print(
                f"episode {total_episodes}, step {total_steps}, agent={rctd3_agent}, env={env}",
            )
        for key in episode_info:
                print(f"{key}: {episode_info[key]}")

    if total_episodes % save_every_x_episodes == 0:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = check_point_prefix + f"_{current_time}_episodes_{total_episodes}.bin"
        #checkpoint_path = f"./saved_model/rctd3_fixed_reward_cost_checkpoint_{current_time}.bin"
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(rctd3_agent, f)
        print("+"*50)
        print(f"Checkpoint saved:\n{checkpoint_path}\n")
        print("+"*50)

current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
checkpoint_path = check_point_prefix + f"_{current_time}_episodes_{total_episodes}.bin"
#checkpoint_path = f"./saved_model/rctd3_fixed_reward_cost_checkpoint_{current_time}.bin"
with open(checkpoint_path, 'wb') as f:
    pickle.dump(rctd3_agent, f)
print("+"*50)
print(f"Checkpoint saved:\n{checkpoint_path}\n")
print("+"*50)