import json
import os
import random

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

        for i in range(240400):
            test_1 = random.choice(self.name_list)
            test_2 = random.choice(self.name_list)

            point_1 = random.choice(self.data_dict[test_1])
            point_2 = random.choice(self.data_dict[test_2])

            result = 1
            if test_1 == test_2:
                result = 0

            data_set.append((point_1, point_2, result))

        return data_set

    def evaluate(self):
        data_set = self.create_test_data()

        model = HierarchicalModel(None)

        result_set = []
        distance_set = []

        for point_1, point_2, result in data_set:
            print(point_1, point_2)
            distance = model.dissimilarity(point_1, point_2)
            if distance == HierarchicalModel.MAX_DISTANCE:
                distance = 1
            result_set.append(result)
            distance_set.append(distance)

            print(result, distance)
        print(len(result_set))

        return roc_auc_score(result_set, distance_set, average="micro")


if __name__ == "__main__":
    evaluator = DistanceEvaluation()
    evaluator.read_data()
    print(evaluator.evaluate())
