from collections import defaultdict


class Sequence:
    def __init__(self, path):
        self.sequence = path

    def word_to_feature(self):
        feature_word_dict = defaultdict(lambda: [])
        for ev in self.sequence:
            for feature in feature_list

