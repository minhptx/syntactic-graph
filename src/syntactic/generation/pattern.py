import regex as re
from collections import defaultdict

from syntactic.generation.atomic import START_TOKEN, END_TOKEN, ATOMIC_LIST, ConstantString


class EdgeValue:
    def __init__(self, atomic, nth, length=-1, values=None):
        self.atomic = atomic
        self.nth = nth
        self.length = length
        if values:
            self.values = values
        else:
            self.values = []

    def __eq__(self, ev):
        if self.atomic.name == ev.atomic.name and self.nth == ev.nth and self.length == self.length:
            return True
        return False

    def join(self, ev):
        return EdgeValue(self.atomic, self.nth, self.length, self.values + ev.values)


class Edge:
    def __init__(self, edge_value_list=None):
        if edge_value_list:
            self.value_list = edge_value_list
        else:
            self.value_list = []

    def add_edge_value(self, ev):
        self.value_list.append(ev)

    def join(self, edge):
        matched_list = []
        for ev_1 in self.value_list:
            for ev_2 in edge.value_list:
                if ev_1 == ev_2:
                    # print(ev_1.atomic.name)
                    ev = ev_1.join(ev_2)
                    matched_list.append(ev)
        if matched_list:
            return Edge(matched_list)
        return None


class Graph:
    def __init__(self, text_list):
        self.edge_map = defaultdict(lambda: defaultdict(lambda: None))
        self.text_list = text_list

    def num_edge(self):
        count = 0
        for start_edge in self.edge_map:
            for end_edge in self.edge_map[start_edge]:
                count += len(self.edge_map[start_edge][end_edge].value_list)

        return count

    def intersect(self, other_graph):
        print(self, other_graph)
        graph = Graph(self.text_list + other_graph.text_list)

        start_nodes = (tuple([0] * len(self.text_list)), tuple([0] * len(other_graph.text_list)))

        queue = [start_nodes]

        is_connected = False

        while queue:
            node_1, node_2 = queue.pop()

            for name_1_2 in self.edge_map[node_1]:
                edge_1 = self.edge_map[node_1][name_1_2]
                if not edge_1:
                    continue

                for name_2_2 in other_graph.edge_map[node_2]:
                    edge_2 = other_graph.edge_map[node_2][name_2_2]

                    if not edge_2:
                        continue

                    edge = edge_1.join(edge_2)
                    if edge:
                        graph.edge_map[node_1 + node_2][name_1_2 + name_2_2] = edge
                        queue.append((name_1_2, name_2_2))

                        if edge.value_list[0].atomic == END_TOKEN:
                            is_connected = True

        if not is_connected:
            return None
        return graph

    def is_matched(self, input_str):
        start_node = tuple([0] * len(self.text_list))

        stack = [(start_node, input_str)]

        while stack:
            current_node, current_str = stack.pop(0)

            for end_node in self.edge_map[current_node]:
                for edge in self.edge_map[current_node][end_node]:

                    is_passable = False

                    for edge_value in edge.value_list:
                        if edge_value.atomic == END_TOKEN:
                            return True

                        match = re.match(r"^" + re.escape(edge_value.atomic.regex), current_str)
                        if match:
                            is_passable = True
                            break

                    if is_passable:
                        stack.append((end_node, current_str[len(match.group()):]))

        return False

    @staticmethod
    def atomic_profile(input_str):
        atomic_pos_dict = defaultdict(lambda: [])

        for atomic in ATOMIC_LIST:
            matches = re.finditer(atomic.regex, input_str)
            for match in matches:
                atomic_pos_dict[atomic].append((match.start(), match.end()))

        return atomic_pos_dict

    @staticmethod
    def generate(input_str):
        input_str = "^" + input_str + "$"
        n = len(input_str)
        graph = Graph([input_str])

        atomic_pos_dict = Graph.atomic_profile(input_str)

        graph.edge_map[(0,)][(1,)] = Edge([EdgeValue(START_TOKEN, 1)])
        graph.edge_map[(n - 1,)][(n,)] = Edge([EdgeValue(END_TOKEN, 1)])

        for i in range(1, n - 1):
            for j in range(i + 1, n):

                sub_str = input_str[i:j]

                graph.edge_map[(i,)][(j,)] = Edge(
                    list(Graph.get_nth_edge_values(ConstantString(sub_str), input_str, i, j)))

                for atomic in ATOMIC_LIST:
                    if (i, j) in atomic_pos_dict[atomic]:
                        left_index = atomic_pos_dict[atomic].index((i, j))
                        right_index = len(atomic_pos_dict[atomic]) - left_index
                        graph.edge_map[(i,)][(j,)].add_edge_value(EdgeValue(atomic, left_index + 1))  # variable-length
                        graph.edge_map[(i,)][(j,)].add_edge_value(EdgeValue(atomic, -right_index))  # variable-length
                        graph.edge_map[(i,)][(j,)].add_edge_value(
                            EdgeValue(atomic, left_index + 1, j - i))  # fixed-length
                        graph.edge_map[(i,)][(j,)].add_edge_value(
                            EdgeValue(atomic, -right_index, j - i))  # fixed-length

        return graph


    @staticmethod
    def get_nth_edge_values(atomic, input_str, i, j):
        left_nth = len(re.findall(atomic.regex, input_str[:i])) + 1
        right_nth = len(re.findall(atomic.regex, input_str[j:])) + 1
        return EdgeValue(atomic, left_nth), EdgeValue(atomic, -right_nth)
