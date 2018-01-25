import json
import os
import random
import numpy as np
from collections import defaultdict
from sklearn.metrics import roc_auc_score

from syntactic.generation.model import HierarchicalModel


class DistanceEvaluation:
    def __init__(self):
        self.data_dict = defaultdict(lambda: [])
        self.name_list = []
        self.folder_path = "data/syntactic"

    def read_data(self):
        for file_name in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file_name)

            self.name_list.append(file_name)

            with open(file_path, "r") as reader:
                json_object = json.load(reader)

                self.data_dict[file_name] = json_object["Data"]

    def create_test_data(self):
        data_set = []

        for i in range(100000):
            test_1 = random.choice(self.name_list)
            test_2 = random.choice(self.name_list)

            point_1 = random.choice(self.data_dict[test_1])
            point_2 = random.choice(self.data_dict[test_2])

            result = 0
            if test_1 == test_2:
                result = 1

            data_set.append((point_1, point_2, result))

        return data_set

    def evaluate(self):
        data_set = self.create_test_data()

        model = HierarchicalModel(None)

        result_set = []
        distance_set = []
        roc_set = []

        for point_1, point_2, result in data_set:
            print(point_1, point_2)
            distance = model.similarity(point_1, point_2, is_cached=False)
            if distance == -HierarchicalModel.MAX_DISTANCE:
                distance = 0
            result_set.append(result)
            distance_set.append(distance)

            print(len(distance_set))

            if len(result_set) == 10000:
                roc_set.append(roc_auc_score(result_set, distance_set))
                result_set = []
                distance_set = []

        return np.mean(roc_set)


if __name__ == "__main__":
    evaluator = DistanceEvaluation()
    evaluator.read_data()
    print(evaluator.evaluate())
