import random
from collections import defaultdict

import pandas as pd
import time

from syntactic.generation.pattern import Graph


class HierarchicalModel:
    MAX_DISTANCE = 10000

    def __init__(self, text_list):
        self.text_list = text_list
        self.pattern_graph_list = []
        self.clusters = []
        self.graph_map = defaultdict(lambda: defaultdict(lambda: None))
        self.distance_map = defaultdict(lambda: defaultdict(lambda: -1))
        self.min_distance_map = defaultdict(lambda: 0)

    def build_hierarchy(self):
        seed_set, anchor = self.seed_cluster()

        min_seed = None
        min_dist = HierarchicalModel.MAX_DISTANCE
        for seed in seed_set:
            if self.distance_map[seed][anchor] < min_dist:
                min_dist = self.distance_map[seed][anchor]
                min_seed = seed

        uncovered_list = self.text_list[:]

        while uncovered_list:
            graph = self.graph_map[min_seed][anchor]

            cluster = [min_seed, anchor]
            uncovered_list.remove(min_seed)
            uncovered_list.remove(anchor)

            for text in uncovered_list:
                if text in seed_set:
                    continue
                elif graph.is_matched(text):
                    cluster.append(text)
                    uncovered_list.remove(text)
                else:
                    pass

    def seed_cluster(self):

        pre_max_dist = -1
        max_dist = 0
        text_list = self.text_list[:]
        seed_set = [random.choice(self.text_list)]

        text_list.remove(seed_set[0])

        while max_dist == HierarchicalModel.MAX_DISTANCE or abs(pre_max_dist - max_dist) > 0.1:
            pre_max_dist = max_dist
            new_seed, max_dist = self.max_dist_sample(text_list, seed_set)
            print(new_seed, max_dist)
            seed_set.append(new_seed)
            text_list.remove(new_seed)

        return seed_set[:-1], seed_set[-1]

    def dissimilarity(self, text_1, text_2):
        if text_1 in self.graph_map:
            graph_1 = self.graph_map[text_1]
        else:
            graph_1 = Graph.generate(text_1)
        if text_2 in self.graph_map:
            graph_2 = self.graph_map[text_2]
        else:
            graph_2 = Graph.generate(text_2)

        graph = graph_1.intersect(graph_2)

        self.graph_map[text_1][text_2] = graph
        self.graph_map[text_2][text_1] = graph

        if not graph:
            return HierarchicalModel.MAX_DISTANCE

        return 2 - graph.num_edge() * 1.0 / min(graph_1.num_edge(), graph_2.num_edge())

    def max_dist_sample(self, text_list, anchor_set):
        max_dist = 0
        max_sample = None

        print(anchor_set)

        for text in text_list:
            min_dist = HierarchicalModel.MAX_DISTANCE
            for anchor in anchor_set:
                # print(anchor, text)
                if text == anchor:
                    continue
                if self.distance_map[anchor][text] == -1:
                    self.distance_map[anchor][text] = self.dissimilarity(anchor, text)
                    self.distance_map[text][anchor] = self.dissimilarity(anchor, text)
                    # print(self.distance_map[anchor][text])

                if self.distance_map[anchor][text] < min_dist:
                    min_dist = self.distance_map[anchor][text]

            self.min_distance_map[text] = min_dist
            if min_dist > max_dist:
                max_sample = text
                max_dist = min_dist
        return max_sample, max_dist


if __name__ == "__main__":
    df = pd.read_csv("data/input/raw/1st_dimension.csv")
    value_list = df.iloc[:, 0].values.tolist()
    print(value_list)
    model = HierarchicalModel(value_list)

    start = time.time()

    print(model.seed_cluster())

    # print(time.time() - start)
    #
    # graph_1 = Graph.generate('6.75" H x 14.5" W x 0.3125" D')
    # graph_2 = Graph.generate('33 x 25"')
    #
    # graph = graph_1.intersect(graph_2)
    # print(graph.num_edge())
