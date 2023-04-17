import numpy as np

ACTIONS = {
  0: (0, 0),
  1: (0, 1),
  2: (1, 0),
  3: (1, 1),
  # 4: split
}


class State:

  def __init__(self, player: int = None, values: np.ndarray = None):

    if (player is None) ^ (values is None):
      raise ValueError('player and values must both be None or both not None')
    elif player is None and values is None:
      player, values = 0, np.ones((2, 2), dtype=int)

    if not isinstance(player, int):
      raise TypeError('player must be an integer')

    if player not in [0, 1]:
      raise ValueError(f'player must be 0 or 1 but was {player}')

    if not isinstance(values, np.ndarray):
      raise TypeError('state must be a numpy array')

    if values.shape != (2, 2) or values.dtype != int:
      raise ValueError('state must be a 2x2 numpy array of integers')

    if not ((values >= 0) & (values < 5)).all():
      raise ValueError('state must be between 0 and 4')

    self.player = player
    self.values = sorted_values(values)

  def __copy__(self):
    return State(self.player, self.values)

  def __eq__(self, other):
    return isinstance(other, State) \
      and self.player == other.player \
      and np.array_equal(self.values, other.values)

  def __hash__(self):
    return hash(self.get_tuple())

  def __str__(self):
    return str(self.get_tuple())

  def get_tuple(self) -> tuple:
    return tuple([self.player] + list(self.values.flatten()))

  def next_player(self) -> int:
    return (self.player + 1) % 2

  def is_terminal(self) -> bool:
    for row in self.values:
      if all(row == 0):
        return True
    return False

  def get_possible_actions(self) -> list:
    if self.is_terminal():
      raise ValueError('game is over')

    index, index_next = self.player, self.next_player()
    state = self.values
    possible_actions = []

    # add action if from and to hands are not empty
    for key, (index_from, index_to) in ACTIONS.items():
      if state[index, index_from] > 0 and state[index_next, index_to] > 0:
        possible_actions.append(key)

    # if one hand is empty and second has an even number, add split action
    if sum(state[index] == 0) == 1 and sum(state[index] % 2 == 0) == 2:
      possible_actions.append(4)

    return possible_actions

  def get_next_values(self, action: int):

    if action not in ACTIONS and action != 4:
      raise ValueError(f'invalid action {action}')

    # todo or simply continue and dont increment t
    possible_actions = self.get_possible_actions()
    if action not in possible_actions:
      raise ValueError(f'action {action} is not possible')

    index, state = self.player, self.values.copy()

    if action == 4:
      arr = state[index]
      state[index] = np.full(arr.shape, arr[arr > 0] // 2)
    else:
      index_next = self.next_player()
      index_from, index_to = ACTIONS[action]
      state[index_next, index_to] += state[index, index_from]

      # set 5+ numbers to 0
      state[state >= 5] = 0

    return sorted_values(state)

  def step(self, action: int):
    self.values = self.get_next_values(action)
    self.player = self.next_player()

  def get_next_state_map(self):
    next_states = {}
    for action in self.get_possible_actions():
      next_state = self.__copy__()
      next_state.step(action)
      next_states[action] = next_state

    return next_states

  def get_next_state_set(self):
    return set(self.get_next_state_map().values())

  def get_state_action_map(self):
    next_state_map = self.get_next_state_map()

    state_action_map = {}
    for action, next_state in next_state_map.items():
      if next_state in state_action_map:
        state_action_map[next_state].append(action)
      else:
        state_action_map[next_state] = [action]
    return state_action_map


def sorted_values(values: np.ndarray) -> np.ndarray:
  arr = values.copy()
  arr.sort()
  return arr
