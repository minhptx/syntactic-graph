import random
import time
from collections import defaultdict

import pandas as pd
from syntactic.generation.pattern import Graph


class Cluster:
    def __init__(self, text_list=None, pattern_graph=None):
        if text_list:
            self.text_list = text_list
        else:
            self.text_list = []

        self.pattern_graph = pattern_graph

    @staticmethod
    def generate(seed, cluster_value_list):
        cluster_graph = Graph.generate(seed)
        for cluster_text in cluster_value_list:
            cluster_graph = cluster_graph.intersect(Graph.generate(cluster_text))

        return Cluster(cluster_value_list + [seed], cluster_graph)


class HierarchicalModel:

    def __init__(self, text_list):
        self.text_list = text_list
        self.pattern_graph_list = []
        self.clusters = []
        self.graph_map = defaultdict(lambda: defaultdict(lambda: None))
        self.sim_map = defaultdict(lambda: defaultdict(lambda: -1))
        self.nearest_seeds_map = defaultdict(lambda: None)
        self.max_sim = defaultdict(lambda: 0)

    def get_cluster_labels(self):
        cluster_id_list = []
        print(len(self.text_list))
        for text in self.text_list:
            for cluster_id, cluster in enumerate(self.clusters):
                if text in cluster.text_list:
                    cluster_id_list.append(cluster_id)
                    break
        return cluster_id_list

    def build_hierarchy(self):
        pre_cluster_map = defaultdict(lambda: [])

        self.seed_cluster()

        for text, seed in self.nearest_seeds_map.items():
            print(text, seed, self.sim_map[text][seed])
            pre_cluster_map[seed].append(text)

        for seed, cluster_value_list in pre_cluster_map.items():
            self.clusters.append(Cluster.generate(seed, cluster_value_list))

    def seed_cluster(self):

        pre_min_sim = -1
        min_sim = 1
        text_list = self.text_list[:]
        seed_set = [random.choice(self.text_list)]

        text_list.remove(seed_set[0])

        while min_sim == 0 or abs(pre_min_sim - min_sim) > 0.1:
            pre_min_sim = min_sim
            new_seed, min_sim = self.min_sim_sample(text_list, seed_set)
            seed_set.append(new_seed)
            text_list.remove(new_seed)

        return seed_set[:-1], seed_set[-1]

    def similarity(self, text_1, text_2, is_cached=True):
        if text_1 in self.graph_map:
            graph_1 = self.graph_map[text_1]
        else:
            graph_1 = Graph.generate(text_1)
        if text_2 in self.graph_map:
            graph_2 = self.graph_map[text_2]
        else:
            graph_2 = Graph.generate(text_2)

        graph = graph_1.intersect(graph_2)

        if is_cached:
            self.graph_map[text_1] = graph_1
            self.graph_map[text_2] = graph_2

        if not graph:
            return 0

        # print(graph.num_edge(), graph_1.num_edge(), graph_2.num_edge())
        return graph.num_edge() * 1.0 / min(graph_1.num_edge(), graph_2.num_edge())

    def min_sim_sample(self, text_list, anchor_set):
        min_sim = 1
        max_sample = None

        print(anchor_set)

        for text in text_list:
            max_sim = 0
            for anchor in anchor_set:
                # print(anchor, text)
                if text == anchor:
                    self.sim_map[anchor][text] = 1
                if self.sim_map[anchor][text] == -1:
                    self.sim_map[anchor][text] = self.similarity(anchor, text)
                    self.sim_map[text][anchor] = self.sim_map[anchor][text]
                    # print(self.distance_map[anchor][text])

                if self.sim_map[anchor][text] > max_sim:
                    max_sim = self.sim_map[anchor][text]
                    self.nearest_seeds_map[text] = anchor

            self.max_sim[text] = max_sim
            if max_sim < min_sim:
                max_sample = text
                min_sim = max_sim
        return max_sample, min_sim


if __name__ == "__main__":
    df = pd.read_csv("data/input/raw/1st_dimension.csv")
    # value_list = df.iloc[:, 0].values.tolist()
    # print(value_list)
    # model = HierarchicalModel(value_list)
    #
    # start = time.time()
    #
    # print(model.seed_cluster())
    #
    # print(time.time() - start)

    model = HierarchicalModel(None)

    print(model.similarity('3133:72AD:5956:32C2:416B:872F:098F:851B:DDB9:6528:4C6C:BE9A:4F19:0964:30DB:A95A',
                           '3133:72AD:5956:32C2:416B:872F:098F:851B:DDB9:6528:4C6C:BE9A:4F19:0964:30DB:A95A'))
