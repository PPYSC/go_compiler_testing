import torch
import numpy as np
import matplotlib.pyplot as plt

from pearl.neural_networks.sequential_decision_making.q_value_networks import VanillaQValueNetwork
from pearl.utils.functional_utils.experimentation.set_seed import set_seed
from pearl.policy_learners.sequential_decision_making.deep_q_learning import DeepQLearning
from pearl.policy_learners.sequential_decision_making.double_dqn import DoubleDQN
from pearl.replay_buffers.sequential_decision_making.fifo_off_policy_replay_buffer import FIFOOffPolicyReplayBuffer
from pearl.utils.functional_utils.train_and_eval.online_learning import online_learning
from pearl.pearl_agent import PearlAgent
from pearl.utils.instantiations.environments.gym_environment import GymEnvironment
from pearl.action_representation_modules.one_hot_action_representation_module import (
    OneHotActionTensorRepresentationModule,
)

from goenv_discreaction import MaskedGoEnv
import datetime
import pickle

set_seed(0)


env = GymEnvironment("CartPole-v1")
env = MaskedGoEnv("./data/data_71421_token_size_filtered.jsonl")
num_actions = env.action_space.n

# VanillaQValueNetwork class uses a simple mlp for approximating the Q values.
#  - Input dimension of the mlp = (state_dim + action_dim)
#  - Size of the intermediate layers are specified as list of `hidden_dims`.
hidden_dims = [64, 64]


# Set up a different instance of a Q value network.

# We will be using a one hot representation for representing actions. So take action_dim = num_actions.
Q_network_DoubleDQN = VanillaQValueNetwork(state_dim=env.observation_space.shape[0],  # dimension of the state representation
                                       action_dim=num_actions,                        # dimension of the action representation
                                       hidden_dims=hidden_dims,                       # dimensions of the intermediate layers
                                       output_dim=1)                                  # set to 1 (Q values are scalars)


# Instead of using the 'network_type' argument, use the 'network_instance' argument.
# Pass Q_value_network as the `network_instance` to the `DoubleDQN` policy learner.
DoubleDQNagent = PearlAgent(
    policy_learner=DoubleDQN(
        state_dim=env.observation_space.shape[0],
        action_space=env.action_space,
        batch_size=64,
        training_rounds=10,
        soft_update_tau=0.75,
        network_instance=Q_network_DoubleDQN,   # pass an instance of Q value network to the policy learner.
        action_representation_module=OneHotActionTensorRepresentationModule(
            max_number_actions=num_actions
        ),
    ),
    replay_buffer=FIFOOffPolicyReplayBuffer(10_000),
)

number_of_episodes = 40000
print_every_x_episodes = 1
learn_after_episode = True

info_DoubleDQN = online_learning(
    agent=DoubleDQNagent,
    env=env,
    number_of_episodes=number_of_episodes,
    print_every_x_episodes=print_every_x_episodes,
    learn_after_episode=True,
)

current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
checkpoint_path = f"./saved_model/ddqn_checkpoint_{current_time}.bin"

with open(checkpoint_path, 'wb') as f:
    pickle.dump(DoubleDQNagent, f)

print("Checkpoint saved.")