import networkx as nx, numpy as np
from app import db

def compute_embeddings(url, embedding_dimensions, walk_length=10, num_walks=90, window_size=9):
    res = db.session.execute("SELECT id FROM webs WHERE url = :url", {"url": url})
    rows = res.fetchall()
    if rows == []:
        print("No such domain found")
        return
    web_url = rows[0][0]

    nodes_res = db.session.execute("SELECT id, url, old_rank, new_rank FROM pages WHERE web_id = :wi", {"wi": web_id})
    nodes_db = nodes_res.fetchall()

    links_res = db.session.execute(
        "SELECT from_id, to_id FROM links, pages WHERE from_id = pages.id AND pages.web_id = :wi",
        {"wi": web_id}
        )
    links_db = links_res.fetchall()

    g = nx.MultiDiGraph()
    for node in nodes_db:
        g.add_node(node["id"], url=node[1], old_rank=np.float64(node[2]), new_rank=np.float64(node[3]))
    for edge in links_db:
        g.add_edge(*edge)

    node2vec = Node2Vec(g, dimensions=20, walk_length=walk_length, num_walks=num_walks)

    model = node2vec.fit(window=window_size, min_count=1)
    dom = url.split("/")[2]
    model.save(f"app/spider/{dom}_network.model")
    nx.write_gpickle(g, f"app/spider/{dom}_network.graph")
    print("Graph and corresponding embedding model saved")
    # ... return some stats later
