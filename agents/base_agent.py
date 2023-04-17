from state import State


class BaseAgent:
  def get_action(self, state: State):
    raise NotImplementedError('get_action not implemented')
