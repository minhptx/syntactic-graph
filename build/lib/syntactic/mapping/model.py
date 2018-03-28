import numpy as np
from collections import defaultdict

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from syntactic.mapping.feature import *


class MappingModel:

    def __init__(self):
        self.model = LogisticRegression()
        self.feature_functions = [w2v_cosine, ks, tfidf_cosine, jaccard]

    def train(self, train_data, train_labels):
        self.model.fit(train_data, train_labels)
        # print("result", self.model.score(train_data, train_labels))
        print("Coef", self.model.coef_)

    def train_from_graph(self, input_graphs):
        train_data = []
        train_labels = []
        for input_graph in input_graphs:
            sub_train_data, sub_train_labels = self.generate_data(input_graph)
            train_data.extend(sub_train_data)
            train_labels.extend(sub_train_labels)

        self.train(train_data, train_labels)

    def get_sim(self, list_1, list_2):
        feature_vector = self.create_feature_vector(list_1, list_2)
        return self.predict_proba([feature_vector])[0][1]

    def predict(self, test_data):
        return self.model.predict(test_data)

    def predict_proba(self, test_data):
        return self.model.predict_proba(test_data)

    def generate_data(self, graph):
        train_data = []
        train_labels = []
        edge_data_dict = defaultdict(lambda: [])

        for start_node in graph.edge_map:
            for end_node in graph.edge_map[start_node]:
                edge = graph.edge_map[start_node][end_node]

                edge_data_dict[(start_node, end_node)].extend(edge.values[0].values)

        edge_data_dict["Blank Column"] = ['' for x in range(1000)]

        for name_1 in edge_data_dict:
            for name_2 in edge_data_dict:
                if name_1 == name_2:
                    for i in range(5):
                        sample_1 = np.random.choice(edge_data_dict[name_1], len(edge_data_dict[name_1]) // 5).tolist()
                        sample_2 = np.random.choice(edge_data_dict[name_2], len(edge_data_dict[name_1]) // 5).tolist()

                        feature_vector = self.create_feature_vector(sample_1, sample_2)
                        train_data.append(feature_vector)

                        train_labels.append(1)
                else:
                    sample_1 = np.random.choice(edge_data_dict[name_1], len(edge_data_dict[name_1]) // 2).tolist()
                    sample_2 = np.random.choice(edge_data_dict[name_2], len(edge_data_dict[name_1]) // 2).tolist()
                    feature_vector = self.create_feature_vector(sample_1, sample_2)
                    train_data.append(feature_vector)
                    train_labels.append(0)

        return train_data, train_labels

    def create_feature_vector(self, list_1, list_2):
        feature_vector = []
        for feature_function in self.feature_functions:
            feature_vector.append(feature_function(list_1, list_2))
        return feature_vector
