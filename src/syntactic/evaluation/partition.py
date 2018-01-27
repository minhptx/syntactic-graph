from collections import defaultdict
import random
import os
import json
import numpy as np

from sklearn.metrics import normalized_mutual_info_score

from syntactic.generation.model import HierarchicalModel


class PartitionEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.data_dict = defaultdict(lambda: [])
        self.folder_path = "data/syntactic"
        self.name_list = []

    def read_data(self):
        for file_name in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file_name)

            self.name_list.append(file_name)

            with open(file_path, "r") as reader:
                json_object = json.load(reader)

                self.data_dict[file_name] = json_object["Data"]

    def evaluate(self):
        nmi_list = []

        for size in range(2, 9):
            for j in range(0, 10):
                subset = random.sample(self.name_list, size)
                data_list = []
                label_list = []
                label = 0


                for name in subset:
                    print("Size", size)
                    data_size = 256
                    if len(self.data_dict[name]) <= 256:
                        data_size = len(self.data_dict[name])
                    data_list.extend(random.sample(self.data_dict[name], data_size))
                    label_list.extend([label] * data_size)
                    label += 1

                model = HierarchicalModel(data_list)
                model.build_hierarchy()
                cluster_ids = model.get_cluster_labels()

                nmi_list.append(normalized_mutual_info_score(label_list, cluster_ids))
        return np.mean(nmi_list)


if __name__ == "__main__":
    evaluator = PartitionEvaluation()
    evaluator.read_data()
    print(evaluator.evaluate())
