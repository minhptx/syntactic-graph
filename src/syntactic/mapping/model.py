from collections import defaultdict


class MappingModel:
    def __init__(self, raw_list, transformed_list):
        self.raw_list = raw_list
        self.transformed_list = transformed_list
        self.translation_table = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
        self.alignment_table = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))

    def train(self):
        for idx_1, raw_sentence in enumerate(self.raw_list):
            for idx_2, transformed_sentence in enumerate(self.transformed_list):
                raw_sentence = [None] + raw_sentence
                transformed_sentence = ["UNUSED"] + transformed_sentence

                for i in range(len(raw_sentence)):
                    for j in range(len(transformed_sentence)):
                        self.translation_table[idx_1][idx_2][i][j] = 0

    def init_probabilities(self):
        pass

    def expected_count(self):
        pass

    def expectation_maximization(self):
        self.expected_count()
        pass


