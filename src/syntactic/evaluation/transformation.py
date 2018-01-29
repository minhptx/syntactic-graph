import os
from collections import defaultdict

import pandas as pd

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
        for data_set in os.listdir(self.folder_path):
            raw_data_path = os.path.join(self.folder_path, data_set, "input", 'raw')
            transformed_data_path = os.path.join(self.folder_path, data_set, "input", "transformed")
            groundtruth_data_path = os.path.join(self.folder_path, data_set, "groundtruth")

            for file_name in os.listdir(raw_data_path):
                raw_file_path = os.path.join(raw_data_path, file_name)
                transformed_file_path = os.path.join(transformed_data_path, file_name)
                groundtruth_file_path = os.path.join(groundtruth_data_path, file_name)

                raw_list = pd.read_csv(raw_file_path).iloc[:, 0].values.tolist()
                transformed_list = pd.read_csv(transformed_file_path).iloc[:, 0].values.tolist()
                groundtruth_list = pd.read_csv(groundtruth_file_path).iloc[:, 0].values.tolist()

                raw_model = HierarchicalModel(raw_list)
                raw_model.build_hierarchy()

                transformed_model = HierarchicalModel(transformed_list)
                transformed_model.build_hierarchy(1)

                transformed_graph = transformed_model.clusters[0].pattern_graph

                for raw_cluster in raw_model.clusters:
                    transformation_model = TransformationModel(raw_cluster.pattern_graph, transformed_graph)

                    pass

