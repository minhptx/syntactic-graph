from collections import defaultdict

from syntactic.generation.atomic import *
from utils.string import jaccard_similarity, jaccard_subset_similarity, soft_tfidf_similarity


class Operation(object):
    def __init__(self, raw_ev, transformed_ev, *args, **kwargs):
        self.raw_ev = raw_ev
        self.transformed_ev = transformed_ev
        self.score = 0

    def score_function(self):
        return 0

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        pass

    def transform(self):
        pass


class Constant(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Constant, self).__init__(raw_ev, transformed_ev)
        self.constant = transformed_ev.atomic.regex

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if isinstance(transformed_ev.atomic, ConstantString) and raw_ev.atomic not in [START_TOKEN, END_TOKEN]:
            return True
        else:
            return False

    def score_function(self):
        return 1

    def transform(self):
        return [self.transformed_ev.values[0] for x in self.raw_ev.values]


class PartOf(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(PartOf, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.atomic in [START_TOKEN, END_TOKEN] or transformed_ev.atomic in [START_TOKEN, END_TOKEN]:
            return False
        if raw_ev.atomic != transformed_ev.atomic:
            return False
        if raw_ev.length <= transformed_ev.length:
            return True

    def score_function(self):
        return soft_tfidf_similarity(self.raw_ev.values, self.transformed_ev.values)

    def transform(self):
        return self.raw_ev.values


class Upper(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Upper, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic == UPPER_CASE and raw_ev.atomic in [LOWER_CASE, ALPHABET, PROPER_CASE]:
            if transformed_ev.length == raw_ev.length:
                return True
        return False

    def score_function(self):
        value_list = [x.upper() for x in self.raw_ev.values]
        return soft_tfidf_similarity(value_list, self.transformed_ev.values)

    def transform(self):
        return [x.toupper() for x in self.raw_ev.values]


class Lower(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Lower, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic == LOWER_CASE and raw_ev.atomic in [UPPER_CASE, ALPHABET, PROPER_CASE]:
            if transformed_ev.length == raw_ev.length:
                return True
        return False

    def score_function(self):
        value_list = [x.lower() for x in self.raw_ev.values]
        return soft_tfidf_similarity(value_list, self.transformed_ev.values)

    def transform(self):
        return [x.lower() for x in self.raw_ev.values]


class SubStr(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(SubStr, self).__init__(raw_ev, transformed_ev)
        self.score = 0
        self.index = -1
        self.length = transformed_ev.length
        self.get_best_range()

    def get_best_range(self):
        length = self.transformed_ev.length
        # print("Value list", self.raw_ev.values)
        # print("Value list", self.transformed_ev.values)

        min_length = min([len(x) for x in self.raw_ev.values])

        score_dict = defaultdict(lambda: 0)

        for i in range(0, min_length - length):
            value_list = []
            for value in self.raw_ev.values:
                value_list.append(value[i: i + length])
            score_dict[i] = self.score_range(value_list)

            value_list = []
            for value in self.raw_ev.values:
                value_list.append(value[i: i + length])
            score_dict[-i] = self.score_range(value_list)

        # print(score_dict, min_length, length)
        if score_dict:
            self.score = max(score_dict.values())
        else:
            self.score = 0
        if self.score:
            self.index = list(score_dict.keys())[list(score_dict.values()).index(self.score)]

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.atomic in [START_TOKEN, END_TOKEN] or transformed_ev.atomic in [START_TOKEN, END_TOKEN]:
            return False
        if raw_ev.atomic != transformed_ev.atomic or transformed_ev.length == -1:
            return False
        if raw_ev.length >= transformed_ev.length or raw_ev.length == -1:
            return True

    def score_function(self):
        if self.score == -1:
            self.get_best_range()
        return self.score

    def score_range(self, value_list):
        return jaccard_similarity(value_list, self.raw_ev.values)

    def transform(self):
        return [x[self.index:self.index + self.length] for x in self.raw_ev.values]

class Replace(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Replace, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev == raw_ev:
            return True
        return False

    def score_function(self):
        if self.raw_ev.atomic in [START_TOKEN, END_TOKEN]:
            return 1
        return jaccard_similarity(self.raw_ev.values, self.transformed_ev.values)

    def transform(self):
        return self.raw_ev.values