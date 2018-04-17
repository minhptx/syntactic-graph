from collections import defaultdict

from syntactic.generation.atomic import *


class Operation(object):
    def __init__(self, raw_ev, transformed_ev, *args, **kwargs):
        self.raw_ev = raw_ev
        self.transformed_ev = transformed_ev
        self.score = 0

    def score_function(self, model):
        transformed_data = self.transform()
        return model.get_sim(transformed_data, self.transformed_ev.values)

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
        if len(transformed_ev.values) == 1:
            return False
        if isinstance(transformed_ev.atomic, ConstantString):
            return True
        elif transformed_ev.atomic in [START_TOKEN, END_TOKEN]:
            return True
        else:
            return False

    def score_function(self, model):
        return 1

    def transform(self):
        try:
            return [self.transformed_ev.values[0] for x in self.raw_ev.values]
        except:
            return self.transformed_ev.values


class Replace(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Replace, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.atomic in [START_TOKEN, END_TOKEN] or transformed_ev.atomic in [START_TOKEN, END_TOKEN]:
            return False
        if raw_ev.atomic == transformed_ev.atomic:
            if raw_ev.is_length_fit(transformed_ev):
                return True
        return False

    def transform(self):
        return self.raw_ev.values[:]


class Upper(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Upper, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic in [UPPER_CASE, UPPER_CASE_WS] and raw_ev.atomic in [LOWER_CASE, ALPHABET, PROPER_CASE,
                                                                                      LOWER_CASE_WS, ALPHABET_WS,
                                                                                      PROPER_CASE_WS]:
            if transformed_ev.is_length_fit(raw_ev):
                return True
        return False

    def transform(self):
        return [x.upper() for x in self.raw_ev.values]


class Lower(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Lower, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic in [LOWER_CASE, LOWER_CASE_WS] and raw_ev.atomic in [UPPER_CASE, ALPHABET, PROPER_CASE,
                                                                                      UPPER_CASE_WS, ALPHABET_WS,
                                                                                      PROPER_CASE_WS]:
            if raw_ev.is_length_fit(transformed_ev):
                return True
        return False

    def transform(self):
        return [x.lower() for x in self.raw_ev.values]


class SubStr(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(SubStr, self).__init__(raw_ev, transformed_ev)
        self.score = -1
        self.start_index = -1
        self.end_index = -1
        self.min_length = raw_ev.min_length

    def get_best_range(self, model):
        length = self.transformed_ev.min_length
        # print("Value list", self.raw_ev.values)
        # print("Value list", self.transformed_ev.values)

        score_dict = defaultdict(lambda: 0)

        # print("Lenght", self.min_length, length)

        for i in range(self.min_length - length + 1):
            value_list = []
            for value in self.raw_ev.values:
                value_list.append(value[i: i + length])
            # print("Index list", i, value_list)
            score_dict[i] = self.score_range(value_list, model)

            value_list = []
            for value in self.raw_ev.values:
                value_list.append(value[-i - length: -i])
            score_dict[-i] = self.score_range(value_list, model)

        # print("Score dict", score_dict)
        if score_dict:
            self.score = max(score_dict.values())
        else:
            self.score = 0
        if self.score:
            self.start_index = list(score_dict.keys())[list(score_dict.values()).index(self.score)]
            self.end_index = self.start_index + length

    def __str__(self):
        return "SubString(%s, %s)" % (self.start_index, self.end_index)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        # print(raw_ev.min_length, raw_ev.max_length, transformed_ev.min_length, transformed_ev.max_length)
        if transformed_ev.min_length != transformed_ev.max_length - 1:
            return False
        if raw_ev.atomic in [START_TOKEN, END_TOKEN] or transformed_ev.atomic in [START_TOKEN, END_TOKEN]:
            return False
        if raw_ev.atomic != transformed_ev.atomic:
            return False
        if raw_ev.min_length >= transformed_ev.max_length:
            return True
        return False

    def score_function(self, model):
        if self.score == -1:
            self.get_best_range(model)
        return self.score

    def score_range(self, value_list, model):
        return model.get_sim(value_list, self.transformed_ev.values)

    def transform(self):
        return [x[self.start_index:self.end_index] for x in self.raw_ev.values]


class InvSubStr(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(InvSubStr, self).__init__(raw_ev, transformed_ev)
        self.score = -1
        self.start_index = -1
        self.end_index = -1
        self.min_length = transformed_ev.min_length

    def get_best_range(self, model):
        length = self.raw_ev.min_length
        # print("Value list", self.raw_ev.values)
        # print("Value list", self.transformed_ev.values)

        score_dict = defaultdict(lambda: 0)

        for i in range(self.min_length - length + 1):
            value_list = []
            for value in self.transformed_ev.values:
                value_list.append(value[i: i + length])
            score_dict[i] = self.score_range(value_list, model)

            value_list = []
            for value in self.transformed_ev.values:
                value_list.append(value[i: i + length])
            score_dict[-i] = self.score_range(value_list, model)

        # print(score_dict, min_length, length)
        if score_dict:
            self.score = max(score_dict.values())
        else:
            self.score = 0
        if self.score:
            self.start_index = list(score_dict.keys())[list(score_dict.values()).index(self.score)]
            self.end_index = self.start_index + length

    def __str__(self):
        return "InvSubStr(%s, %s)" % (self.start_index, self.end_index)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.min_length != raw_ev.max_length - 1:
            return False
        if transformed_ev.atomic in [START_TOKEN, END_TOKEN] or raw_ev.atomic in [START_TOKEN, END_TOKEN]:
            return False
        if raw_ev.atomic != transformed_ev.atomic or transformed_ev.max_length > raw_ev.max_length \
                or transformed_ev.min_length > raw_ev.min_length:
            return False
        if transformed_ev.min_length >= raw_ev.max_length:
            return True
        return False

    def score_function(self, model):
        if self.score == -1:
            self.get_best_range(model)
        return self.score

    def score_range(self, value_list, model):
        return model.get_sim(value_list, self.raw_ev.values)

    def transform(self):
        return [
            self.transformed_ev.values[0][:self.start_index] + x + self.transformed_ev.values[0][
                                                                   self.start_index + self.length:]
            for x in self.raw_ev.values]
