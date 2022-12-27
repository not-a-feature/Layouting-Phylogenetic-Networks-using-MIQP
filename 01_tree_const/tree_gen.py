"""
Generates 1000x random trees and saves them.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from Graph import Graph, Node, Edge
from random import randint, sample

from math import ceil

out_path = "Trees/"
num_trees = 1000

min_children = 1
max_children = 8
max_nodes = 40


def rand_tree(min_children, max_children, num_nodes):
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

    return g
