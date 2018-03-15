class ValidationModel:
    def __init__(self):
        pass

    def validate(self, result_cluster, transformed_cluster):
        if result_cluster.pattern_graph.similar(transformed_cluster.pattern_graph):
            print("Validated")
            return True
        print("Not Validated")
        return False
