import random
from collections import defaultdict

from syntactic.generation.pattern import Graph


class Cluster:
    def __init__(self, text_list=None, pattern_graph=None):
        if text_list:
            self.text_list = text_list
        else:
            self.text_list = []

        self.pattern_graph = pattern_graph

    @staticmethod
    def generate(seed, cluster_value_list, sim_map):
        # print("Cluster list", cluster_value_list, seed)
        seed_graph = Graph.generate(seed)
        if cluster_value_list:
            min_sim_sample = min(cluster_value_list, key=lambda x: sim_map[seed][x])
        else:
            return Cluster([seed], seed_graph)
        # print(min_sim_sample)
        min_sim_graph = Graph.generate(min_sim_sample)
        cluster_graph = seed_graph.intersect(min_sim_graph)

        # print("Cluster Graph", cluster_graph)

        for cluster_text in cluster_value_list:
            if "^" + cluster_text + "$" in cluster_graph.values or cluster_graph.is_matched(cluster_text):
                continue
            else:
                graph = Graph.generate(cluster_text)
                result = cluster_graph.intersect(graph)
                if result:
                    cluster_graph = result
                else:
                    result =  seed_graph.intersect(graph)
                    cluster_graph = cluster_graph.intersect(result)

        return Cluster(cluster_value_list + [seed], cluster_graph)


class HierarchicalModel:

    def __init__(self, text_list):
        self.values = text_list
        self.pattern_graph_list = []
        self.clusters = []
        self.intersection_map = defaultdict(lambda: defaultdict(lambda: -1))
        self.graph_map = defaultdict(lambda: -1)
        self.num_edge_map = defaultdict(lambda: 0)
        self.sim_map = defaultdict(lambda: defaultdict(lambda: -1))
        self.nearest_seeds_map = defaultdict(lambda: None)
        self.max_sim = defaultdict(lambda: 0)

    def get_cluster_labels(self):
        cluster_id_list = []
        # print(len(self.text_list))

        for text in self.values:
            for cluster_id, cluster in enumerate(self.clusters):
                if text in cluster.text_list:
                    cluster_id_list.append(cluster_id)
                    break
            else:
                cluster_id_list.append(-1)
        return cluster_id_list

    def build_hierarchy(self, num_cluster=100):
        pre_cluster_map = defaultdict(lambda: [])

        seed_set = self.seed_cluster(num_cluster)

        covered_list = self.values[:]

        while covered_list:
            text_list = random.sample(covered_list, 100)
            self

            for seed in seed_set:
                text_list.remove(seed)

            for text in text_list:
                if text not in self.nearest_seeds_map:
                    pre_cluster_map[text] = []
                else:
                    pre_cluster_map[self.nearest_seeds_map[text]].append(text)

            # print(pre_cluster_map)

            for seed, cluster_value_list in pre_cluster_map.items():
                self.clusters.append(Cluster.generate(seed, cluster_value_list, self.sim_map))

            for text in text_list:


    def seed_cluster(self, num_cluster):

        pre_min_sim = -1
        min_sim = 0
        text_list = self.values[:]

        print(self.values)
        seed_set = [sorted(self.values, key=lambda x: len(x))[0]]


        while min_sim == 0 or (abs(pre_min_sim - min_sim) > 0.2 and min_sim < 0.8):
            # print(pre_min_sim, min_sim)
            pre_min_sim = min_sim
            new_seed, min_sim = self.min_sim_sample(text_list, seed_set)
            print("Seed", new_seed, min_sim, seed_set, pre_min_sim)
            if new_seed in seed_set or not new_seed:
                return seed_set
            seed_set.append(new_seed)
            text_list.remove(new_seed)
        return seed_set[:-1]

    def similarity(self, text_1, text_2, is_cached=True):
        if self.intersection_map[text_1][text_2] != -1:
            graph = self.intersection_map[text_1][text_2]
        else:
            if self.graph_map[text_1] == -1:
                graph_1 = Graph.generate(text_1)
            else:
                graph_1 = self.graph_map[text_1]

            graph_2 = Graph.generate(text_2)

            graph = graph_1.intersect(graph_2)

            if is_cached:
                self.intersection_map[text_1][text_2] = graph
                self.intersection_map[text_1][text_2] = graph
                self.num_edge_map[text_1] = graph_1.num_edge()
                self.num_edge_map[text_2] = graph_2.num_edge()
                self.graph_map[text_1] = graph_1

        if not graph:
            return 0

        if self.num_edge_map[text_1]:
            num_edge_1 = self.num_edge_map[text_1]
        else:
            num_edge_1 = Graph.generate(text_1).num_edge()

        if self.num_edge_map[text_2]:
            num_edge_2 = self.num_edge_map[text_2]
        else:
            num_edge_2 = Graph.generate(text_2).num_edge()

        # print(graph.num_edge(), num_edge_1, num_edge_2)
        return graph.num_edge() * 1.0 / min(num_edge_1, num_edge_2)

    def min_sim_sample(self, text_list, anchor_set):
        # print("Sampling")
        min_sim = 1
        max_sample = None

        for text in text_list:
            max_sim = 0
            for anchor in anchor_set:
                if text == anchor:
                    self.sim_map[anchor][text] = 1
                else:
                    if self.sim_map[anchor][text] == -1:
                        self.sim_map[anchor][text] = self.similarity(anchor, text, is_cached=True)
                        self.sim_map[text][anchor] = self.sim_map[anchor][text]
                    # print(self.distance_map[anchor][text])

                if self.sim_map[anchor][text] > max_sim:
                    max_sim = self.sim_map[anchor][text]
                    # if self.sim_map[anchor][text] > 0:
                    self.nearest_seeds_map[text] = anchor

            self.max_sim[text] = max_sim
            if max_sim < min_sim:
                max_sample = text
                min_sim = max_sim
        return max_sample, min_sim


if __name__ == "__main__":
    # df = pd.read_csv("data/input/raw/1st_dimension.csv")
    # value_list = df.iloc[:, 0].values.tolist()
    # print(value_list)
    # model = HierarchicalModel(value_list)
    #
    # start = time.time()
    #
    # print(model.seed_cluster())
    #
    # print(time.time() - start)

    model = HierarchicalModel("")
    graph_1 = Graph.generate(u'Male')
    graph_2 = Graph.generate(u'Undetermined')
    graph_3 = Graph.generate(u"Male")

    graph = graph_1.intersect(graph_2)
    graph = graph.intersect(graph_3)
