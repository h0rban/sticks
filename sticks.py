from state import State
from agents.base_agent import BaseAgent


class Sticks:

  def __init__(self, agent1: BaseAgent, agent2: BaseAgent, log=False):
    if not isinstance(agent1, BaseAgent) or not isinstance(agent2, BaseAgent):
      raise ValueError('agents must be of type BaseAgent')

    self.log = log
    self.t = 0
    self.state = State()
    self.agents = [agent1, agent2]

  def step(self):

    state = self.state.__copy__()
    if state.is_terminal():
      raise ValueError('game is over')

    action = self.agents[state.player].get_action(state)
    self.state.step(action)

    if self.log:
      print({
        't': self.t,
        'state': state.get_tuple()[1:],
        'agent': state.player,
        'action': action,
        'next_state': self.state.get_tuple()[1:],
        'game_over': self.state.is_terminal()
      })

    self.t += 1

  def play(self, max_steps=100):
    for _ in range(max_steps):
      self.step()
      if self.state.is_terminal():
        break
