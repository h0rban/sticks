import networkx as nx
import matplotlib.pyplot as plt
from state import State


def get_dictionary_string(dictionary: dict, max_depth: float = float('inf'),
    level: int = 0, indent: int = 2):
  """
  Returns a string representation of a dictionary in a json-like format.
  :param dictionary: dictionary to be converted to string
  :param level: variable to track the current depth
  :param indent: number of spaces to indent
  :param max_depth: maximum depth of the dictionary to traverse
  :return: string representation of the dictionary
  """
  # empty case
  if not dictionary:
    return '{}'

  # max depth reached
  if level >= max_depth:
    return '{...}'

  # length 1 case
  if len(dictionary) == 1:
    key, value = next(iter(dictionary.items()))
    if not isinstance(value, dict):
      return f'{{ {key}: {value} }}'

  out = '{\n'

  front = (' ' * indent) * (level + 1)
  for key, value in dictionary.items():
    if not isinstance(value, dict):
      out += front + f'{key}: {value}'
    else:
      out += front + f'{key}: '
      out += get_dictionary_string(value, max_depth, level + 1)

    out += ',\n'  # in both cases add a comma at the end

  # remove last comma, add new line and closing bracket after indent
  return out[:-2] + '\n' + ' ' * indent * level + '}'


def print_tree(tree: dict, indent: int = 2, max_depth: float = float('inf')):
  print(get_dictionary_string(tree, max_depth=max_depth, indent=indent))


def get_tree_lengths(dictionary: dict):
  """
  Returns a list of the number of nodes at each level of the tree.
  :param dictionary: dictionary to traverse
  :return: list of integers
  """

  def recursion(tree: dict, level: int = 0):
    if len(lengths) < level + 1:
      lengths.append(0)

    lengths[level] += len(tree)
    for value in tree.values():
      if isinstance(value, dict):
        recursion(value, level + 1)

  lengths = []
  recursion(dictionary)
  return lengths


def build_game_tree():
  """
  Returns a dictionary representation of the game tree.
  :return: dictionary of dictionaries
  """

  def recursion(state: State):

    if state in observed:
      return 'visited'
    else:  # record visited node
      observed.add(state)

    if state.is_terminal():
      return state.next_player()  # same as previous

    tree = {}
    for next_state in state.get_next_state_set():
      tree[next_state] = recursion(next_state)
    return tree

  observed = set()
  initial = State()
  return {initial: recursion(initial)}, observed


def build_winner_map():
  """
  Returns a dictionary mapping states to the player that will
  win from that state.
  :return: dictionary of state -> player
  """

  def add_guaranteed_winner(state, _winner_map):
    next_state_set = state.get_next_state_set()
    winner_list = []
    for next_state in next_state_set:
      if next_state in _winner_map:
        winner_list.append(_winner_map[next_state])

    if len(winner_list) == len(next_state_set):
      first = winner_list[0]
      if all(map(lambda x: x == first, winner_list)):
        _winner_map[state] = first

  def recursion(state: State):

    if state in visited:
      return
    else:
      visited.add(state)

    if state.is_terminal():
      winner_map[state] = state.next_player()  # same as previous player
      return

    for next_state in state.get_next_state_set():
      recursion(next_state)

    add_guaranteed_winner(state, winner_map)

  winner_map, visited = {}, set()
  recursion(State())
  return winner_map, visited


def draw_tree_with_edge_labels(tree, edge_label_tag, secondary_edges,
    figure_size=(8, 6), file_name=None, alpha=.3):
  """
  Draws a graph of the tree with edge labels
  :param tree: graph to draw
  :param edge_label_tag: name of the attribute holding the edge label
  :param secondary_edges: list of edges leading to visited nodes
  :param figure_size: size of the figure
  :param file_name: file name to save the figure to
  :param alpha: transparency of the secondary edges
  """

  def get_tree_node_positions(_tree):

    # For visualization purposes, layout the nodes in topological order
    for i, layer in enumerate(nx.topological_generations(_tree)):
      for node in layer:
        _tree.nodes[node]["layer"] = i
    _pos = nx.multipartite_layout(_tree, subset_key="layer", align="horizontal")

    # Flip the layout so the root node is on top
    for k in _pos:
      _pos[k][-1] *= -1

    return _pos

  def draw_edge_labels(_tree, _pos, _edge_labels, **kwargs):
    el_text = nx.draw_networkx_edge_labels(_tree, _pos,
                                           edge_labels=_edge_labels, **kwargs)
    for _, t in el_text.items():
      t.set_rotation('horizontal')

  # set figure size
  plt.subplots(figsize=figure_size)

  pos = get_tree_node_positions(tree)

  # draw tree
  nx.draw(tree, pos=pos, with_labels=True, node_shape='none')

  # draw edge labels
  edge_labels = {(u, v): l for u, v, l in tree.edges(data=edge_label_tag)}
  draw_edge_labels(tree, pos, edge_labels)

  # add secondary edges
  if secondary_edges:
    for u, v, l in secondary_edges:
      tree.add_edges_from([(u, v, {edge_label_tag: l})])

    # draw edges
    edge_list = [(u, v) for u, v, l in secondary_edges]
    nx.draw_networkx_edges(tree, pos, edgelist=edge_list, style='dashed',
                           alpha=alpha)

    # draw labels
    edge_labels = {(u, v): l for u, v, l in secondary_edges}
    draw_edge_labels(tree, pos, edge_labels, alpha=alpha)

  if file_name:
    plt.savefig(file_name)


class Counter:
  def __init__(self):
    self.value = 0

  def increment(self):
    self.value += 1


def build_graph(max_depth):
  """
  Builds the networkx graph of the game tree.
  :param max_depth: maximum depth of the tree
  :return: graph and secondary edges
  """

  def recursion(state, depth):

    # terminate if the maximum depth is reached
    if depth == 0:
      return

    for next_state, actions in state.get_state_action_map().items():
      if len(actions) == 1:
        actions = actions[0]
      else:
        actions = ','.join(map(str, sorted(actions)))

      if next_state in winner_map:
        winner = winner_map[next_state]
        graph.add_edge(state, f't{counter.value}: {winner}', action=actions)
        counter.increment()
      elif next_state in graph:
        secondary_edges.append((state, next_state, actions))
        # todo can there aver be a duplicate ?
      else:
        graph.add_edge(state, next_state, action=actions)
        recursion(next_state, depth - 1)

  winner_map = build_winner_map()[0]
  graph = nx.DiGraph()
  secondary_edges = []
  counter = Counter()

  recursion(State(), max_depth)

  return graph, secondary_edges


def build_and_draw_tree(max_depth=float('inf'), figure_size=(8, 6),
    file_name=None):
  graph, secondary_edges = build_graph(max_depth)
  draw_tree_with_edge_labels(graph, 'action', secondary_edges,
                             figure_size=figure_size, file_name=file_name)
