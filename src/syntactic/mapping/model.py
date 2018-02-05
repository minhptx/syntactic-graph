from collections import defaultdict, OrderedDict

import pandas as pd
import regex as re
from py_stringmatching import SoftTfIdf

from syntactic.generation.atomic import PUNCTUATION, TOKEN_TYPES, WHITESPACE
from syntactic.mapping.atomic import SubStr


class MappingModel:
    def __init__(self, raw_model, transformed_model):
        self.raw_model = raw_model
        self.transformed_model = transformed_model
        self.constant_scores = defaultdict(lambda: [])

    def map(self):
        raw_nested_list, transformed_nested_list = self.segment()
        raw_format_dict = defaultdict(lambda: None)
        transformed_format_dict = defaultdict(lambda: None)

        for idx, raw_list in enumerate(raw_nested_list):
            df = pd.DataFrame(raw_list)
            raw_format_dict[idx] = Format.from_df(df, idx)

        for idx, transformed_list in enumerate(transformed_nested_list):
            df = pd.DataFrame(transformed_list)
            transformed_format_dict[idx] = Format.from_df(df, idx)

        score_dict = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_dict = {}
        column_mapped_dict = defaultdict(lambda: defaultdict(lambda: None))
        for format_1 in raw_format_dict.values():
            for format_2 in transformed_format_dict.values():
                print("Format id pair", format_1.id, format_2.id)
                result = format_1.find_column_matching_from(format_2)
                print(result)
                score_dict[format_1.id][format_2.id] = result[1]
                column_mapped_dict[format_1.id][format_2.id] = result[0]
            mapped_dict[format_1.id] = sorted(score_dict[format_1.id].items(), key=lambda x: x[1], reverse=True)[0][
                0]

        raw_final_list = []
        transformed_final_list = []
        for format_pair in mapped_dict.items():
            raw_format = raw_format_dict[int(format_pair[0])]
            transformed_format = transformed_format_dict[int(format_pair[1])]
            column_matches = column_mapped_dict[raw_format.id][transformed_format.id]
            new_transformed_format = transformed_format.transform_by(raw_format, column_matches)
            transformed_df = new_transformed_format.to_df()
            raw_df = raw_format.to_df()

            transformed_final_list.extend(transformed_df.apply(lambda x: "".join(x), axis=1))
            raw_final_list.extend(raw_df.apply(lambda x: "".join(x), axis=1))
        return raw_final_list, transformed_final_list

    def segment(self):
        raw_count_dict = defaultdict(lambda: defaultdict(lambda: 0))
        transformed_count_dict = defaultdict(lambda: defaultdict(lambda: 0))

        raw_segmented_list = []
        transformed_segmented_list = []
        for idx_1, raw_cluster in enumerate(self.raw_model.clusters):
            raw_count_dict[idx_1] = MappingModel.count_ngram_and_filter(raw_cluster)
            rule_count_dict, key_to_rule_dict, position_dict = self.learn_extraction_rules(raw_count_dict[idx_1],
                                                                                           raw_cluster.values)
            rule_key_list = []

            for rule_key in rule_count_dict:
                if rule_count_dict[rule_key] * 1.0 / len(raw_cluster.values) == 1:
                    rule_key_list.append(rule_key)
            raw_segmented_list.append(
                MappingModel.split_value_list_by_rule(raw_cluster.values, position_dict, rule_key_list))

        for idx_1, transformed_cluster in enumerate(self.transformed_model.clusters):
            transformed_count_dict[idx_1] = MappingModel.count_ngram_and_filter(transformed_cluster)
            rule_count_dict, key_to_rule_dict, position_dict = self.learn_extraction_rules(
                transformed_count_dict[idx_1], transformed_cluster.values)

            rule_key_list = []

            for rule_key in rule_count_dict:
                if rule_count_dict[rule_key] * 1.0 / len(transformed_cluster.values) == 1:
                    rule_key_list.append(rule_key)

            transformed_segmented_list.append(
                MappingModel.split_value_list_by_rule(transformed_cluster.values, position_dict, rule_key_list))

        return raw_segmented_list, transformed_segmented_list

    @staticmethod
    def count_ngram_and_filter(cluster):
        main_value = cluster.values[0]
        candidate_list = []

        while main_value:
            for token in TOKEN_TYPES:
                match = re.match("^%s" % token.regex, main_value)
                if match:
                    candidate_list.append(match.group())
                    main_value = main_value[len(match.group()):]

        ngram_count_dict = defaultdict(lambda: 0)

        for value in cluster.values:
            added = []
            for candidate in candidate_list:
                if candidate not in added:
                    ngram_count_dict[candidate] += 1
                    added.append(candidate)

        remove_list = []

        for text in ngram_count_dict:
            if not text.isalpha() and not text.isdigit() and not re.match(PUNCTUATION.regex, text) and not re.match(
                    WHITESPACE.regex, text):
                remove_list.append(text)

        for text in remove_list:
            del ngram_count_dict[text]
        return ngram_count_dict

    @staticmethod
    def learn_extraction_rules(ngram_count_dict, values):
        position_dict = defaultdict(lambda: defaultdict(lambda: []))
        rule_count_dict = defaultdict(lambda: 0)
        key_to_rule_dict = {}

        for ngram in ngram_count_dict:
            for idx, value in enumerate(values):
                if ngram not in value:
                    continue

                extraction_rule_list, position_list = SubStr.generate("|" + value + "|", ngram)

                for rule in extraction_rule_list:
                    rule_count_dict[str(rule)] += 1
                    key_to_rule_dict[str(rule)] = rule
                    position_dict[str(rule)][idx].extend(position_list)

        return rule_count_dict, key_to_rule_dict, position_dict

    @staticmethod
    def split_value_list_by_rule(value_list, position_dict, rule_key_list):
        result_list = []
        for idx, raw_value in enumerate(value_list):
            text = "|" + raw_value + "|"
            segmented_value = []
            start = 0
            position_list = []
            for rule_key in rule_key_list:
                for pos_tup in position_dict[rule_key][idx]:
                    position_list.append(pos_tup)
            for start_pos, end_pos in list(sorted(set(position_list))):
                if start_pos < start:
                    continue
                segmented_value.append(text[start:start_pos])
                segmented_value.append(text[start_pos:end_pos])
                start = end_pos
            segmented_value.append(text[start:])
            segmented_value[0] = segmented_value[0][1:]
            segmented_value[-1] = segmented_value[-1][:-1]
            segmented_value = [x for x in segmented_value if x]
            result_list.append(segmented_value)
        return result_list

    def score_rule(self, rule, other_attribute):
        score = 0
        if other_attribute:
            if rule.text in other_attribute.constants_with_scores:
                score += other_attribute.constants_with_scores[rule.text]
            if rule.text not in other_attribute.constants_with_scores and other_attribute.text:
                score -= (other_attribute.text.count(rule.text) * 1.0 / len(other_attribute.value_list))
        return score


class Format(object):
    def __init__(self, format_id):
        self.id = str(format_id)
        self.column_dict = OrderedDict()
        self.metric_learner = None
        self.tf_idf_vectorizer = None

    def learn_tf_idf(self):
        if self.tf_idf_vectorizer is None:
            pass
            # self.tf_idf_vectorizer = TfidfVectorizer()
            # self.tf_idf_vectorizer.fit([" ".join(col.one_token_list) for col in self.column_dict.values()])

    def to_df(self):
        data_dict = {str(name): column.value_list for name, column in self.column_dict.items()}
        return pd.DataFrame.from_dict(data_dict, orient="index", dtype=object).transpose()

    def __len__(self):
        return len(self.column_dict[0])

    @staticmethod
    def from_file(file_path, format_id):
        df = pd.read_csv(file_path, dtype=object).fillna("")
        return Format.from_df(df, format_id)

    @staticmethod
    def from_df(df, format_id):
        format_ = Format(format_id)
        df = df.dropna(axis=1, how="all")
        for column_name in df.columns.values:
            data = df[column_name].tolist()
            column = Column(column_name)
            for value in data:
                column.append(value)
            format_.column_dict[column.name] = column

        return format_

    def join(self, other_format, mappings):
        mapped_columns = []
        for id_1, id_2 in mappings.items():
            column_1 = other_format.column_dict[id_1]
            column_2 = self.column_dict[id_2]
            column_2.join(column_1)
            mapped_columns.append(column_2.name)

        length = len(list(other_format.column_dict.values())[0].value_list)
        for name, column in self.column_dict.items():
            if name not in mapped_columns:
                column.value_list.extend(["" for x in range(length)])

    def transform_by(self, other_format, mapping_dict):
        new_length = 0
        format_ = Format(self.id)

        for column_name in self.column_dict:
            format_.column_dict[column_name] = Column(column_name)

        for column_name, other_column_name in mapping_dict.items():
            new_length = len(other_format.column_dict[column_name].value_list)
            for value in other_format.column_dict[column_name].value_list:
                format_.column_dict[other_column_name].append(value)

        for column_name in self.column_dict:
            if column_name not in mapping_dict.values():
                for i in range(new_length):
                    if self.column_dict[column_name].is_constant:
                        format_.column_dict[column_name].append(self.column_dict[column_name].main_value)
                    else:
                        format_.column_dict[column_name].append("")

        column_keys = list(format_.column_dict.keys())

        if len(format_.column_dict[column_keys[0]].value_list) == 1:
            return format_

        for idx_1 in range(len(format_.column_dict[column_keys[0]].value_list)):
            for idx_2, column_name in enumerate(column_keys):
                if not format_.column_dict[column_name].is_optional and \
                        not format_.column_dict[column_name].is_constant:
                    continue
                else:
                    if idx_2 > 0:
                        pre_column_key = column_keys[idx_2 - 1]
                        if not format_.column_dict[pre_column_key].value_list[idx_1]:
                            format_.column_dict[column_name].value_list[idx_1] = ""
                            continue
                    if idx_2 < len(column_keys) - 1:
                        post_column_key = column_keys[idx_2 + 1]
                        if not format_.column_dict[post_column_key].value_list[idx_1]:
                            format_.column_dict[column_name].value_list[idx_1] = ""
                            continue
        return format_

    def find_column_matching_from(self, other_format):
        mapped_list_1 = []
        mapped_list_2 = []
        mapping_dict = {}

        score_dict = defaultdict(lambda: defaultdict(lambda: 0))
        for column_1 in self.column_dict.values():
            for column_2 in other_format.column_dict.values():
                if column_2.is_constant:
                    continue
                else:
                    if column_1.name in mapped_list_1 or column_2.name in mapped_list_2:
                        continue
                    else:
                        print(column_1.name, column_2.name, column_1.similarity(column_2))
                        score_dict[column_1.name][column_2.name] = column_1.similarity(column_2)

        format_score = 0

        score_dict = {(x, y): score_dict[x][y] for x in score_dict for y in score_dict[x]}

        for (col_1, col_2), score in sorted(score_dict.items(), key=lambda x: x[1], reverse=True):
            if col_1 not in mapped_list_1 and col_2 not in mapped_list_2:
                format_score += score
                mapping_dict[col_1] = col_2
                mapped_list_1.append(col_1)
                mapped_list_2.append(col_2)

        format_score = format_score \
                       / (len(other_format.column_dict) - 0.9 * len(
            [x for x in other_format.column_dict.values() if x.is_constant]))

        if format_score < 0.1:
            return {'0': '0'}, 0
        return mapping_dict, format_score


class Column(object):
    def __init__(self, name):
        self.name = str(name)
        self.main_value = None
        self.value_list = []
        self.one_token_list = []
        self.is_constant = True
        self.is_optional = False
        self.text_list = []
        self.numeric_list = []
        self.feature_matrix = None

    def extract_feature_vector(self, metric_learner):
        if self.feature_matrix is None:
            self.feature_matrix = metric_learner.convert_to_features(self)

    def is_same_length(self):
        return all(len(i) == len(self.value_list[0]) for i in self.value_list)

    def append(self, value):
        if value:
            self.value_list.append(value)
            self.main_value = value
            self.one_token_list.append(value.replace(" ", "_"))

            if self.is_constant:
                if len(self.value_list) > 1 and value != self.value_list[0]:
                    self.is_constant = False
        else:
            self.value_list.append("")
            self.one_token_list.append("")
            self.is_optional = True

    def __len__(self):
        return len(self.value_list)

    def __getitem__(self, index):
        return self.value_list[index]

    def extend(self, values):
        for value in values:
            self.value_list.append(value)

    def replace_by(self, other_column):
        if self.is_optional:
            self.value_list = []
            for value in other_column.value_list:
                if value:
                    self.value_list.append(value)

    def join(self, other_column):
        for value in other_column.value_list:
            self.append(value)

    def similarity(self, other_column):

        soft_tfidf = SoftTfIdf([self.value_list, other_column.value_list])
        return (soft_tfidf.get_raw_score(self.value_list, other_column.value_list))
