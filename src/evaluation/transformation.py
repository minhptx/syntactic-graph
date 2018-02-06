import os
from collections import defaultdict

import numpy as np
import pandas as pd

from syntactic.generation.model import HierarchicalModel
from syntactic.transformation.model import TransformationModel


class TransformationEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.raw_data_dict = defaultdict(lambda: [])
        self.transformed_data_dict = defaultdict(lambda: [])
        self.folder_path = "data/transformation"
        self.name_list = []

    def read_data(self):
        accuracy_list = []

        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")

        for file_name in sorted(os.listdir(raw_data_path))[0:100]:
        # for file_name in ["10.csv"]:
            print("File", file_name)
            #
            # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
            #     continue
            raw_file_path = os.path.join(raw_data_path, file_name)
            transformed_file_path = os.path.join(transformed_data_path, file_name)
            groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)

            raw_input_list = pd.read_csv(raw_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()
            transformed_list = pd.read_csv(transformed_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()
            groundtruth_list = pd.read_csv(groundtruth_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()

            # try:
            raw_model = HierarchicalModel(raw_input_list)
            raw_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:
            #     continue

            cost_map = defaultdict(lambda: defaultdict(lambda: float("inf")))
            result_map = defaultdict(lambda: defaultdict(lambda: None))

            count = len(groundtruth_list)
            true_count = 0

            for idx_1, raw_cluster in enumerate(raw_model.clusters):
                for idx_2, transformed_cluster in enumerate(transformed_model.clusters):
                    print("Length", len(raw_cluster.values), len(transformed_cluster.values))
                    transformation_model = TransformationModel(raw_cluster.pattern_graph,
                                                               transformed_cluster.pattern_graph)

                    result_list, cost = transformation_model.generate_program()

                    cost_map[idx_1][
                        idx_2] = cost - transformed_cluster.pattern_graph.num_edge() / \
                                 raw_cluster.pattern_graph.num_edge()
                    result_map[idx_1][idx_2] = result_list

            for idx_1 in result_map:
                idx_2 = min(cost_map[idx_1].items(), key=lambda x: x[1])[0]
                result_list = result_map[idx_1][idx_2]
                for idx, values in result_list.items():
                    value_str = "".join(values)
                    raw_str = raw_model.clusters[idx_1].pattern_graph.values[idx]

                    print("Value and raw", value_str, "-----", raw_str)
                    raw_idx = raw_input_list.index(raw_str[1:-1])
                    groundtruth = groundtruth_list[raw_idx]

                    if value_str == groundtruth:
                        true_count += 1
                    else:
                        print(value_str, groundtruth)

            accuracy = true_count * 1.0 / count

            accuracy_list.append(accuracy)
            print(accuracy)

        print(np.mean(accuracy_list))


if __name__ == "__main__":
    evaluation = TransformationEvaluation()
    print(evaluation.read_data())
