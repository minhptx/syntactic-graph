import csv
import operator
import os
import re
import string
from collections import defaultdict
from itertools import groupby

import nltk
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer

from formatting.model import SubStr
from utils import nlp

NUMWRD = r"^[0-9]+$"
LWRD = r"^[a-z]+$"
UWRD = r"^[A-Z][a-z]+S"
PUNC = "^[%s]+$" % (string.punctuation + "|")
SPACE = "^\s+$"
TOKEN_TYPES = {"NUM": NUMWRD, "LWD": LWRD, "UWD": UWRD, "PUN": PUNC, "SPACE": SPACE}


class IndexedValue:
    def __init__(self, index, value, is_constant=False):
        self.text = value
        self.index = index


class Attribute:
    def __init__(self, value_list):
        self.text = "|".join(value_list)
        self.value_list = self.index_data(value_list)
        self.constants_with_scores = defaultdict(lambda: 0)
        self.token_list = nltk.wordpunct_tokenize(self.text)
        self.candidate_list = []

    def index_data(self, value_list):
        return [IndexedValue(index, [value]) if value else IndexedValue(index, []) for index, value in
                enumerate(value_list)]

    def find_candidates(self, other_column_token_list):
        for token in other_column_token_list:
            matches = re.finditer(re.escape(token), self.text)
            for match in matches:
                start = match.start()
                end = match.end()
                if start > 0:
                    prefix = self.text[start - 1]
                    self.candidate_list.append(prefix)
                if end < len(self.text) - 1:
                    suffix = self.text[end + 1]
                    self.candidate_list.append(suffix)

    def cluster(self, other_attribute=None):
        if other_attribute:
            self.find_candidates(other_attribute.token_list)
        cluster = Cluster(self.value_list, self.candidate_list, other_attribute)
        new_clusters = cluster.train()
        # clusters, constants = cluster.train()
        #
        # new_clusters = defaultdict(lambda: [])
        # for id, value_list in clusters.items():
        #     new_clusters[id] = value_list
        #     for constant in constants:
        #         new_clusters[id] = Cluster.split_value_list_by_rule(new_clusters[id], constant)

        output_data = defaultdict(lambda: [])

        for cluster_id, cluster_values in new_clusters.items():
            for value in cluster_values:
                output_data[cluster_id].append([value.index] + value.text)

        return output_data

    def cluster_and_output(self, output_path, other_attribute=None):
        output_data = self.cluster(other_attribute)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for cluster_id, cluster_data in output_data.items():
            df = pd.DataFrame(cluster_data).astype(str)

            for column_name in df.columns.values:
                if column_name == 0:
                    continue
                count_dict = df[column_name].value_counts().to_dict()
                for value, count in count_dict.items():
                    self.constants_with_scores[value] += count * 1.0 / len(self.value_list)

            df.to_csv(os.path.join(output_path, str(cluster_id) + ".csv"), index=False, quoting=csv.QUOTE_ALL)
        return output_data


class Cluster:
    def __init__(self, indexed_value_list, candidate_list, other_attribute):
        self.indexed_value_list = [x for x in indexed_value_list if x.text]
        self.ngram_count_dict = defaultdict(lambda: 0)
        self.candidate_list = set(candidate_list)
        self.other_attribute = other_attribute
        self.value_text = "|".join(["".join(x.text) for x in indexed_value_list])

    def train(self):
        print("Before training:", len(self.indexed_value_list), [x.text for x in self.indexed_value_list])
        if len(self.indexed_value_list) < 3:
            return {0: self.indexed_value_list}

        print("Start ...")
        print([x.text for x in self.indexed_value_list])

        self.count_ngram_and_filter([1, 2, 3, 4, 5])
        print("Finish couting ngram ...")

        rule_count_dict, key_to_rule_dict, position_dict = self.learn_extraction_rules()
        rule_score_dict = defaultdict(lambda: 0)

        print("Finish learning rules ...")

        for rule_key in rule_count_dict:
            rule_score_dict[rule_key] += rule_count_dict[rule_key] * 1.0 / len(self.indexed_value_list)
            rule_score_dict[rule_key] += self.score_rule(key_to_rule_dict[rule_key], self.other_attribute)
            # print(rule_key, rule_count_dict[rule_key] * 1.0 / len(self.indexed_value_list),
            #       self.score_rule(key_to_rule_dict[rule_key], self.other_attribute), rule_count_dict[rule_key])

        rule_clusters, inverted_indices = self.cluster_extraction_rules(rule_count_dict, key_to_rule_dict)

        print("Finish scoring rules ...")

        rule_key_list = set()
        rule_cluster_count = 0

        for rule_key, score in sorted(rule_score_dict.items(), key=operator.itemgetter(1), reverse=True):
            # print(rule_key, score)
            if score > 0.5 and rule_key not in rule_key_list:
                key = inverted_indices[rule_key]
                for rule in rule_clusters[key]:
                    rule_key_list.add(rule)
                rule_cluster_count += 1
            if score < 0.5:
                break

        # print("LENGTH:", len(rule_key_list))
        value_list = self.split_value_list_by_rule(self.indexed_value_list, position_dict, rule_key_list)
        clusters, labels = self.cluster_by_constant(value_list)

        if clusters:
            new_cluster_id = 0

            new_clusters = defaultdict(lambda: [])

            for cluster_id, value_list in clusters.items():
                sub_ids_for_value_dict = defaultdict(lambda: [])
                sub_values_for_value_dict = defaultdict(lambda: [])

                columns = self.columnize(value_list)
                if len(columns) == 1:
                    return clusters
                for column in columns.values():
                    sub_clusters = Cluster(column, self.candidate_list, self.other_attribute).train()
                    for sub_cluster_id, sub_values in sub_clusters.items():
                        for sub_value in sub_values:
                            sub_ids_for_value_dict[sub_value.index].append(sub_cluster_id)
                            sub_values_for_value_dict[sub_value.index].extend(sub_value.text)

                for label, indexed_tups in groupby(sorted(sub_ids_for_value_dict.items(), key=operator.itemgetter(1)),
                                                   key=operator.itemgetter(1)):
                    for index, _ in indexed_tups:
                        indexed_value = IndexedValue(index, sub_values_for_value_dict[index])
                        new_clusters[new_cluster_id].append(indexed_value)
                    new_cluster_id += 1

            return new_clusters
        return {0: self.indexed_value_list}

    def count_ngram_and_filter(self, n_list):
        for n in n_list:
            for indexed_value in self.indexed_value_list:
                sentence = indexed_value.text[0]
                if n >= len(sentence):
                    continue
                for i in range(0, len(sentence) - n + 1):
                    text = sentence[i:i + n]
                    self.ngram_count_dict[text] += 1

        del_list = []
        for ngram, count in self.ngram_count_dict.items():
            if count < len(self.indexed_value_list) * 0.1:
                del_list.append(ngram)
            elif ngram.isalpha():
                if ngram.islower():
                    del_list.append(ngram)
            elif ngram.isdigit():
                if len(ngram) < 2:
                    del_list.append(ngram)
            elif not ngram.isalpha() and not ngram.isdigit() and ngram not in string.punctuation and ngram != " ":
                del_list.append(ngram)

        for ngram in del_list:
            del self.ngram_count_dict[ngram]

    def cluster_extraction_rules(self, rule_count_dict, key_to_rule_dict):
        if not key_to_rule_dict:
            return {}, {}
        feature_vectors = []
        rule_list = []
        for key in key_to_rule_dict:
            feature_value = {}
            rule = key_to_rule_dict[key]
            for idx, token in enumerate(rule.start_pos.pre_regex.token_seq):
                feature_value["START PRE %s" % idx] = token.type
            for idx, token in enumerate(rule.start_pos.post_regex.token_seq):
                feature_value["START POS %s" % idx] = token.type
            for idx, token in enumerate(rule.end_pos.pre_regex.token_seq):
                feature_value["END PRE %s" % idx] = token.type
            for idx, token in enumerate(rule.end_pos.post_regex.token_seq):
                feature_value["END POS %s" % idx] = token.type
            feature_vectors.append(feature_value)
            rule_list.append(rule)

        data = DictVectorizer().fit_transform(feature_vectors)
        data = data.toarray()

        unique, indices = np.unique(data, return_inverse=True, axis=0)

        rule_clusters = defaultdict(lambda: [])
        labels = []

        for idx, rule in enumerate(rule_list):
            rule_clusters[indices[idx]].append(rule)
            labels.append(data[idx])

        index = len(rule_clusters)
        idx = 0
        while idx < len(rule_clusters):
            key = list(rule_clusters.keys())
            rule_list = rule_clusters[key[idx]]
            for rule_1 in rule_list[1:]:
                if rule_1 == rule_list[0]:
                    idx += 1
                    continue
                if nlp(rule_1.text).similarity(nlp(rule_list[0].text)) < 0.8:
                    rule_clusters[index].append(rule_1)
                    index += 1
            idx += 1

        inverted_indices = {}

        for key in rule_clusters:
            for idx, rule in enumerate(rule_clusters[key]):
                rule_clusters[key][idx] = str(rule_clusters[key][idx])
                inverted_indices[str(rule_clusters[key][idx])] = key

        return rule_clusters, inverted_indices

    def learn_extraction_rules(self):
        position_dict = defaultdict(lambda: defaultdict(lambda: []))
        rule_count_dict = defaultdict(lambda: 0)
        key_to_rule_dict = {}

        for ngram in self.ngram_count_dict:
            for value in self.indexed_value_list:
                if ngram not in value.text[0]:
                    continue

                extraction_rule_list, position_list = SubStr.generate("|" + value.text[0] + "|", ngram)

                for rule in extraction_rule_list:
                    rule_count_dict[str(rule)] += 1
                    key_to_rule_dict[str(rule)] = rule
                    position_dict[str(rule)][value.index].extend(position_list)

        # print(sorted(rule_count_dict.items(), key=lambda x: x[1], reverse=True)[:100])
        return rule_count_dict, key_to_rule_dict, position_dict

    @staticmethod
    def cluster_by_constant(value_list, threshold=40):
        feature_vectors = []
        for idx, value in enumerate(value_list):
            feature_value = {"VALUE": len(value.text)}
            for idx, token in enumerate(value.text):
                is_matched = False
                for token_type, regex in TOKEN_TYPES.items():
                    match = re.match(regex, token)
                    if match:
                        if token_type == "PUN":
                            feature_value["REGEX %s" % idx] = token
                            is_matched = True
                        else:
                            feature_value["REGEX %s" % idx] = token_type
                            is_matched = True
                if not is_matched:
                    feature_value["REGEX %s" % idx] = "OTHER"
            feature_vectors.append(feature_value)
        data = DictVectorizer().fit_transform(feature_vectors)

        data = data.toarray()

        unique, indices = np.unique(data, return_inverse=True, axis=0)
        # if len(counts) > threshold:
        #     return None, None

        clusters = defaultdict(lambda: [])
        labels = []

        print("Num Clusters: ", len(clusters))

        for idx, value in enumerate(value_list):
            clusters[indices[idx]].append(value)
            labels.append(data[idx])
        return clusters, labels

    @staticmethod
    def split_value_list_by_rule(indexed_value_list, position_dict, rule_key_list):
        value_list = []
        for indexed_value in indexed_value_list:
            text = "|" + indexed_value.text[0] + "|"
            value = []
            start = 0
            # print(position_dict[rule_key][indexed_value.index])
            position_list = []
            for rule_key in rule_key_list:
                for pos_tup in position_dict[rule_key][indexed_value.index]:
                    position_list.append(pos_tup)
            # print(list(sorted(set(position_list))))
            for start_pos, end_pos in list(sorted(set(position_list))):
                if start_pos < start:
                    continue
                value.append(text[start:start_pos])
                value.append(text[start_pos:end_pos])
                start = end_pos
            value.append(text[start:])
            value[0] = value[0][1:]
            value[-1] = value[-1][:-1]
            # print(value)
            value = [x for x in value if x]
            value_list.append(IndexedValue(indexed_value.index, value))
        return value_list

    @staticmethod
    def columnize(indexed_value_list):
        # common_len = max([len(x.text) for x in indexed_value_list])
        columns = defaultdict(lambda: [])
        for value in indexed_value_list:
            for idx1, part in enumerate(value.text):
                columns[idx1].append(IndexedValue(value.index, [part]))
                # for idx2 in range(len(value.text), common_len):
                #     columns[idx2].append(IndexedValue(value.index, [""]))
        return columns

    def score_rule(self, rule, other_attribute):
        score = 0
        # if self.candidate_list:
        #     if rule.text[-1] in self.candidate_list or rule.text[0] in self.candidate_list:
        #         score += 0.3
        if other_attribute:
            if rule.text in other_attribute.constants_with_scores:
                # print(other_attribute.constants_with_scores[rule.text])
                score += other_attribute.constants_with_scores[rule.text]
            if rule.text not in other_attribute.constants_with_scores and other_attribute.text:
                score -= (other_attribute.text.count(rule.text) * 1.0 / len(other_attribute.value_list))
        return score
