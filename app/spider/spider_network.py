import networkx as nx
from node2vec import Node2Vec

from app import db
from app.models import Link


class NodeEmbed():
    "Class to do node embedings"

    def __init__(self):
        self.links = None

    def create_graph(self):
        directed_graph = nx.DiGraph()

        self.links = db.query(Link).with_entities(Link.from_id, Link.to_id)

        for link in links:
            from_id, to_id = link
            directed_graph.add_edge(from_id, to_id)
        
        # Precompute Probabilities and generate walks
        node_vec = Node2Vec(directed_graph)

        # Embed Nodes
        model = node_vec.fit()

        return model
