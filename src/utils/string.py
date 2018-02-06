from collections import Counter

import jellyfish
from py_stringmatching import SoftTfIdf
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math


def lcs(a, b):
    lengths = [[0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x - 1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y - 1]:
            y -= 1
        else:
            assert a[x - 1] == b[y - 1]
            result = a[x - 1] + result
            x -= 1
            y -= 1
    return result


def jaccard_similarity(set_1, set_2):
    set_1 = set(set_1)
    set_2 = set(set_2)

    n = len(set_1.intersection(set_2))
    # print(set_1, set_2, n)
    try:
        return n / float(len(set_1) + len(set_2) - n)
    except Exception as e:
        print(e)
        return 0


def jaccard_subset_similarity(set_1, set_2):
    n = 0
    count = 0
    for value_1 in set_1:
        for value_2 in set_2:
            if value_1 in value_2:
                n += len(value_1) * 1.0 / len(value_2)
                count += 1
                break

    return n / float(len(set_1) + len(set_2) - count)


def list_jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)


def list_cosine_similarity(list_1, list_2):
    vec1 = Counter(list_1)
    vec2 = Counter(list_2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def list_tfidf_cosine_similarity(list_1, list_2, tfidf_vectorizer):
    tfidf_list_1 = tfidf_vectorizer.transform(list_1)
    tfidf_list_2 = tfidf_vectorizer.transform(list_2)
    return np.abs(cosine_similarity(tfidf_list_1, tfidf_list_2))[0][0]


def list_soft_jaccard_similarity(list_1, list_2):
    intersection_length = sum(sum(jellyfish.jaro_winkler(i, j) for j in list_2) / float(len(list_2)) for i in list_1)
    return float(intersection_length) / (len(list_1) + len(list_2) - intersection_length)


def soft_tfidf_similarity(list_1, list_2):
    soft_tfidf = SoftTfIdf([list_1, list_2])
    return (soft_tfidf.get_raw_score(list_1, list_2))