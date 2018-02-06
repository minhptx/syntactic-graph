import os
from collections import defaultdict

import pandas as pd

from syntactic.generation.model import HierarchicalModel
from syntactic.mapping.model import MappingModel


class MappingEvaluation:
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

        # for file_name in sorted(os.listdir(raw_data_path))[0:100]:
        for file_name in ["name3.csv"]:
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

            # try:
            raw_model = HierarchicalModel(raw_list)
            raw_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:

            mapping_model = MappingModel(raw_model, transformed_model)

            raw_final_list, transformed_final_list = mapping_model.map()

            true_count = 0
            count = 0

            print(raw_final_list)
            for new_idx, value in enumerate(raw_final_list):
                old_idx = raw_list.index(value)
                print(value, raw_list[old_idx], transformed_final_list[new_idx], groundtruth_list[old_idx], )
                if groundtruth_list[old_idx] == transformed_final_list[new_idx]:
                    true_count += 1
                count += 1

            if count:
                accuracy_list.append(true_count * 1.0 / count)
                print(true_count * 1.0 / count)
        return accuracy_list

if __name__ == "__main__":
    evaluation = MappingEvaluation()
    print(evaluation.read_data())