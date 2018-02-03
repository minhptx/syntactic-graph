from collections import defaultdict

import os
import pandas as pd

from syntactic.generation.model import HierarchicalModel


class SimplicationEvaluation:
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

        # for file_name in sorted(os.listdir(raw_data_path))[0:40]:
        for file_name in ["118.csv"]:
            print(file_name)
            #
            # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
            #     continue
            raw_file_path = os.path.join(raw_data_path, file_name)
            transformed_file_path = os.path.join(transformed_data_path, file_name)
            groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)

            raw_list = pd.read_csv(raw_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()
            transformed_list = pd.read_csv(transformed_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()
            groundtruth_list = pd.read_csv(groundtruth_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()

            raw_model = HierarchicalModel(raw_list)
            raw_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()

            for idx_1, raw_cluster in enumerate(raw_model.clusters):
                for idx_2, transformed_cluster in enumerate(transformed_model.clusters):
                    print(raw_cluster.pattern_graph.simplify())
                    print(transformed_cluster.pattern_graph.simplify())


if __name__ == "__main__":
    evaluation = SimplicationEvaluation()
    print(evaluation.read_data())