import json
import os
from collections import defaultdict, OrderedDict

import numpy as np
import pandas as pd
from py_stringmatching import SoftTfIdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from formatting.learner import Attribute
from utils import nlp
from utils.list_helpers import list_histogram_similarity, list_tfidf_cosine_similarity, list_jaccard_similarity


class Type(object):
    def __init__(self, name):
        self.name = name
        self.format_dict = {}

    def unify(self):
        ordered_format_list = sorted(self.format_dict.values(), key=lambda x: len(x.column_dict), reverse=True)

        main_format_list = ordered_format_list[:1]
        matching_dict = defaultdict(lambda: None)

        for aligning_format in ordered_format_list[1:]:
            if len(list(aligning_format.column_dict.values())[0].value_list) > 1:
                continue
            found = False
            for main_format in main_format_list:
                is_matched, mappings = aligning_format.find_column_joining_matching(main_format)
                if is_matched:
                    matching_dict[aligning_format.id] = (mappings, main_format)
                    found = True
                    break
            if not found:
                main_format_list.append(aligning_format)

        new_format_list = ordered_format_list[:]

        for format_id in matching_dict:
            mappings, main_format = matching_dict[format_id]
            aligning_format = self.format_dict[format_id]
            main_format.join(aligning_format, mappings)
            new_format_list.remove(aligning_format)

        self.format_dict = {}
        for new_format in new_format_list:
            self.format_dict[new_format.id] = new_format

    @staticmethod
    def from_folder(folder_path, name):
        type_ = Type(name)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            format_ = Format.from_file(file_path, os.path.splitext(file_name)[0])
            type_.format_dict[format_.id] = format_
        return type_

    @staticmethod
    def from_dict(df_dict, name):
        type_ = Type(name)
        for format_id, df in df_dict.items():
            format_ = Format.from_df(df, format_id)
            type_.format_dict[format_.id] = format_
        return type_

    def find_format_matching_from(self, other_type, is_indexed=True):
        score_dict = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_dict = {}
        column_mapped_dict = defaultdict(lambda: defaultdict(lambda: None))
        for format_1 in self.format_dict.values():
            for format_2 in other_type.format_dict.values():
                print("Format id pair", format_1.id, format_2.id)
                result = format_1.find_column_matching_from(format_2, is_indexed)
                print(result)
                score_dict[format_1.id][format_2.id] = result[1]
                column_mapped_dict[format_1.id][format_2.id] = result[0]
            mapped_dict[format_1.id] = sorted(score_dict[format_1.id].items(), key=lambda x: x[1], reverse=True)[0][0]
        return mapped_dict, column_mapped_dict





class ConstrainedColumn(Column):
    def __init__(self, name, possible_values):
        super(ConstrainedColumn, self).__init__(name)
        self.constrained_values = possible_values
        self.default_value = possible_values[0]
        for value in possible_values:
            self.append(value)


class ConstrainedFormat(Format):
    def __init__(self, format_id):
        super(ConstrainedFormat, self).__init__(format_id)
        self.column_dict = {}
        self.constants = []

    def to_template_list(self):
        template_list = []
        for column_name in self.column_dict:
            if isinstance(self.column_dict[column_name], ConstrainedColumn):
                template_list.append(self.column_dict[column_name].default_value)
            else:
                template_list.append(self.column_dict[column_name].value_list[0])
        return template_list

    @staticmethod
    def from_template_file(file_path, format_id):
        format_ = ConstrainedFormat(format_id)
        with open(file_path, 'r') as reader:
            name = 0
            for line in reader.readlines():
                # print("Line:", line.strip())
                if line.startswith("Constant"):
                    constant = line.split("|")[1].strip()
                    column = Column(str(name))
                    format_.constants.append(constant)
                    for i in range(100):
                        column.append(constant)
                    format_.column_dict[column.name] = column
                else:
                    value_list = json.loads(line.strip())
                    column = ConstrainedColumn(str(name), value_list)
                    column.is_constant = False
                    format_.column_dict[column.name] = column
                name += 1
        return format_


class ConstrainedType(Type):
    def __init__(self, name):
        super(ConstrainedType, self).__init__(name)

    @staticmethod
    def from_template_folder(folder_path, name):
        type_ = ConstrainedType(name)
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            format_ = ConstrainedFormat.from_template_file(file_path, os.path.splitext(file_name)[0])
            type_.format_dict[format_.id] = format_
        return type_

    def to_template(self):
        value_list = []
        template = Attribute(value_list)
        for format_ in self.format_dict.values():
            value_list += [x for column in format_.column_dict.values() for x in column]
            template.constants_with_scores.update({c: 1 for c in format_.constants})
        return template
