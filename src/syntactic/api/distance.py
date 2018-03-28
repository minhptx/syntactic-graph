from syntactic.generation.model import HierarchicalModel


def syntactic_distance(list_1, list_2):
    model_1 = HierarchicalModel(list_1)
    model_1.build_hierarchy()

    model_2 = HierarchicalModel(list_2)
    model_2.build_hierarchy()

    graph_1 = max(model_1.clusters, key=lambda x: len(x.values)).pattern_graph
    graph_2 = max(model_2.clusters, key=lambda x: len(x.values)).pattern_graph

    intersection = graph_1.join(graph_2)

    return intersection.num_edge() * 1.0 / min(graph_1.num_edge(), graph_2.num_edge())

if __name__ == "__main__":
    print(syntactic_distance(['1', '0', '2'], ['10', '11', '12']))