from collections import defaultdict
import math
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
        # print("Raw value", self.raw_graph.values)
        # print("Transformed value", self.transformed_graph.values)

        raw_paths = self.raw_graph.to_paths()
        transformed_paths = self.transformed_graph.to_paths()

        # print("Num paths", len(raw_paths), len(transformed_paths))
        # print("Length path", max([len(path) for path in raw_paths]), max([len(path) for path in transformed_paths]))

        best_operations = defaultdict(lambda: defaultdict(lambda: None))

        candidate_map, sim_map = self.generate(self.raw_graph, self.transformed_graph)

        for start_node, end_node in candidate_map:
            best_operations[start_node][end_node] = candidate_map[(start_node, end_node)][1]

        path_scores = []

        for raw_path in raw_paths:
            for transformed_path in transformed_paths:
                raw_node_pairs = [(raw_path[i], raw_path[i + 1]) for i in range(len(raw_path) - 1)]
                transformed_node_pairs = [(transformed_path[i], transformed_path[i + 1]) for i in
                                          range(len(transformed_path) - 1)]

                local_sim_map = {(key, key_1): value for key in sim_map if key in raw_node_pairs for
                                 key_1, value in
                                 sim_map[key].items() if key_1 in transformed_node_pairs}

                for max_score, max_transformation, max_labels in TransformationModel.k_greedy_max_assignment(3,
                        local_sim_map):
                    path_scores.append((max_score, max_transformation, max_labels))

        top_k_result = sorted(path_scores, key=lambda x: x[0], reverse=True)[:5]

        transformed_values_lists = []
        scores = []

        for max_score, max_transformation, max_labels in top_k_result:
            transformed_column = []
            print("Best transformation")
            max_transformation = sorted(zip(max_transformation, max_labels), key=lambda x: x[1])
            for operation, label in max_transformation:
                print("Best", operation, operation.raw_ev.values[:5], operation.transformed_ev.values[:5],
                      operation.score_function(self.model),
                      operation.transform()[:5], len(operation.raw_ev.values),
                      operation.transformed_ev.is_length_fit(operation.raw_ev))
                # print(operation.transformed_ev.min_length, operation.transformed_ev.max_length)
                # print(operation.raw_ev.min_length, operation.raw_ev.max_length)
                transformed_column.append(operation.transform())

            transformed_value_list = defaultdict(lambda: [])

            for column in transformed_column:
                if not column:
                    continue
                for i in range(len(column)):
                    transformed_value_list[i].append(column[i])

            transformed_values_lists.append(transformed_value_list)
            scores.append(max_score)

        return transformed_values_lists, scores

    @staticmethod
    def hungarian_max_assignment(local_sim_map):
        return 0

    @staticmethod
    def k_greedy_max_assignment(k, local_sim_map):

        path_scores = []
        path_transformations = []
        path_list_labels = []

        local_sim_map = sorted(local_sim_map.items(), key=lambda x: x[1][0], reverse=True)

        # print("Sim map", local_sim_map)
        conflicted_mapping = []

        for i in range(k):
            if conflicted_mapping:
                # print("Conflicted", conflicted_mapping)
                label_1, label_2, op_with_score = conflicted_mapping[i]
                mapped_list_1 = [label_1]
                mapped_list_2 = [label_2]
                path_score = op_with_score[0]
                path_transformation = [op_with_score[1]]
                path_labels = [label_2]
            else:
                mapped_list_1 = []
                mapped_list_2 = []
                path_score = 0
                path_transformation = []
                path_labels = []

            for label, op_with_score in local_sim_map:
                label_1, label_2 = label
                if label_1 not in mapped_list_1 and label_2 not in mapped_list_2:
                    path_score += op_with_score[0]
                    path_transformation.append(op_with_score[1])
                    path_labels.append(label_2)
                    if not isinstance(op_with_score[1], Constant):
                        mapped_list_1.append(label_1)
                    mapped_list_2.append(label_2)
                    # if (label_1, label_2, op_with_score) in conflicted_mapping:
                    #     conflicted_mapping.remove((label_1, label_2, op_with_score))
                # elif (label_1, label_2, op_with_score) not in conflicted_mapping:
                elif k == 0:
                    conflicted_mapping.append((label_1, label_2, op_with_score))

            path_scores.append(path_score)
            path_transformations.append(path_transformation)
            path_list_labels.append(path_labels)

        return zip(path_scores, path_transformations, path_list_labels)

    @staticmethod
    def greedy_max_assignment(local_sim_map):
        mapped_list_1 = []
        mapped_list_2 = []

        path_score = 0
        path_transformation = []
        path_labels = []

        for label, op_with_score in sorted(local_sim_map.items(), key=lambda x: x[1][0], reverse=True):
            label_1, label_2 = label
            if label_1 not in mapped_list_1 and label_2 not in mapped_list_2:
                path_score += op_with_score[0]
                path_transformation.append(op_with_score[1])
                path_labels.append(label_2)
                if not isinstance(op_with_score[1], Constant):
                    mapped_list_1.append(label_1)
                mapped_list_2.append(label_2)

        return [(path_score, path_transformation, path_labels)]

    def generate(self, raw_graph, transformed_graph):

        candidate_map = {}
        sim_map = defaultdict(lambda: defaultdict(lambda: None))

        for start_node_1 in raw_graph.edge_map:
            for end_node_1 in raw_graph.edge_map[start_node_1]:
                edge_1 = raw_graph.edge_map[start_node_1][end_node_1]
                for start_node_2 in transformed_graph.edge_map:
                    for end_node_2 in transformed_graph.edge_map[start_node_2]:
                        edge_2 = transformed_graph.edge_map[start_node_2][end_node_2]

                        best_score = 0
                        best_op = None

                        for ev_1 in edge_1.values:
                            for ev_2 in edge_2.values:
                                candidates = TransformationModel.get_all_candidates(ev_1, ev_2)

                                for candidate in candidates:
                                    score = candidate.score_function(self.model)

                                    score *= math.pow(sum([len(x) for x in ev_2.values]), 2) / len(ev_2.values)
                                    # print(score, candidate)
                                    # print(score, candidate, ev_2.values[:3], ev_1.values[:3])

                                    if score >= best_score:
                                        best_score = score
                                        best_op = candidate

                        if best_op is None:
                            continue
                        candidate_map[(start_node_2, end_node_2)] = (best_score, best_op)
                        sim_map[(start_node_1, end_node_1)][(start_node_2, end_node_2)] = (best_score, best_op)

        return candidate_map, sim_map

    @staticmethod
    def get_all_candidates(ev_1, ev_2):
        candidate_operations = []
        for operation in [Lower, Upper, Replace, Constant, SubStr, InvSubStr]:
            if operation.check_condition(ev_1, ev_2):
                candidate_operations.append(operation(ev_1, ev_2))
        return candidate_operations
