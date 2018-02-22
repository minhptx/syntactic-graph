import codecs
import csv
import os
from collections import defaultdict

import numpy as np
import pandas as pd
import time

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
        accuracy_dict = {}
        time_dict = {}
        validation_dict = {}

        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")
        output_data_path = os.path.join("data/result")

        for file_name in sorted(os.listdir(raw_data_path))[:50]:
        # for file_name in ["1.csv"]:
            # if file_name in ["116.csv", "120.csv", "161.csv", "170.csv"]:
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
            raw_model = HierarchicalModel(raw_input_list)
            raw_model.build_hierarchy()

            print("Transformation")

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:
            #     continue

            cost_map = defaultdict(lambda: defaultdict(lambda: float("inf")))
            result_map = defaultdict(lambda: defaultdict(lambda: None))

            true_count = 0
            false_count = 0
            validation_count = 0

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

            value_list = defaultdict(lambda: None)

            for idx_1 in result_map:
                idx_2 = min(cost_map[idx_1].items(), key=lambda x: x[1])[0]
                result_list = result_map[idx_1][idx_2]
                # print("Size", raw_model.clusters[idx_1].pattern_graph.values)
                # print(result_list)
                # print(raw_model.clusters[idx_1].values)
                # print(true_count, false_count)
                # print(result_list, min(cost_map[idx_1].items(), key=lambda x: x[1]))

                transformed_cluster = transformed_model.clusters[idx_2]

                for idx, values in result_list.items():
                    value_str = "".join(values)

                    is_validated = transformed_cluster.pattern_graph.is_matched(value_str)

                    # print("Length", len(raw_model.clusters[idx_1].pattern_graph.values), len(result_list))
                    # print(raw_model.clusters[idx_1].pattern_graph.values)
                    raw_str = raw_model.clusters[idx_1].pattern_graph.values[idx]

                    raw_indices = [i for i, val in enumerate(raw_input_list) if val == raw_str[1:-1]]
                    # print(value_str)
                    # print(raw_str)
                    # print(groundtruth_list[raw_idx].strip())
                    # print(len(groundtruth_list), len(raw_input_list))

                    for raw_idx in raw_indices:
                        value_list[raw_idx] = value_str

                        try:
                            groundtruth = groundtruth_list[raw_idx]
                            if value_str.strip() == groundtruth.strip():
                                if is_validated:
                                    validation_count += 1
                                true_count += 1
                            else:
                                false_count += 1
                                if not is_validated:
                                    validation_count += 1
                                print("False", value_str, groundtruth)
                        except Exception as e:
                            print(e)
                            if not is_validated:
                                validation_count += 1
                            false_count += 1

            running_time = time.time() - start
            accuracy = true_count * 1.0 / (false_count + true_count)
            validate_accuracy = validation_count * 1.0 / (false_count + true_count)

            accuracy_dict[file_name] = accuracy
            time_dict[file_name] = running_time
            validation_dict[file_name] = validation_count
            print(accuracy)
            print(accuracy_dict)
            print(time_dict)
            print(validation_dict)
            print(np.mean(list(accuracy_dict.values())))
            print(np.mean(list(time_dict.values())))
            print(np.mean(list(validation_dict.values())))

            with open(output_file_path, "w") as writer:
                for i in range(len(raw_input_list)):
                    if i not in value_list:
                        writer.write("\n")
                    else:
                        writer.write(value_list[i] + "\n")

        with open("result.csv", "w") as f:
            writer = csv.writer(f)

            for name, acc in accuracy_dict.items():
                writer.writerow([name, acc, time_dict[name]])

        print(np.mean(list(accuracy_dict.values())))


if __name__ == "__main__":
    evaluation = TransformationEvaluation()
    print(evaluation.read_data())
