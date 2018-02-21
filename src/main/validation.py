import codecs
import os
from collections import defaultdict

import editdistance
import numpy as np
import pandas as pd

from evaluation.validator import Validator

input_datapath = "data/transformation/input/raw"
desire_datapath = "data/transformation/input/transformed"
output_datapath = "data/result"
groundtruth_datapath = "data/transformation/groundtruth"

true_count_dict = defaultdict(lambda: 0)
total_count_dict = defaultdict(lambda: 0)
edit_distance_dict = defaultdict(lambda: 0)
org_edit_distance_dict = defaultdict(lambda: 0)
confidence_dict = defaultdict(lambda: 0)
for file_name in sorted(os.listdir(output_datapath)):
    output_file_path = os.path.join(output_datapath, file_name)
    desire_file_path = os.path.join(desire_datapath, file_name)
    groundtruth_file_path = os.path.join(groundtruth_datapath, file_name)
    input_file_path = os.path.join(input_datapath, file_name)

    with codecs.open(input_file_path, encoding="utf-8") as reader:
        input_data = list(reader.readlines())

    with codecs.open(output_file_path, encoding="utf-8") as reader:
        output_data = list(reader.readlines())

    with codecs.open(groundtruth_file_path, encoding="utf-8") as reader:
        groundtruth_data = list(reader.readlines())
        if groundtruth_data[0][0] == '"':
            groundtruth_data = [x.strip()[1:-1] for x in groundtruth_data]

    for idx, line in enumerate(output_data):
        # print(line.strip(), groundtruth_data[idx].strip())
        try:
            if line.strip() == groundtruth_data[idx].strip():
                true_count_dict[file_name] += 1
            edit_distance_dict[file_name] += editdistance.eval(line.strip(), groundtruth_data[idx].strip())
            org_edit_distance_dict[file_name] += editdistance.eval(groundtruth_data[idx].strip(),
                                                                   input_data[idx].strip())
        except:
            edit_distance_dict[file_name] += len(line.strip())
            org_edit_distance_dict[file_name] += len(input_data[idx].strip())
            pass
        total_count_dict[file_name] += 1

    validator = Validator(output_file_path, desire_file_path)
    print(file_name)
    confidence_dict[file_name] += ((1 - validator.classify())) / 0.5

result_list = []
for key in total_count_dict:
    result_list.append([
        key, true_count_dict[key] * 1.0 / total_count_dict[key], edit_distance_dict[key] * 1.0 / total_count_dict[key],
        org_edit_distance_dict[key] * 1.0 / total_count_dict[key], confidence_dict[key], total_count_dict[key]
    ])

result_list.append([
    "Mean",
    np.mean([x[1] for x in result_list]),
    np.mean([x[2] for x in result_list]),
    np.mean([x[3] for x in result_list]), 0, 0
])

result_list.append([
    "Total",
    sum(true_count_dict.values()) * 1.0 / sum(total_count_dict.values()),
    sum(edit_distance_dict.values()) * 1.0 / sum(total_count_dict.values()),
    sum(org_edit_distance_dict.values()) * 1.0 / sum(total_count_dict.values()), 0, 0
])

df = pd.DataFrame(result_list)
df.to_csv(
    "result.csv",
    header=["Name", "Accuracy", "Avg Distance", "Avg Org Distance", "Confidence Score", "Countgroundtruth"],
    index=False)
