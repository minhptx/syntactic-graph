from collections import defaultdict

from syntactic.transformation.atomic import Lower, Upper, PartOf, SubStr, Constant, Replace


class TransformationModel:
    def __init__(self, raw_graph, transformed_graph):
        self.model = None
        self.raw_graph = raw_graph
        self.transformed_graph = transformed_graph

    def generate_program(self):
        best_operations = defaultdict(lambda: defaultdict(lambda: None))
        sim_map = defaultdict(lambda: defaultdict(lambda: -1))

        candidate_map = TransformationModel.generate(self.raw_graph, self.transformed_graph)

        for start_node, end_node in candidate_map:
            best_operation = max(candidate_map[(start_node, end_node)], key=lambda x: x[0])
            best_operations[start_node][end_node] = best_operation[1]
            sim_map[start_node][end_node] = 1 - best_operation[0]

        # print("Mapping", best_operations)
        path, cost = TransformationModel.dijkstra(sim_map, self.transformed_graph.start_node,
                                                  self.transformed_graph.end_node)
        # print("graph", self.raw_graph.values, self.transformed_graph.values)
        # print(cost)

        operation_path = []
        for i in range(1, len(path)):
            operation_path.append(best_operations[path[i - 1]][path[i]])

        transformed_column_list = []
        raw_column_list = []

        # print(operation_path)
        for operation in operation_path:
            raw_column_list.append(operation.raw_ev.values)
            transformed_column_list.append(operation.transform())

        raw_value_list = defaultdict(lambda: [])
        transformed_value_list = defaultdict(lambda: [])

        for column in transformed_column_list:
            if not column:
                continue
            for i in range(len(column)):
                transformed_value_list[i].append(column[i])

        for column in raw_column_list:
            if not column:
                continue
            for i in range(len(column)):
                raw_value_list[i].append(column[i])

        return raw_value_list, transformed_value_list, cost

    @staticmethod
    def dijkstra(sim_matrix, start_node, end_node):
        vertex_set = list(sim_matrix.keys())
        distance_map = defaultdict(lambda: float("inf"))
        previous_map = defaultdict(lambda: None)

        distance_map[start_node] = 1

        while vertex_set:

            u = min(vertex_set, key=lambda x: distance_map[x])

            vertex_set.remove(u)

            for v in sim_matrix[u]:
                distance = distance_map[u] + sim_matrix[u][v]

                if distance < distance_map[v]:
                    distance_map[v] = distance
                    previous_map[v] = u

        S = []
        # print("Previous", distance_map)

        u = end_node
        while previous_map[u]:
            S.insert(0, u)
            u = previous_map[u]

        S.insert(0, u)
        return S, distance_map[end_node]

    @staticmethod
    def generate(raw_graph, transformed_graph):
        candidate_map = defaultdict(lambda: [])

        for start_node_1 in raw_graph.edge_map:
            for end_node_1 in raw_graph.edge_map[start_node_1]:
                edge_1 = raw_graph.edge_map[start_node_1][end_node_1]
                for start_node_2 in transformed_graph.edge_map:
                    for end_node_2 in transformed_graph.edge_map[start_node_2]:
                        edge_2 = transformed_graph.edge_map[start_node_2][end_node_2]
                        for ev_1 in edge_1.value_list:
                            for ev_2 in edge_2.value_list:
                                candidates = TransformationModel.get_all_candidates(ev_1, ev_2)

                                # print("pair", start_node_2, end_node_2, ev_1.atomic.regex, ev_2.atomic.regex,
                                # candidates)

                                for candidate in candidates:
                                    score = candidate.score_function()
                                    candidate_map[(start_node_2, end_node_2)].append((score, candidate))

        return candidate_map

    @staticmethod
    def get_all_candidates(ev_1, ev_2):
        candidate_operations = []
        for operation in [Lower, Upper, PartOf, Constant, SubStr, Replace]:
            if operation.check_condition(ev_1, ev_2):
                candidate_operations.append(operation(ev_1, ev_2))
        return candidate_operations
