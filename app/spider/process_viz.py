import json

import gensim
import networkx as nx
import numpy as np
from sklearn.manifold import TSNE

def get_viz(g, model, perplexity=20):
    """Performs processing for network visualization"""
    nodes = [x for x in model.wv.vocab]
    embeddings = np.array([model.wv[x] for x in nodes])

    tsne_2d = TSNE(n_components=2, random_state=7, perplexity=perplexity)
    embeddings_2d = tsne_2d.fit_transform(embeddings)

    tsne_3d = TSNE(n_components=3, random_state=7, perplexity=perplexity)
    embeddings_3d = tsne_3d.fit_transform(embeddings)

    # For 3d
    nodes_dict = {
        int(id): {
            **g.nodes[int(id)], "fx": np.float64(coords[0]),
            "fy": np.float64(coords[1]), "fz": np.float64(coords[2])
        } for id, coords in zip(nodes, embeddings_3d)
    }

    # What is the third tuple value _ ?
    edges = [
        {"source": nodes_dict[u], "target": nodes_dict[v]} for u, v, _ in g.edges
        ]
    nodes_output_list = sorted(
        list(nodes_dict.values()), key=lambda node: node["id"]
        )
    spider_json_full = {"nodes": nodes_output_list, "links": edges}
    fname = f"app/spider/{dom}.spiderFull.js"
    with open(f"{fname}", "w") as f:
        f.write("spiderJson = ")
        f.write(json.dumps(spider_json_full, indent=2))
        f.write(";")
    print(f"3D layout file saved to {fname}")
