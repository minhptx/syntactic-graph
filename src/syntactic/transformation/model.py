class TransformationModel:
    def __init__(self, raw_graph, transformed_graph):
        self.model = None
        self.raw_graph = raw_graph
        self.transformed_graph = transformed_graph

    def generate_program(self):
        raw_paths = self.raw_graph.to_paths()
        transformed_paths = self.transformed_graph.to_paths()




