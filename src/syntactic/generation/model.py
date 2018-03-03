import random
from collections import defaultdict

from syntactic.generation.pattern import Graph


class Cluster:
    def __init__(self, values=None, pattern_graph=None):
        if values:
            self.values = values
        else:
            self.values = []

        self.pattern_graph = pattern_graph

    def match_and_join(self, text):
        return self.pattern_graph.match_and_join(text)

    def add_value(self, text):
        self.values.append(text)
        self.pattern_graph.values.append("^" + text + "$")

    @staticmethod
    def generate(seed, cluster_value_list, sim_map):
        print("Generate ...", len(cluster_value_list), cluster_value_list)
        seed_graph = Graph.generate(seed)
        print(seed, cluster_value_list)
        cluster_value_list.remove(seed)
        if cluster_value_list:
            min_sim_sample = min(cluster_value_list, key=lambda x: sim_map[seed][x])
        else:
            return Cluster([seed], seed_graph), []
        min_sim_graph = Graph.generate(min_sim_sample)
        cluster_graph = seed_graph.join(min_sim_graph)

        cluster_value_list.remove(min_sim_sample)

        no_fit_list = []

        for cluster_text in cluster_value_list:
            # print(cluster_text)
            if cluster_graph.match_and_join(cluster_text):
                cluster_graph.values.append("^" + cluster_text + "$")
            else:
                graph = Graph.generate(cluster_text)
                result = cluster_graph.join(graph)
                if result is None:
                    no_fit_list.append(cluster_text)

        return Cluster(cluster_value_list + [seed, min_sim_sample], cluster_graph), no_fit_list


class HierarchicalModel:

    def __init__(self, text_list):
        self.values = text_list
        self.pattern_graph_list = []
        self.clusters = []
        self.intersection_map = defaultdict(lambda: defaultdict(lambda: -1))
        self.graph_map = defaultdict(lambda: -1)
        self.num_edge_map = defaultdict(lambda: 0)
        self.sim_map = defaultdict(lambda: defaultdict(lambda: -1))
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

        uncovered_list = self.values[:]

        while uncovered_list:

            print("Len uncovered", len(uncovered_list))

            pre_cluster_map = defaultdict(lambda: [])

            if len(uncovered_list) > 100:
                text_list = random.sample(uncovered_list, 100)
            else:
                text_list = uncovered_list[:]

            seed_set = self.seed_cluster(text_list)

            print("Text", text_list, seed_set)

            for text in text_list:
                if text in seed_set:
                    pre_cluster_map[text].append(text)
                    uncovered_list.remove(text)
                else:
                    min_seed, min_distance = \
                        max([(x, y) for x, y in self.sim_map[text].items() if x in seed_set], key=lambda x: x[1])
                    if min_seed in text_list and min_distance > 0:
                        pre_cluster_map[min_seed].append(text)
                        uncovered_list.remove(text)

            for seed, cluster_value_list in pre_cluster_map.items():
                cluster, no_fit_list = Cluster.generate(seed, cluster_value_list, self.sim_map)
                self.clusters.append(cluster)
                uncovered_list = uncovered_list + no_fit_list

            remove_list = []

            for text in uncovered_list:
                for cluster in self.clusters:
                    if cluster.match_and_join(text):
                        cluster.add_value(text)
                        remove_list.append(text)
                        break
                else:
                    print(text)
                # print(len(remove_list), len(cluster.pattern_graph.values))

            uncovered_list = [x for x in uncovered_list if x not in set(remove_list)]

        for cluster in self.clusters:
            cluster.pattern_graph = cluster.pattern_graph.simplify()

    def seed_cluster(self, text_list):
        min_sim_list = [-2, -1]
        min_sim = 0

        sample_list = text_list[:]

        seed_set = [sorted(text_list, key=lambda x: len(x))[0]]

        while min_sim < 0.1 or abs(min_sim_list[-2] - min_sim_list[-1]) > 0.1:
            # print(text_list)
            new_seed, min_sim = self.min_sim_sample(sample_list, seed_set)
            min_sim_list.append(min_sim)

            print(min_sim_list, new_seed, seed_set)
            if not new_seed:
                return seed_set
            seed_set.append(new_seed)
            sample_list.remove(new_seed)

        return seed_set[:-2]

    def similarity(self, text_1, text_2, is_cached=True):
        if self.intersection_map[text_1][text_2] != -1:
            graph = self.intersection_map[text_1][text_2]
        else:
            if self.graph_map[text_1] == -1:
                graph_1 = Graph.generate(text_1)
            else:
                graph_1 = self.graph_map[text_1]

            graph_2 = Graph.generate(text_2)

            graph = graph_1.join(graph_2)

            if is_cached:
                self.intersection_map[text_1][text_2] = graph
                self.intersection_map[text_2][text_1] = graph
                self.num_edge_map[text_1] = graph_1.num_edge()
                self.num_edge_map[text_2] = graph_2.num_edge()
                self.graph_map[text_1] = graph_1

        # print("Text", text_1, text_2)

        if not graph:
            # print("No graph")
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
                        # print(anchor, text, self.sim_map[anchor][text])
                        self.sim_map[text][anchor] = self.sim_map[anchor][text]

                # print(text, max_sim)
                if self.sim_map[text][anchor] > max_sim:
                    max_sim = self.sim_map[text][anchor]

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

    graph = graph_1.join(graph_2)
    graph = graph.join(graph_3)
