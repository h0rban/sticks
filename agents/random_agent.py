import numpy as np
from state import State
from agents.base_agent import BaseAgent


class RandomAgent(BaseAgent):
  def get_action(self, state: State):
    return np.random.choice(state.get_possible_actions())
