from collections import defaultdict
import os
import json


class TransformationEvaluation:
    def __init__(self):
        self.data_set = defaultdict(lambda: [])
        self.data_dict = defaultdict(lambda: [])
        self.folder_path = "data/transformation"
        self.name_list = []

    def read_data(self):
        for data_set in os.listdir(self.folder_path):
            input_data_path = os.path.join(self.folder_path, data_set, "input")
            groundtruth_data_path = os.path.join(self.folder_path, data_set, "groundtruth")


            self.name_list.append(file_name)

            with open(file_path, "r") as reader:
                json_object = json.load(reader)

                self.data_dict[file_name] = json_object["Data"]