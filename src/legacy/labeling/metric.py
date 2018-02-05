import re
import string
from collections import defaultdict

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_extraction import DictVectorizer


class MetricLearner:
    NUMWRD = r"[0-9]+"
    LWRD = r"[a-z]+"
    UWRD = r"[A-Z]+"
    PUNC = "[%s]" % (string.punctuation + "|")
    SPACE = "\s+"
    TOKEN_TYPES = {"NUM": NUMWRD, "LWD": LWRD, "UWD": UWRD, "PUN": PUNC, "SPACE": SPACE}

    def __init__(self, column_dict):
        self.vector_list = []
        self.label_list = []
        self.alpha = 0.1
        self.column_dict = column_dict
        self.vectorizer = None
        self.feature_matrix = None
        self.weight_vector = None

    def train(self):
        print("Training")
        for name, column in self.column_dict.items():
            for value in column.value_list:
                self.vector_list.append(self.extract_feature(value))
                self.label_list.append(name)

        self.vectorizer = DictVectorizer()
        self.vectorizer.fit(self.vector_list)
        print(self.vector_list)
        self.feature_matrix = self.vectorizer.transform(self.vector_list).todense()
        self.weight_vector = np.array([0.0] * self.feature_matrix.shape[1])
        self.gradient_descent()

    def convert_to_features(self, column):
        vector_list = []
        for value in column.value_list:
            vector_list.append(self.extract_feature(value))

        feature_vector = self.vectorizer.transform(vector_list).todense()
        return feature_vector

    def gradient_descent(self):
        old_weight_vector = np.array([-1] * self.feature_matrix.shape[1])
        while np.abs(np.sum(self.weight_vector - old_weight_vector)) > 0.01:
            print("Objective function", self.objective_function())
            print("Derivative:", self.derivative_function())
            self.weight_vector -= self.alpha * self.derivative_function()

    def objective_function(self):
        internal_distance_sum = 0
        internal_count = 0
        external_distance_sum = 0
        extenal_count = 0

        weuclid_distances = squareform(np.power(pdist(self.feature_matrix, "wminkowski", 2, self.weight_vector), 2))

        for i in range(len(self.label_list)):
            for j in range(i, len(self.label_list)):
                if i == j:
                    internal_distance_sum += weuclid_distances[i][j]
                    internal_count += 1
                else:
                    external_distance_sum += weuclid_distances[i][j]
                    extenal_count += 1

        return internal_distance_sum / internal_count - external_distance_sum / extenal_count

    def derivative_function(self):
        internal_distance_sum = 0
        internal_count = 0
        external_distance_sum = 0
        extenal_count = 0
        derivatives = []

        for j in range(self.feature_matrix.shape[1]):
            feature_column = self.feature_matrix[:, j]

            euclid_distances = squareform(np.power(pdist(feature_column, "minkowski", 2), 2))

            for i in range(len(self.label_list)):
                for j in range(i, len(self.label_list)):
                    if i == j:
                        internal_distance_sum += euclid_distances[i][j]
                        internal_count += 1
                    else:
                        external_distance_sum += euclid_distances[i][j]
                        extenal_count += 1

            # print(internal_distance_sum, internal_count, external_distance_sum, external_distance_sum)
            derivatives.append(internal_distance_sum / internal_count - external_distance_sum / extenal_count)

        return np.array(derivatives)

    def extract_feature(self, value):
        position_dict = defaultdict(lambda: [])
        count_dict = defaultdict(lambda: 0)
        for key, token_type in self.TOKEN_TYPES.items():
            matches = re.finditer(token_type, "".join(value))
            for match in matches:
                position_dict[match.group()].append(match.start())
                count_dict[match.group()] += 1
                position_dict[token_type].append(match.start())
                count_dict[match.group()] += 1

        feature_vector = {}
        for text in position_dict:
            feature_vector["POS " + text] = np.mean(position_dict[text])

        for text in count_dict:
            feature_vector["COUNT " + text] = count_dict[text]

        return feature_vector
