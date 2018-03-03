import random
from collections import defaultdict

from sklearn.linear_model import LogisticRegression


class MappingModel:
    def __init__(self, ):
        self.model = LogisticRegression()

    def train(self, train_data, train_labels):
        self.model.fit(train_data, train_labels)

    def train_from_graph(self, input_graphs):
        train_data = []
        train_labels = []
        for input_graph in input_graphs:
            sub_train_data, sub_train_labels = self.generate_data(input_graph)
            train_data.extend(sub_train_data)
            train_labels.extend(sub_train_labels)




    def generate_data(self, graph):
        train_data = []
        train_labels = []
        edge_data_dict = defaultdict(lambda: [])

        for start_node in graph.edge_map:
            for end_node in graph.edge_map[start_node]:
                edge = graph.edge_map[start_node][end_node]

                edge_data_dict[(start_node, end_node)].extend(edge.values)

        for name_1 in edge_data_dict:
            for name_2 in edge_data_dict:
                sample_1 = random.sample(edge_data_dict[name_1], 100)
                sample_2 = random.sample(edge_data_dict[name_2], 100)

                feature_vector = self.create_feature_vector(sample_1, sample_2)
                train_data.append(feature_vector)
                if name_1 == name_2:
                    train_labels.append(1)
                else:
                    train_labels.append(0)

        return train_data, train_labels

    def create_feature_vector(self, list_1, list_2):
        pass
