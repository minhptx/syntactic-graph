from collections import defaultdict

from syntactic.generation.atomic import *


class Operation(object):
    def __init__(self, raw_ev, transformed_ev, *args, **kwargs):
        self.raw_list = raw_ev
        self.transformed_list = transformed_ev
        self.score = 0

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        pass


class Transformation:

    @staticmethod
    def generate(raw_path, tranformed_path):
        matches = defaultdict(lambda: [])

        for idx_1, edge_1 in enumerate(raw_path):
            for idx_2, edge_2 in enumerate(tranformed_path):
                for ev_1 in edge_1.value_list:
                    for ev_2 in edge_2.value_list:
                        if ev_1.is_subset(ev_2):
                            matches[idx_1].append((ev_2, idx_2))

    @staticmethod
    def get_all_candidates(ev_1, ev_2):
        candidate_operations = []
        if ev_2.atomic == LOWER_CASE and ev_1.atomic != LOWER_CASE:
            candidate_operations.append(Lower(ev_1, ev_2))
        if ev_2.atomic == UPPER_CASE and ev_1.atomic != UPPER_CASE:
            candidate_operations.append(Upper(ev_1, ev_2))
        if ev_1.length != -1 and ev_2 != -1:
            if ev_1.length < ev_2.length:
                candidate_operations.append(PartOf(ev_1, ev_2))
            elif ev_1.length > ev_2.length:
                for i in range(0, ev_1.length - ev_2.length):
                    candidate_operations.append(SubStr(ev_1, ev_2, i))
        elif ev_1.length != -1:
            candidate_operations.append(PartOf(ev_1, ev_2))


class Constant(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Constant, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if isinstance(transformed_ev.atomic, Constant):
            return True
        else:
            return False


class PartOf(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(PartOf, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.atomic != transformed_ev.atomic:
            return False
        if raw_ev.length <= transformed_ev.length:
            return True


class Upper(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Upper, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic == UPPER_CASE and raw_ev in [LOWER_CASE, ALPHABET, PROPER_CASE]:
            if transformed_ev.length == raw_ev.length:
                return True
        return False


class Lower(Operation):
    def __init__(self, raw_ev, transformed_ev):
        super(Lower, self).__init__(raw_ev, transformed_ev)

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if transformed_ev.atomic == LOWER_CASE and raw_ev in [UPPER_CASE, ALPHABET, PROPER_CASE]:
            if transformed_ev.length == raw_ev.length:
                return True
        return False


class SubStr(Operation):
    def __init__(self, raw_ev, transformed_ev, start_index):
        super(SubStr, self).__init__(raw_ev, transformed_ev)
        self.start_index = start_index

    @staticmethod
    def check_condition(raw_ev, transformed_ev):
        if raw_ev.atomic != transformed_ev.atomic:
            return False
        if raw_ev.length >= transformed_ev.length:
            return True
