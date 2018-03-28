import math
import random
from collections import Counter

import numpy as np
from py_stringmatching import SoftTfIdf, Jaro, Levenshtein
from scipy.stats import ks_2samp
from sklearn.metrics.pairwise import cosine_similarity

from utils import nlp


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


def list_histogram_similarity(string_list1, string_list2):
    hist_1 = sorted(list(Counter([x for x in string_list1 if x]).values()))
    hist_2 = sorted(list(Counter([x for x in string_list2 if x]).values()))
    if not hist_1 or not hist_2:
        return 0
    return ks_2samp(hist_1, hist_2)[1]


def list_total_sim(list_1, list_2):
    w2v_sim = list_w2v_similarity(list_1, list_2)
    cos_sim = list_jaccard_similarity(list_1, list_2)
    # ks_sim = list_histogram_similarity(list_1, list_2)
    return (cos_sim + w2v_sim) / 2


def list_w2v_similarity(list_1, list_2):
    if len(list_1) > 500:
        list_1  = random.sample(list_1, 500)
    if len(list_2) > 500:
        list_2  = random.sample(list_2, 500)
    vec_1 = nlp(" ".join(list_1))
    vec_2 = nlp(" ".join(list_2))

    return vec_1.similarity(vec_2)