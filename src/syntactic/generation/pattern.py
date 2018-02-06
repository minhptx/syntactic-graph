from collections import defaultdict

import regex as re

from syntactic.generation.atomic import START_TOKEN, END_TOKEN, ATOMIC_LIST, ConstantString, TOKEN_TYPES
from utils.string import lcs


class EdgeValue:
    def __init__(self, atomic, nth, length=-1, neighbor=None, values=None):
        self.atomic = atomic
        self.nth = nth
        self.length = length
        self.neighbor = neighbor
        if values:
            self.values = values
        else:
            self.values = []

    def __eq__(self, ev):
        return self.atomic == ev.atomic and self.nth == ev.nth and self.length == ev.length and self.neighbor == \
               ev.neighbor

    def is_subset(self, ev):
        if self.atomic.is_subset(ev.atomic) or self.atomic == ev.atomic:
            if self.nth == ev.nth and ev.length == -1:
                return True

        return False

    def join(self, ev):
        if self == ev:
            return EdgeValue(self.atomic, self.nth, self.length, self.neighbor, values=self.values + ev.values)


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
                if ev_1 == ev_2 and ev_1 not in matched_list:
                    # print(ev_1.atomic.name)
                    ev = ev_1.join(ev_2)
                    matched_list.append(ev)
        if matched_list:
            return Edge(matched_list)
        return None


class Graph:
    def __init__(self, text_list):
        self.edge_map = defaultdict(lambda: defaultdict(lambda: Edge([])))
        self.values = text_list
        self.start_node = None
        self.end_node = None

    def num_edge(self):
        count = 0
        for start_edge in self.edge_map:
            for end_edge in self.edge_map[start_edge]:
                count += len(self.edge_map[start_edge][end_edge].value_list)
        return count

    def simplify(self):
        graph = Graph(self.values[:])
        for start_node in self.edge_map:
            for end_node in self.edge_map[start_node]:
                edge = self.edge_map[start_node][end_node]
                minimal_list = edge.value_list[:]
                for ev_1 in edge.value_list:
                    for ev_2 in edge.value_list:
                        if ev_2 not in minimal_list:
                            continue
                        if ev_1.is_subset(ev_2):
                            minimal_list.remove(ev_2)

                graph.edge_map[start_node][end_node] = Edge(minimal_list)
        return graph

    def to_paths(self):
        paths = []
        start_node = tuple([0] * len(self.values))

        visited = []

        self.traverse(start_node, [], paths, visited)

        edge_paths = []

        for path in paths:
            edge_path = []
            for idx in range(1, len(path)):
                edge_path.append(self.edge_map[path[idx - 1]][path[idx]])

            edge_paths.append(edge_path)

        return edge_paths

    def traverse(self, current_node, path, paths, visited):
        path.append(current_node)
        visited.append(current_node)

        for end_node in self.edge_map[current_node]:
            if self.edge_map[current_node][end_node]:
                paths.append(path + [end_node])
            else:
                self.traverse(end_node, path, paths, visited)

        visited.remove(current_node)
        path.remove(current_node)

    def intersect(self, other_graph):
        # print(self, other_graph)
        graph = Graph(self.values + other_graph.values)

        graph.start_node = self.start_node + other_graph.start_node

        queue = [(self.start_node, other_graph.start_node)]
        visited = []

        is_connected = False

        while queue:
            node_1, node_2 = queue.pop()
            # print(node_1, node_2)
            visited.append((node_1, node_2))

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
                        if (name_1_2, name_2_2) not in visited:
                            queue.append((name_1_2, name_2_2))

                        if edge.value_list[0].atomic == END_TOKEN:
                            is_connected = True
                            graph.end_node = name_1_2 + name_2_2

        if not is_connected:
            return None
        return graph

    def is_matched(self, input_str, is_add=False):

        stack = [(self.start_node, input_str)]

        while stack:
            current_node, current_str = stack.pop(0)
            # print(current_node, current_str)

            for end_node in self.edge_map[current_node]:
                edge = self.edge_map[current_node][end_node]

                for edge_value in edge.value_list:
                    if edge_value.atomic == END_TOKEN:
                        return True

                    match = re.match(edge_value.atomic.regex, current_str)
                    if match and match.start() == 0:
                        if (end_node, current_str[len(match.group()):]) not in stack:
                            stack.append((end_node, current_str[len(match.group()):]))
                        if is_add:
                            edge_value.values.append(match.group())
        return False

    @staticmethod
    def atomic_profile(input_str):
        atomic_pos_dict = defaultdict(lambda: [])

        for atomic in ATOMIC_LIST:
            matches = re.finditer(atomic.regex, input_str)
            for match in matches:
                atomic_pos_dict[atomic.name].append((match.start(), match.end()))

        return atomic_pos_dict

    @staticmethod
    def token_type_segment(input_str):
        token_type_dict = defaultdict(lambda: [])

        for token_type in TOKEN_TYPES:
            matches = re.finditer(token_type.regex, input_str)
            for match in matches:
                token_type_dict[token_type.name].append((match.start(), match.end()))

        return token_type_dict

    @staticmethod
    def generate(input_str):
        input_str = "^" + input_str + "$"
        n = len(input_str)
        graph = Graph([input_str])

        atomic_pos_dict = Graph.atomic_profile(input_str)
        token_type_dict = Graph.token_type_segment(input_str)

        graph.edge_map[(0,)][(1,)] = Edge([EdgeValue(START_TOKEN, 1)])
        graph.edge_map[(n - 1,)][(n,)] = Edge([EdgeValue(END_TOKEN, 1)])

        for atomic in ATOMIC_LIST:
            for i, j in atomic_pos_dict[atomic.name]:
                sub_str = input_str[i:j]
                if i == 0 or j == n:
                    continue
                left_index = atomic_pos_dict[atomic.name].index((i, j))
                right_index = len(atomic_pos_dict[atomic.name]) - left_index
                graph.edge_map[(i,)][(j,)].add_edge_value(
                    EdgeValue(atomic, left_index + 1, values=[sub_str]))  # variable-length
                graph.edge_map[(i,)][(j,)].add_edge_value(
                    EdgeValue(atomic, -right_index, values=[sub_str]))  # variable-length
                graph.edge_map[(i,)][(j,)].add_edge_value(
                    EdgeValue(atomic, left_index + 1, j - i, values=[sub_str]))  # fixed-length
                graph.edge_map[(i,)][(j,)].add_edge_value(
                    EdgeValue(atomic, -right_index, j - i, values=[sub_str]))  # fixed-length

            for atomic in TOKEN_TYPES:
                for i, j in token_type_dict[atomic.name]:
                    sub_str = input_str[i:j]
                    if i == 0 or j == n:
                        continue
                    left_index = atomic_pos_dict[atomic.name].index((i, j))
                    right_index = len(atomic_pos_dict[atomic.name]) - left_index
                    graph.edge_map[(i,)][(j,)].add_edge_value(
                        EdgeValue(ConstantString(sub_str), left_index + 1, values=[sub_str]))  # variable-length
                    graph.edge_map[(i,)][(j,)].add_edge_value(
                        EdgeValue(ConstantString(sub_str), -right_index, values=[sub_str]))  # variable-length

        graph.start_node = (0,)
        graph.end_node = (n,)

        return graph

    @staticmethod
    def generate_from_list(seed, text_list, sim_map):
        seed = "|".join(list(seed))
        min_sim_sample = min(text_list, key=lambda x: sim_map[seed][x])
        min_sim_sample = "|".join(list(min_sim_sample))
        print(min_sim_sample, seed)
        common_str = lcs(seed, min_sim_sample)
        for cluster_value in text_list:
            print("|".join(list(cluster_value)), common_str)

            common_str = lcs(common_str, "|".join(list(cluster_value)))

        constant_list = [x for x in re.split(r"\|\|+", common_str) if x]

        constant_list = [x.replace("|", "") for x in constant_list]

        regex = "(.*)" + "(.*)".join(["(%s)" % re.escape(x) for x in constant_list]) + "(.*)"

        slot_values = defaultdict(lambda: [])

        for text in text_list:
            matching = re.match(regex, text)
            if matching:
                for idx, match in enumerate(matching.groups()):
                    slot_values[idx + 1].append(match)

        value_list = []

        for idx in slot_values:
            if [x for x in set(slot_values[idx]) if x]:
                value_list.append(slot_values[idx])

        graph = Graph(text_list)

        n = len(value_list) + 2

        graph.edge_map[(0,)][(1,)] = Edge([EdgeValue(START_TOKEN, 1)])
        graph.edge_map[(n - 1,)][(n,)] = Edge([EdgeValue(END_TOKEN, 1)])

        for idx in range(len(value_list)):
            i = idx + 1
            for atomic in ATOMIC_LIST:
                for value in value_list[idx]:
                    if not re.match("^" + atomic.regex + "$", value):
                        break
                else:
                    length_list = [len(x) for x in value_list[idx]]
                    if max(length_list) == min(length_list):
                        length = length_list[0]
                    else:
                        length = -1
                    graph.edge_map[(i,)][(i + 1,)].add_edge_value(EdgeValue(atomic, -1, length, values=value_list[idx]))
            if len(set(value_list[idx])) == 1:
                for j in range(0, len(value_list[idx][0])):

                    for k in range(j + 1, len(value_list[idx][0]) + 1):

                        sub_str = value_list[idx][0][j:k]

                        if k <= j + 3:
                            atomic = ConstantString(value_list[idx][0])
                            graph.edge_map[(i + j * 1.0 / len(value_list[idx][0]),)][
                                (i + k * 1.0 / (len(value_list[idx][0])),)] = Edge(
                                [EdgeValue(atomic, -1, values=[sub_str]),
                                 EdgeValue(atomic, -1, values=[sub_str])])

        graph.start_node = (0,)
        graph.end_node = (n,)
        return graph

    @staticmethod
    def get_nth_edge_values(atomic, input_str, i, j):
        left_nth = len(re.findall(atomic.regex, input_str[:i])) + 1
        right_nth = len(re.findall(atomic.regex, input_str[j:])) + 1
        return left_nth, -right_nth
