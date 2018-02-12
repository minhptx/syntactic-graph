import codecs
import os
from collections import defaultdict

import pandas as pd

from sequence.model import ClassificationModel
from syntactic.generation.model import HierarchicalModel
from syntactic.mapping.model import MappingModel


class MappingEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.raw_data_dict = defaultdict(lambda: [])
        self.transformed_data_dict = defaultdict(lambda: [])
        self.folder_path = "data/noisy"
        self.name_list = []

    def read_data(self):
        accuracy_list = []

        raw_data_path = os.path.join(self.folder_path, "input", 'raw')
        transformed_data_path = os.path.join(self.folder_path, "input", "transformed")
        groundtruth_data_path = os.path.join(self.folder_path, "groundtruth")

        # for file_name in sorted(os.listdir(raw_data_path))[0:100]:
        for file_name in ["1st_dimension.csv"]:
            print(file_name)
            #
            # if file_name in ["10.csv", "102.csv", "103.csv", "104.csv", "107.csv", "108.csv", "116.csv", "117.csv"]:
            #     continue
            raw_file_path = os.path.join(raw_data_path, file_name)
            transformed_file_path = os.path.join(transformed_data_path, file_name)
            groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)

            raw_list = pd.read_csv(raw_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()
            transformed_list = pd.read_csv(transformed_file_path, na_filter=False, dtype=str).iloc[:, 0].values.tolist()

            with codecs.open(groundtruth_file_path, encoding="utf-8") as reader:
                groundtruth_list = list(reader.readlines())
                if groundtruth_list[0][0] == '"':
                    groundtruth_list = [x.strip()[1:-1] for x in groundtruth_list]
            # try:
            raw_model = HierarchicalModel(raw_list)
            raw_model.build_hierarchy()

            transformed_model = HierarchicalModel(transformed_list)
            transformed_model.build_hierarchy()
            # except:

            for cluster in transformed_model.clusters:
                for node_1 in cluster.pattern_graph.edge_map:
                    for node_2 in cluster.pattern_graph.edge_map[node_1]:
                        for ev in cluster.pattern_graph.edge_map[node_1][node_2].value_list:
                            print(node_1, node_2, ev.atomic.name, ev.atomic.regex, ev.length, ev.nth, ev.values[:3])

            

            for cluster_1 in raw_model.clusters:
                for cluster_2 in transformed_model.clusters:
                    graph_1 = cluster_1.pattern_graph
                    graph_2 = cluster_2.pattern_graph

                    model = ClassificationModel(graph_2)
                    model.train()
                    model.predict(graph_1)

        return accuracy_list


if __name__ == "__main__":
    evaluation = MappingEvaluation()
    print(evaluation.read_data())
