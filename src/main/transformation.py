import codecs
import csv
import os
import random
import time
from collections import defaultdict

import numpy as np
import pandas as pd

from syntactic.generation.model import HierarchicalModel
from syntactic.transformation.model import TransformationModel
from syntactic.validation.model import ValidationModel


class TransformationEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.raw_data_dict = defaultdict(lambda: [])
        self.transformed_data_dict = defaultdict(lambda: [])
        self.folder_path = "data/sygus"
        self.name_list = []

    def read_data(self):
        accuracy_dict = {}
        time_dict = {}
        validation_dict = {}

        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")
        output_data_path = os.path.join("data/result")

        validation_model = ValidationModel()

        validation_count = 0

        for file_name in sorted(os.listdir(raw_data_path))[:1]:
        # for file_name in ["107.csv"]:
            # for file_name in ["1.csv"]:            # if file_name in ["116.csv", "120.csv", "161.csv", "170.csv"]:
            #     continue
            start = time.time()
            #         continue
            print("File", file_name)
            #
            # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
            #     continue
            raw_file_path = os.path.join(raw_data_path, file_name)
            transformed_file_path = os.path.join(transformed_data_path, file_name)
            groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)
            output_file_path = os.path.join(output_data_path, file_name)

            raw_input_list = pd.read_csv(raw_file_path, dtype=object, header=None).iloc[:, 0].fillna("").values.tolist()
            transformed_list = pd.read_csv(
                transformed_file_path, dtype=object, header=None).iloc[:, 0].fillna("").values.tolist()

            with codecs.open(groundtruth_file_path, "r", encoding="utf-8") as reader:
                groundtruth_list = reader.readlines()
                groundtruth_list = [x.strip() for x in groundtruth_list]

                if groundtruth_list[0] and groundtruth_list[0][0] == '"':
                    groundtruth_list = [x.strip()[1:-1] for x in groundtruth_list]
                else:
                    groundtruth_list = groundtruth_list

            # try:

            raw_input_list = raw_input_list[:1000]
            transformed_list = transformed_list[:1000]
            groundtruth_list = groundtruth_list[:1000]

            raw_model = HierarchicalModel(raw_input_list)
            raw_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:
            #     continue

            cost_map = defaultdict(lambda: defaultdict(lambda: float("-inf")))
            result_map = defaultdict(lambda: defaultdict(lambda: None))

            true_count = 0
            false_count = 0

            for idx_1, raw_cluster in enumerate(raw_model.clusters):
                for idx_2, transformed_cluster in enumerate(transformed_model.clusters):
                    # print("Length", len(raw_cluster.values), len(transformed_cluster.values))
                    transformation_model = TransformationModel(raw_cluster.pattern_graph,
                                                               transformed_cluster.pattern_graph)

                    result_list, cost = transformation_model.generate_program()

                    cost_map[idx_1][
                        idx_2] = cost
                    result_map[idx_1][idx_2] = result_list

            value_list = defaultdict(lambda: None)

            validated = True

            for idx_1 in result_map:
                idx_2 = max(cost_map[idx_1].items(), key=lambda x: x[1])[0]
                result_list = result_map[idx_1][idx_2]

                existed_list = []
                for idx, values in result_list.items():
                    value_str = "".join(values)

                    if value_str in existed_list:
                        continue

                    existed_list.append(value_str)

                    raw_str = raw_model.clusters[idx_1].pattern_graph.values[idx]


                    raw_indices = [i for i, val in enumerate(raw_input_list) if val == raw_str[1:-1]]
                    for raw_idx in raw_indices:

                        value_list[raw_idx] = value_str

                        try:
                            groundtruth = groundtruth_list[raw_idx]
                            if value_str.strip() == groundtruth.strip():
                                true_count += 1
                            else:
                                false_count += 1
                                print("False", value_str, groundtruth)
                        except Exception as e:
                            print(e)
                            false_count += 1

                transformed_cluster = transformed_model.clusters[idx_2]

                result_model = HierarchicalModel(["".join(x) for x in result_list.values()])
                result_model.build_hierarchy()

                print(len(result_model.clusters))

                if len(result_model.clusters) != 1:
                    validated = False
                    # print("Not Validated: Too much clusters")
                elif not validation_model.validate(result_model.clusters[0], transformed_cluster):
                    validated = False

            running_time = time.time() - start
            accuracy = true_count * 1.0 / len(groundtruth_list)

            if validated and accuracy == 1:
                validation_count += 1
            elif not validated and accuracy != 1:
                validation_count += 1

            accuracy_dict[file_name] = accuracy
            time_dict[file_name] = running_time
            print("Accuracy", accuracy)
            # print(accuracy_dict)
            # print(time_dict)
            # print(validation_dict)
            print("Mean accuracy", np.mean(list(accuracy_dict.values())))
            print("Mean time", np.mean(list(time_dict.values())))
            print("Mean validation", validation_count * 1.0 / len(accuracy_dict))

            with codecs.open(output_file_path, "w", encoding="utf-8") as writer:
                for i in range(len(raw_input_list)):
                    if i not in value_list:
                        writer.write("\n")
                    else:
                        writer.write(value_list[i] + "\n")

        with open("result.csv", "w") as f:
            writer = csv.writer(f)

            for name, acc in accuracy_dict.items():
                writer.writerow([name, acc, time_dict[name]])

if __name__ == "__main__":
    random.seed(1)
    evaluation = TransformationEvaluation()
    print(evaluation.read_data())
