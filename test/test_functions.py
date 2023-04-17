from functions import *
from unittest import TestCase

d1 = {
  'a': 1,
  'b': 2,
  'c': {
    'd': 4,
    'e': 5,
    'f': {},
    'g': {'h': 6}
  }
}

d1_str = """{
  a: 1,
  b: 2,
  c: {
    d: 4,
    e: 5,
    f: {},
    g: { h: 6 }
  }
}"""


class TestFunctions(TestCase):

  def test_get_dictionary_string(self):
    # empty case
    self.assertEqual(get_dictionary_string({}), '{}')

    # max depth reached
    self.assertEqual(get_dictionary_string({'a': 1}, max_depth=0), '{...}')

    # length 1 case
    self.assertEqual(get_dictionary_string({'a': 1}), '{ a: 1 }')

    self.assertEqual(get_dictionary_string(d1), d1_str)

  def test_get_tree_lengths(self):
    self.assertEqual(get_tree_lengths({}), [0])
    self.assertEqual(get_tree_lengths({'a': 1}), [1])
    self.assertEqual(get_tree_lengths({'a': 1, 'b': 2}), [2])

    self.assertEqual(get_tree_lengths(d1), [3, 4, 1])

    self.assertEqual(get_tree_lengths({
      'a': {
        'b': {
          'd': 1
        },
        'c': {
          'e': 2
        }
      }
    }), [1, 2, 2])
