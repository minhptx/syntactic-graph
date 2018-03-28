import random
from collections import Counter

from scipy.stats import ks_2samp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score
from sklearn.metrics.pairwise import cosine_similarity

from utils import nlp


def jaccard(x, y):
    try:
        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        union_cardinality = len(set.union(*[set(x), set(y)]))
        return intersection_cardinality / float(union_cardinality)
    except:
        return 0


def tfidf_cosine(list_1, list_2):
    try:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_vectorizer.fit([" ".join(list_1), " ".join(list_2)])
        tfidf_list_1 = tfidf_vectorizer.transform(list_1)
        tfidf_list_2 = tfidf_vectorizer.transform(list_2)
        return cosine_similarity(tfidf_list_1, tfidf_list_2)[0][0]
    except:
        return 0


def ks(string_list1, string_list2):
    min_length = min(len(string_list1), len(string_list2))
    string_list1 = string_list1[:min_length]
    string_list2 = string_list2[:min_length]
    return normalized_mutual_info_score(string_list1, string_list2)


def w2v_cosine(list_1, list_2):
    if len(list_1) > 200:
        list_1 = random.sample(list_1, 200)
    if len(list_2) > 200:
        list_2 = random.sample(list_2, 200)
    vec_1 = nlp(" ".join(list_1))
    vec_2 = nlp(" ".join(list_2))

    return vec_1.similarity(vec_2)
