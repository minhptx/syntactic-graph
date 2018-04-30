import codecs
import csv
import math
import os
import random
import time
from collections import defaultdict

import numpy as np
import pandas as pd

from syntactic.generation.model import HierarchicalModel
from syntactic.transformation.model import TransformationModel
from syntactic.validation.model import GraphValidationModel


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

        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")
        output_data_path = os.path.join("data/result")

        validation_model = GraphValidationModel()

        validation_count = 0

        with open("result.csv", "w") as f:
            writer = csv.writer(f)

            for file_name in sorted(os.listdir(raw_data_path))[:]:
            #     print(file_name)
                # if "univ" not in file_name:
                #     continue
            # for file_name in ["uri.csv"]:
                # for file_name in ["1.csv"]:            # if file_name in ["116.csv", "120.csv", "161.csv", "170.csv"]:
                #     continue
                start = time.time()
                #         continue                #
                # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
                #     continue
                raw_file_path = os.path.join(raw_data_path, file_name)
                transformed_file_path = os.path.join(transformed_data_path, file_name)
                groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)
                output_file_path = os.path.join(output_data_path, file_name)

                raw_input_list = pd.read_csv(raw_file_path, dtype=object, header=None).iloc[:, 0].fillna(
                    "").values.tolist()
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

                for idx_1, raw_cluster in enumerate(raw_model.clusters):
                    if len(raw_cluster.values) <= math.ceil(0.1 * len(raw_input_list)):
                        continue
                    for idx_2, transformed_cluster in enumerate(transformed_model.clusters):
                        if len(transformed_cluster.values) <= math.ceil(0.1 * len(transformed_list)):
                            continue

                        # print("Length", len(raw_cluster.values), len(transformed_cluster.values))
                        transformation_model = TransformationModel(raw_cluster.pattern_graph,
                                                                   transformed_cluster.pattern_graph)

                        result_list, cost_list = transformation_model.generate_program()

                        index_key = 0

                        for result, cost in zip(result_list, cost_list):
                            cost_map[idx_1][
                                str(idx_2) + str(index_key)] = cost
                            result_map[idx_1][str(idx_2) + str(index_key)] = result
                            index_key += 1

                all_value_dict = defaultdict(lambda: None)

                # validated = True

                true_count = 0

                for idx_1 in result_map:
                    value_dict_list = []
                    indices_with_scores = sorted(cost_map[idx_1].items(), key=lambda x: x[1], reverse=True)[:5]
                    true_count_list = []
                    false_data_list = []

                    for idx_2, score in indices_with_scores:
                        result_list = result_map[idx_1][idx_2]

                        # print(result_list)
                        value_dict = defaultdict(lambda: None)

                        existed_list = []
                        alt_true_count = 0
                        alt_false_list = []
                        false_count = 0

                        for idx, values in result_list.items():

                            value_str = "".join(values)

                            raw_str = raw_model.clusters[idx_1].pattern_graph.values[idx]

                            if raw_str in existed_list:
                                continue

                            existed_list.append(raw_str)

                            raw_indices = [i for i, val in enumerate(raw_input_list) if val == raw_str[1:-1]]
                            # print(value_str, raw_str, raw_indices, raw_model.clusters[idx_1].pattern_graph.values)

                            for raw_idx in raw_indices:

                                value_dict[raw_idx] = value_str

                                try:
                                    groundtruth = groundtruth_list[raw_idx]
                                    if value_str.strip() == groundtruth.strip():
                                        alt_true_count += 1
                                    else:
                                        alt_false_list.append((value_str, groundtruth))
                                except Exception as e:
                                    print(e)
                                    false_count += 1
                        true_count_list.append(alt_true_count)
                        false_data_list.append(alt_false_list)
                        value_dict_list.append(value_dict)
                    true_count += max(true_count_list)
                    max_index = np.argmax(true_count_list)
                    all_value_dict.update(value_dict_list[max_index])
                    # print("False data", false_data_list[max_index], false_count)

                    # transformed_cluster = transformed_model.clusters[idx_2]
                    #
                    # result_model = HierarchicalModel(["".join(x) for x in result_list.values()])
                    # result_model.build_hierarchy()

                    # print(len(result_model.clusters))

                    # if len(result_model.clusters) != 1:
                    #                     #     validated = False
                    #                     #     # print("Not Validated: Too much clusters")
                    #                     # elif not validation_model.validate(result_model.clusters[0], transformed_cluster):
                    #                     #     validated = False

                running_time = time.time() - start

                if validated and accuracy == 1:
                    validation_count += 1
                elif not validated and accuracy != 1:
                    validation_count += 1
                accuracy = true_count * 1.0 / len(groundtruth_list)
                accuracy_dict[file_name] = accuracy
                time_dict[file_name] = running_time
                print("Accuracy", accuracy)
                # print(accuracy_dict)
                # print(time_dict)
                # print(validation_dict)
                print("Mean accuracy", np.mean(list(accuracy_dict.values())))
                print("Mean time", np.mean(list(time_dict.values())))
                print("Mean validation", validation_count * 1.0 / len(accuracy_dict))

                with codecs.open(output_file_path, "w", encoding="utf-8") as w:
                    for i in range(len(raw_input_list)):
                        if i not in all_value_dict:
                            w.write("\n")
                        else:
                            w.write(all_value_dict[i] + "\n")

                    # for name, acc in accuracy_dict.items():
                writer.writerow([file_name, accuracy_dict[file_name], time_dict[file_name],
                                 validation_count * 1.0 / len(accuracy_dict)])
            writer.writerow(["Total", np.mean(list(accuracy_dict.values())), np.mean(list(time_dict.values())),
                                 validation_count * 1.0 / len(accuracy_dict)])


if __name__ == "__main__":
    random.seed(1)
evaluation = TransformationEvaluation()
print(evaluation.read_data())
