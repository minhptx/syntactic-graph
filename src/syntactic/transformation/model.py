from collections import defaultdict

from syntactic.generation.model import HierarchicalModel
from syntactic.transformation.atomic import Lower, Upper, PartOf, SubStr, Constant


class TransformationModel:
    def __init__(self, raw_graph, transformed_graph):
        self.model = None
        self.raw_graph = raw_graph
        self.transformed_graph = transformed_graph

    def generate_program(self):
        raw_paths = self.raw_graph.to_paths()
        transformed_paths = self.transformed_graph.to_paths()
        best_operations = defaultdict(lambda: defaultdict(lambda: []))

        for idx_1, raw_path in enumerate(raw_paths):
            for idx_2, transformed_path in enumerate(transformed_paths):
                candidate_map = TransformationModel.generate(raw_path, transformed_path)

                for edge in candidate_map:
                    best_operations[idx_1][idx_2].append(max(candidate_map[edge], key=lambda x: x[0])[1])

        return best_operations

    @staticmethod
    def generate(raw_path, transformed_path):
        candidate_map = defaultdict(lambda: [])

        for idx_1, edge_1 in enumerate(raw_path):
            for idx_2, edge_2 in enumerate(transformed_path):
                for ev_1 in edge_1.value_list:
                    for ev_2 in edge_2.value_list:
                        candidates = TransformationModel.get_all_candidates(ev_1, ev_2)

                        for candidate in candidates:
                            score = candidate.score()
                            if score != 0:
                                candidate_map[idx_1].append((score, candidate))

        return candidate_map

    @staticmethod
    def get_all_candidates(ev_1, ev_2):
        candidate_operations = []
        candidate_operations.append(Lower(ev_1, ev_2))
        candidate_operations.append(Upper(ev_1, ev_2))
        candidate_operations.append(PartOf(ev_1, ev_2))
        candidate_operations.append(Constant(None, ev_2))
        candidate_operations.append(SubStr(ev_1, ev_2))
        return candidate_operations