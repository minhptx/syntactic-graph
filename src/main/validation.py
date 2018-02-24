import codecs
import csv
import os
from collections import defaultdict

import numpy as np
import pandas as pd
import time

from syntactic.generation.model import HierarchicalModel
from syntactic.transformation.model import TransformationModel


class ValidationEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.raw_data_dict = defaultdict(lambda: [])
        self.transformed_data_dict = defaultdict(lambda: [])
        self.folder_path = "data/transformation"
        self.name_list = []

    @staticmethod
    def similarity(graph_1, graph_2):
        graph = graph_1.intersect(graph_2)

        if not graph:
            # print("No graph")
            return 0

        num_edge_1 = graph_1.num_edge()
        num_edge_2 = graph_2.num_edge()
        # print(graph.num_edge(), num_edge_1, num_edge_2)
        print("Sim", graph.num_edge() * 1.0 / min(num_edge_1, num_edge_2))
        return graph.num_edge() * 1.0 / min(num_edge_1, num_edge_2)

    def read_data(self):
        accuracy_dict = {}
        time_dict = {}
        validation_dict = {}
        predict_count = 0

        wrong_list = []


        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")
        output_data_path = os.path.join("data/result")

        for file_name in ["0.csv"]:
            # for file_name in ["1.csv"]:
            # if file_name in ["116.csv", "120.csv", "161.csv", "170.csv"]:
            #     continue
            #         continue
            print("File", file_name)
            #
            # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
            #     continue
            # raw_file_path = os.path.join(raw_data_path, file_name)
            transformed_file_path = os.path.join(transformed_data_path, file_name)
            groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)
            output_file_path = os.path.join(output_data_path, file_name)

            transformed_list = pd.read_csv(
                transformed_file_path, dtype=object, header=None).iloc[:, 0].fillna("").values.tolist()

            with codecs.open(groundtruth_file_path, "r", encoding="utf-8") as reader:
                groundtruth_list = reader.readlines()
                groundtruth_list = [x.strip() for x in groundtruth_list]

                if groundtruth_list[0] and groundtruth_list[0][0] == '"':
                    groundtruth_list = [x.strip()[1:-1] for x in groundtruth_list]
                else:
                    groundtruth_list = groundtruth_list

            with codecs.open(output_file_path, "r", encoding="utf-8") as reader:
                output_list = reader.readlines()
                output_list = [x.strip() for x in output_list]

                if output_list[0] and output_list[0][0] == '"':
                    output_list = [x.strip()[1:-1] for x in output_list]
                else:
                    output_list = output_list

            # try:
            output_model = HierarchicalModel(output_list)
            output_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:
            #     continue

            matched_list = []

            for idx, output_cluster in enumerate(output_model.clusters):
                for transformed_cluster in transformed_model.clusters:
                    if ValidationEvaluation.similarity(output_cluster.pattern_graph,
                                                       transformed_cluster.pattern_graph) == 1:
                        matched_list.append(idx)
                        break

            true_count = 0
            total_count = 0

            for idx, line in enumerate(output_list):
                # print(line.strip(), groundtruth_data[idx].strip())
                try:
                    if line.strip() == groundtruth_list[idx].strip():
                        true_count += 1
                    total_count += 1
                except:
                    total_count += 1
                    pass

            is_validated = False
            if len(set(matched_list)) == len(output_model.clusters):
                is_validated = True

            validation_dict[file_name] = is_validated
            accuracy_dict[file_name] = true_count * 1.0 / total_count


            if validation_dict[file_name] and accuracy_dict[file_name] == 1:
                predict_count += 1
            elif not validation_dict[file_name] and accuracy_dict[file_name] < 1:
                predict_count += 1
            else:
                wrong_list.append(file_name)

        print(predict_count * 1.0 / len(accuracy_dict))

        with open("validate.csv", "w") as f:
            writer = csv.writer(f)

            for name, acc in accuracy_dict.items():
                writer.writerow([name, acc, validation_dict[name]])

        print(validation_dict)
        print(wrong_list)


if __name__ == "__main__":
    evaluation = ValidationEvaluation()
    print(evaluation.read_data())
