import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
import regex as re
from collections import defaultdict


class GraphValidationModel:
    def __init__(self):
        pass

    def validate(self, result_cluster, transformed_cluster):
        if result_cluster.pattern_graph.similar(transformed_cluster.pattern_graph):
            print("Validated")
            return True
        print("Not Validated")
        return False


class RFValidationModel:
    NUMWRD = r"[0-9]+"
    LWRD = r"[A-Za-z]+"
    # UWRD = r"[A-Z]+"
    PUNC = r"\p{P}+"
    SPACE = "\s+"
    TOKEN_TYPES = {"NUM": NUMWRD, "LWD": LWRD, "PUN": PUNC, "SPACE": SPACE}

    def __init__(self):
        pass

    def validate(self, raw_list, transformed_list):
        self.vector_list = []

        self.value_list = raw_list + transformed_list
        self.value_list = [x.strip() for x in self.value_list]
        for idx, value in enumerate(self.value_list):
            if value.startswith('"') and value.endswith('"'):
                self.value_list[idx] = value[1:-1].strip()
        self.label_list = [0] * len(raw_list) + [1] * len(transformed_list)
        self.vectorizer = None
        self.feature_matrix = None
        return self.classify()

    def classify(self):
        for value in self.value_list:
            self.vector_list.append(self.extract_feature(value))

        self.vectorizer = DictVectorizer()
        self.vectorizer.fit(self.vector_list)
        self.feature_matrix = self.vectorizer.transform(self.vector_list)
        classifier = RandomForestClassifier()
        # print("Fitting")
        classifier.fit(self.feature_matrix, self.label_list)
        accuracy = sum(classifier.predict(self.feature_matrix) == self.label_list) / len(self.label_list)
        return accuracy

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
