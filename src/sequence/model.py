from collections import defaultdict

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer

from sequence.feature import token_to_features


class ClassificationModel:
    def __init__(self, graph):
        self.pattern_graph = graph
        self.feature_node_dict = defaultdict(lambda: [])
        self.vectorizer = None
        self.classifier = None

    def generate_features(self):
        for node_1 in self.pattern_graph.edge_map:
            for node_2 in self.pattern_graph.edge_map[node_1]:
                print(node_1, node_2)
                self.feature_node_dict[(node_1, node_2)].append(token_to_features(
                    self.pattern_graph.edge_map[node_1][node_2], None, None))

    def train(self):
        train_data = []
        train_labels = []

        for label, feature_vectors in self.feature_node_dict.items():
            for feature_vector in feature_vectors:
                train_data.append(feature_vector)
                train_labels.append("|".join(label))

        self.vectorizer = DictVectorizer()
        print(train_data)
        train_vectors = self.vectorizer.fit_transform(train_data)

        self.classifier = RandomForestClassifier()
        self.classifier.fit(train_vectors, train_labels)

        return self.vectorizer, self.classifier

    def predict(self, graph):
        test_data = []

        for node_1 in graph.edge_map:
            for node_2 in graph.edge_map[node_1]:
                test_data.append(token_to_features(graph.edge_map[node_1][node_2], None, None))

        test_vectors = self.vectorizer.transform()

        print(self.classifier.predict(test_vectors))
