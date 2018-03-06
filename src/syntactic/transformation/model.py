import time
from collections import defaultdict

from syntactic.mapping.model import MappingModel
from syntactic.transformation.atomic import Lower, Upper, Replace, SubStr, Constant, InvSubStr


class TransformationModel:
    def __init__(self, raw_graph, transformed_graph):
        self.model = None
        self.raw_graph = raw_graph
        self.transformed_graph = transformed_graph
        self.model = MappingModel()
        self.model.train_from_graph([self.raw_graph])

    def generate_program(self):
        print("Raw value", self.raw_graph.values)
        print("Transformed value", self.transformed_graph.values)

        best_operations = defaultdict(lambda: defaultdict(lambda: None))
        sim_map = defaultdict(lambda: defaultdict(lambda: -1))

        candidate_map = self.generate(self.raw_graph, self.transformed_graph)

        for start_node, end_node in candidate_map:
            print(candidate_map[(start_node, end_node)])
            best_operation = max(candidate_map[(start_node, end_node)], key=lambda x: x[0])
            best_operations[start_node][end_node] = best_operation[1]
            sim_map[start_node][end_node] = best_operation[0]

        path, cost = TransformationModel.dijkstra(sim_map, self.transformed_graph.start_node,
                                                  self.transformed_graph.end_node)

        if path is None:
            return {}, float("inf")

        operation_path = []
        for i in range(1, len(path)):
            operation_path.append(best_operations[path[i - 1]][path[i]])

        transformed_column_list = []
        print("best transformation")
        for operation in operation_path:
            print(operation.raw_ev.values[:3], operation.transformed_ev.values[:3], operation,
                  operation.score_function(self.model),
                  operation.transform()[:3], len(operation.raw_ev.values))
            transformed_column_list.append(operation.transform())

        transformed_value_list = defaultdict(lambda: [])

        for column in transformed_column_list:
            if not column:
                continue
            for i in range(len(column)):
                transformed_value_list[i].append(column[i])

        return transformed_value_list, cost

    @staticmethod
    def topo_sort(start_node, sim_matrix):
        visited = []
        topo_list = []
        TransformationModel.visit(start_node, visited, topo_list, sim_matrix)
        return topo_list

    @staticmethod
    def visit(n, visited, topo_list, sim_matrix):
        if n in visited:
            return

        for next_node in sim_matrix[n]:
            TransformationModel.visit(next_node, visited, topo_list, sim_matrix)

        visited.append(n)
        topo_list.insert(0, n)

    @staticmethod
    def dijkstra(sim_matrix, start_node, end_node):
        distance_map = defaultdict(lambda: float("-inf"))
        previous_map = defaultdict(lambda: None)

        distance_map[start_node] = 0

        topo_list = TransformationModel.topo_sort(start_node, sim_matrix)

        # print(topo_list, sim_matrix)

        while topo_list:
            current_node = topo_list.pop(0)

            for next_node in sim_matrix[current_node]:
                if distance_map[next_node] < distance_map[current_node] + sim_matrix[current_node][next_node]:
                    distance_map[next_node] = distance_map[current_node] + sim_matrix[current_node][next_node]
                    previous_map[next_node] = current_node

            print("Topo", current_node)

            # print("End")
        current_node = end_node

        path = [end_node]
        print(previous_map)

        while current_node != start_node:
            path.insert(0, previous_map[current_node])
            current_node = previous_map[current_node]
            if current_node is None:
                return None, float("inf")

        print("End")
        return path, distance_map[end_node]


    def generate(self, raw_graph, transformed_graph):

        candidate_map = defaultdict(lambda: [])

        for start_node_1 in raw_graph.edge_map:
            for end_node_1 in raw_graph.edge_map[start_node_1]:
                edge_1 = raw_graph.edge_map[start_node_1][end_node_1]
                for start_node_2 in transformed_graph.edge_map:
                    for end_node_2 in transformed_graph.edge_map[start_node_2]:
                        edge_2 = transformed_graph.edge_map[start_node_2][end_node_2]
                        for ev_1 in edge_1.values:
                            for ev_2 in edge_2.values:
                                candidates = TransformationModel.get_all_candidates(ev_1, ev_2)

                                # print("pair", start_node_2, end_node_2, ev_1.atomic.regex, ev_2.atomic.regex,
                                # candidates)

                                for candidate in candidates:
                                    score = candidate.score_function(self.model)
                                    print(ev_1.values[:3], ev_2.values[:3], candidate, ev_1.atomic, ev_2.atomic, score)
                                    candidate_map[(start_node_2, end_node_2)].append((score, candidate))

        return candidate_map

    @staticmethod
    def get_all_candidates(ev_1, ev_2):
        candidate_operations = []
        for operation in [Lower, Upper, Replace, Constant, SubStr, InvSubStr]:
            if operation.check_condition(ev_1, ev_2):
                candidate_operations.append(operation(ev_1, ev_2))
        return candidate_operations
