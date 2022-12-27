"""
Generates 1000x random trees and saves them.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from Graph import Graph, Node, Edge
from random import randint, sample

from math import ceil
from os import path


def rand_tree(min_children, max_children, num_nodes, balanced=True):
    """
    Generates random tree.

    Input:
            min_children: int, minimum number of children a node must have.
            max_children: int, maximum number of children a node can have.
            num_nodes: int, number of nodes the tree should have.
    """
    g = Graph()
    # Add root node
    root_node = Node(name="0", node_id=0, posx=0, posy=0, dummy=False)
    g.add_node(root_node)
    g.root = "0"

    new_node_name = 0
    layer = 0

    while g.size() < num_nodes:
        last_layer = sorted(g.get_layers().items())[-1][1]
        layer += 1
        for node_name in last_layer:
            for i in range(randint(min_children, max_children)):
                if g.size() < num_nodes:
                    new_node_name += 1
                    new_node = Node(
                        name=str(new_node_name),
                        node_id=new_node_name,
                        posx=layer,
                        posy=0,
                        dummy=False,
                    )
                    g.add_node(new_node)
                    g.add_edge(str(node_name), str(new_node_name), hybrid=False)

                else:
                    break
            if not balanced:
                break

    # add hybrids

    max_hybrid = randint(100 * min_hybrid_percent, 100 * max_hybrid_percent) / 100
    hybrid_edges = 0

    node_names = list(g.names())

    while hybrid_edges / g.size() <= max_hybrid and 4 <= g.size():
        name_a, name_b = sample(node_names, 2)

        pos_a = g.get_node(name_a).posx
        pos_b = g.get_node(name_b).posx

        if 0 < (pos_a - pos_b):
            name_a, name_b = name_b, name_a

        e = Edge(name_a, name_b, hybrid=False)
        if e in g.edges:
            continue

        g.add_edge(name_a, name_b, hybrid=True)
        hybrid_edges += 1

    g.auto_posx()
    return g


if __name__ == "__main__":

    balanced = True

    basePath = path.dirname(path.realpath(__file__))
    if balanced:
        out_path = path.join(basePath, "Trees", "balanced")
    else:
        out_path = path.join(basePath, "Trees", "unbalanced")
    num_trees = 1000

    min_children = 1
    max_children = 8
    max_nodes = 40

    min_hybrid_percent = 0
    max_hybrid_percent = 0.4  # 10 node -> 0.4 -> max 4 hybrids

    sizes = []
    trees_per_step = round(num_trees / max_nodes)
    for i in range(2, max_nodes):
        sizes.extend([i] * trees_per_step)

    trees = []
    for step in sizes:
        trees.append(rand_tree(min_children, max_children, step, balanced=balanced))

    for i, g in enumerate(trees, start=0):

        file_name = path.join(out_path, f"t{i}.gml")
        with open(file_name, "w") as f:
            f.write(g.get_gmlstring())
