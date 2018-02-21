import codecs
import re
import string
from collections import defaultdict

import matplotlib.pyplot as plt
import mpld3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer


class Validator:
    NUMWRD = r"[0-9]+"
    LWRD = r"[A-Za-z]+"
    # UWRD = r"[A-Z]+"
    PUNC = "[%s]+" % (string.punctuation + "|")
    SPACE = "\s+"
    TOKEN_TYPES = {"NUM": NUMWRD, "LWD": LWRD, "PUN": PUNC, "SPACE": SPACE}

    def __init__(self, file_path_1, file_path_2):
        self.vector_list = []
        with codecs.open(file_path_1, encoding="utf-8") as reader:
            value_list_1 = list(reader.readlines())
        with codecs.open(file_path_2, encoding="utf-8") as reader:
            value_list_2 = list(reader.readlines())
        self.value_list = value_list_1 + value_list_2
        self.value_list = [x.strip() for x in self.value_list]
        for idx, value in enumerate(self.value_list):
            if value.startswith('"') and value.endswith('"'):
                self.value_list[idx] = value[1:-1].strip()
        print(self.value_list)
        self.label_list = [0] * len(value_list_1) + [1] * len(value_list_2)
        self.vectorizer = None
        self.feature_matrix = None

    def classify(self):
        for value in self.value_list:
            self.vector_list.append(self.extract_feature(value))

        self.vectorizer = DictVectorizer()
        self.vectorizer.fit(self.vector_list)
        self.feature_matrix = self.vectorizer.transform(self.vector_list)
        classifier = RandomForestClassifier()
        # print("Fitting")
        classifier.fit(self.feature_matrix, self.label_list)
        # print("Predicting")
        accuracy = sum(classifier.predict(self.feature_matrix) == self.label_list) / len(self.label_list)
        return accuracy

    def pca_smallest(self):
        print("Training")
        for value in self.value_list:
            self.vector_list.append(self.extract_feature(value))

        self.vectorizer = DictVectorizer()
        self.vectorizer.fit(self.vector_list)
        self.feature_matrix = self.vectorizer.transform(self.vector_list)
        self.feature_matrix = PCA(n_components=2).fit_transform(self.feature_matrix.toarray())

        print(self.feature_matrix)

        print(self.value_list[-1])

        print(np.unique(self.feature_matrix, return_inverse=True))

        fig = plt.figure(figsize=(6, 4))
        scatter = plt.scatter([self.feature_matrix[:, 0]], [self.feature_matrix[:, 1]])
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.legend(loc='lower center')
        plt.tight_layout()

        tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=self.value_list)
        mpld3.plugins.connect(fig, tooltip)
        mpld3.show()

    def convert_to_features(self, column):
        vector_list = []
        for value in column.value_list:
            vector_list.append(self.extract_feature(value))

        feature_vector = self.vectorizer.transform(vector_list).todense()
        return feature_vector

    def extract_feature(self, value):
        temp = value
        position_dict = defaultdict(lambda: [])
        length_dict = defaultdict(lambda: [])
        index = 0
        while value:
            for key, token_type in self.TOKEN_TYPES.items():
                match = re.match("^" + token_type, "".join(value))
                if match:
                    position_dict["%s %s" % (token_type, index)] = 1
                    index += 1
                    length_dict[token_type].append(match.end() - match.start())
                    value = value[match.end():]
                    break
            else:
                break

        feature_vector = {}
        for text in position_dict:
            feature_vector["POS " + text] = position_dict[text]

        for text in length_dict:
            feature_vector["LENGTH " + text] = np.mean(length_dict[text])

        # print(temp, feature_vector)

        return feature_vector
