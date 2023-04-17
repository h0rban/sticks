import numpy as np
from state import State
from unittest import TestCase


class TestState(TestCase):

  def setUp(self) -> None:
    self.initial = State()
    self.state1 = State(1, np.array([[1, 2], [3, 4]]))
    self.state_over = State(0, np.zeros((2, 2), dtype=int))

  def test_constructor(self):
    ones = np.ones((2, 2), dtype=int)

    with self.assertRaises(ValueError):
      State(0, None)

    with self.assertRaises(ValueError):
      State(None, ones)

    with self.assertRaises(TypeError):
      State('0', ones)

    with self.assertRaises(ValueError):
      State(-1, ones)

    with self.assertRaises(ValueError):
      State(2, ones)

    with self.assertRaises(TypeError):
      State(0, '0')

    with self.assertRaises(ValueError):
      State(0, np.ones((3, 3), dtype=int))

    with self.assertRaises(ValueError):
      State(0, ones * 5)

    with self.assertRaises(ValueError):
      State(0, ones * -1)

    with self.assertRaises(ValueError):
      State(0, np.zeros((2, 2)))

    # shows sorting
    self.assertTrue(np.array_equal(
        State(0, np.array([[2, 1], [4, 3]])).values,
        self.state1.values))

  def test_get_tuple(self):
    self.assertEqual(self.initial.get_tuple(), (0, 1, 1, 1, 1))
    self.assertEqual(self.state1.get_tuple(), (1, 1, 2, 3, 4))

  def test_eq(self):
    self.assertEqual(self.initial, State())
    self.assertEqual(self.state1, State(1, np.array([[1, 2], [3, 4]])))
    self.assertNotEqual(self.initial, self.state1)
    self.assertNotEqual(self.initial, 0)
    self.assertNotEqual(self.initial, '0')

  def test_hash(self):
    self.assertEqual(hash(self.initial), hash((0, 1, 1, 1, 1)))
    self.assertEqual(hash(self.state1), hash((1, 1, 2, 3, 4)))
    self.assertNotEqual(hash(self.initial), hash(self.state1))

  def test_str(self):
    self.assertEqual(str(self.initial), '(0, 1, 1, 1, 1)')
    self.assertEqual(str(self.state1), '(1, 1, 2, 3, 4)')

  def test_copy(self):
    self.assertEqual(self.initial, self.initial.__copy__())
    self.assertEqual(self.state1, self.state1.__copy__())
    self.assertNotEqual(self.initial, self.state1.__copy__())

  def test_get_next_agent(self):
    self.assertEqual(self.initial.next_player(), 1)
    self.assertEqual(self.state1.next_player(), 0)

  def test_is_game_over(self):
    self.assertFalse(self.initial.is_terminal())
    self.assertFalse(self.state1.is_terminal())

    self.assertTrue(State(0, np.array([[0, 0], [0, 0]])).is_terminal())
    self.assertTrue(State(1, np.array([[0, 1], [0, 0]])).is_terminal())
    self.assertTrue(State(0, np.array([[0, 0], [1, 0]])).is_terminal())

  def test_get_possible_actions(self):
    def test_helper(state, expected):
      self.assertEqual(state.get_possible_actions(), expected)

    with self.assertRaises(ValueError):
      self.state_over.get_possible_actions()

    test_helper(self.initial, [0, 1, 2, 3])
    test_helper(self.state1, [0, 1, 2, 3])

    test_helper(State(0, np.array([[0, 1], [0, 1]])), [3])
    test_helper(State(0, np.array([[1, 1], [0, 1]])), [1, 3])
    test_helper(State(0, np.array([[0, 2], [3, 4]])), [2, 3, 4])

  def test_get_next_values(self):
    with self.assertRaises(ValueError):
      self.initial.get_next_values(-1)

    with self.assertRaises(ValueError):
      self.initial.get_next_values(5)

    with self.assertRaises(ValueError):
      self.initial.get_next_values(4)

    with self.assertRaises(ValueError):
      self.state_over.get_next_values(0)

    def test_helper(state, action, expected):
      self.assertTrue(np.array_equal(state.get_next_values(action), expected))

    test_helper(self.initial, 0, np.array([[1, 1], [1, 2]]))
    test_helper(self.initial, 1, np.array([[1, 1], [1, 2]]))
    test_helper(self.initial, 2, np.array([[1, 1], [1, 2]]))
    test_helper(self.initial, 3, np.array([[1, 1], [1, 2]]))

    test_helper(self.state1, 0, np.array([[2, 4], [3, 4]]))
    test_helper(self.state1, 1, np.array([[0, 1], [3, 4]]))
    test_helper(self.state1, 2, np.array([[0, 2], [3, 4]]))
    test_helper(self.state1, 3, np.array([[0, 1], [3, 4]]))

    def test_helper2(state_tuple, action, expected):
      state = State(0, np.array(state_tuple).reshape((2, 2)))
      test_helper(state, action, np.array(expected).reshape((2, 2)))

    test_helper2((2, 0, 1, 1), 4, (1, 1, 1, 1))
    test_helper2((0, 2, 1, 1), 4, (1, 1, 1, 1))
    test_helper2((4, 0, 1, 1), 4, (2, 2, 1, 1))
    test_helper2((0, 4, 1, 1), 4, (2, 2, 1, 1))

  def test_step(self):
    with self.assertRaises(ValueError):
      self.initial.step(-1)

    with self.assertRaises(ValueError):
      self.initial.step(5)

    with self.assertRaises(ValueError):
      self.initial.step(4)

    with self.assertRaises(ValueError):
      self.state_over.step(0)

    def test_helper(state, action, expected):
      next_state = state.__copy__()
      next_state.step(action)
      self.assertEqual(next_state, expected)

    test_helper(self.initial, 0, State(1, np.array([[1, 1], [1, 2]])))
    test_helper(self.initial, 1, State(1, np.array([[1, 1], [1, 2]])))
    test_helper(self.initial, 2, State(1, np.array([[1, 1], [1, 2]])))
    test_helper(self.initial, 3, State(1, np.array([[1, 1], [1, 2]])))

    test_helper(self.state1, 0, State(0, np.array([[2, 4], [3, 4]])))
    test_helper(self.state1, 1, State(0, np.array([[0, 1], [3, 4]])))
    test_helper(self.state1, 2, State(0, np.array([[0, 2], [3, 4]])))
    test_helper(self.state1, 3, State(0, np.array([[0, 1], [3, 4]])))

    def test_helper2(state_tuple, action, expected):
      state = State(0, np.array(state_tuple).reshape((2, 2)))
      test_helper(state, action, State(1, np.array(expected).reshape((2, 2))))

    test_helper2((2, 0, 1, 1), 4, (1, 1, 1, 1))
    test_helper2((0, 2, 1, 1), 4, (1, 1, 1, 1))
    test_helper2((4, 0, 1, 1), 4, (2, 2, 1, 1))
    test_helper2((0, 4, 1, 1), 4, (2, 2, 1, 1))

  def test_get_next_state_map(self):
    with self.assertRaises(ValueError):
      self.state_over.get_next_state_map()

    next_state = State(1, np.array([[1, 1], [1, 2]]))
    self.assertEqual(self.initial.get_next_state_map(), {
      0: next_state,
      1: next_state,
      2: next_state,
      3: next_state,
    })

    self.assertEqual(self.state1.get_next_state_map(), {
      0: State(0, np.array([[2, 4], [3, 4]])),
      1: State(0, np.array([[0, 1], [3, 4]])),
      2: State(0, np.array([[0, 2], [3, 4]])),
      3: State(0, np.array([[0, 1], [3, 4]])),
    })

    self.assertEqual(State(0, np.array([[0, 2], [1, 1]])).get_next_state_map(),
                     {
                       2: State(1, np.array([[0, 2], [1, 3]])),
                       3: State(1, np.array([[0, 2], [1, 3]])),
                       4: State(1, np.array([[1, 1], [1, 1]])),
                     })

  def test_get_next_state_set(self):
    with self.assertRaises(ValueError):
      self.state_over.get_next_state_set()

    self.assertEqual(self.initial.get_next_state_set(), {
      State(1, np.array([[1, 1], [1, 2]]))
    })

    self.assertEqual(self.state1.get_next_state_set(), {
      State(0, np.array([[2, 4], [3, 4]])),
      State(0, np.array([[0, 1], [3, 4]])),
      State(0, np.array([[0, 2], [3, 4]])),
    })

    self.assertEqual(State(0, np.array([[0, 2], [1, 1]])).get_next_state_set(),
                     {
                       State(1, np.array([[0, 2], [1, 3]])),
                       State(1, np.array([[1, 1], [1, 1]])),
                     })
