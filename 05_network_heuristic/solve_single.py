"""
Reads trees, solves them using different settings and plot the results.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from Graph import Graph
from docplex_network_heur_obj import solve_tree
from multiplot import multiplot
from os import listdir
from natsort import natsorted

settings = {
    # Constraints
    "distance_geq": 1,  # int, mimumum node distance should be ≥ 1
    "max_height_by_nodes": True,  # bool, maximum height is determined by number of nodes
    "max_height_factor": 2,  # float, factor * number of nodes * distance_geq
    "c_withing_range": False,  # bool, children at max distance from parent
    "c_withing_range_factor": 1,  # int, distance factor. max dist: num_cildren/2 * factor
    # bool, don't allow crossing of edges from layer n to n+1.
    "no_direct_crossing": True,
    "no_horiz_overlap": True,  # bool, no overlap of horizontal edges
    # Objectives
    # Relative regularisation parameters
    "c_close": 1,  # int, children should be close together
    "p_cent_c": 2,  # int, parents should be centered in between the children
    "max_dist_gc": 2,  # int, maximize the distance of the center of grandchildren
    "hybrid_cent_lcsa": 1,  # int, lowest common stable ancestor centeres to hybrid
    "min_direct_crossing": 5,  # int, minimize direct crossings
    "min_hybrid_length": 1,  # int, minimize vertical length of hybrid-edges
    # Solve settings
    "dummy_nodes": True,  # Add dummy nodes for multi layer spanning edges
    "tree_based_embedding": True,  # Is the network a tree based embedding
    "time_limit": 300,  # int or None, max time to solve in s
    "verbose": True,  # bool, print model and solving infos
}

tree_file = "Trees/unbalanced/t571.gml"

with open(tree_file) as f:
    gml = f.read()


g = Graph(gml=gml)
g.auto_root()
g.auto_posx()

solutions = solve_tree(g, model_setting=settings)
output = []
last_score = float("-inf")
for i, (g, obj_score) in enumerate(solutions[::-1]):
    # add only solutions which improved by at leastr 0.5
    if obj_score > last_score + 0.5:
        last_score = obj_score
        title = f"{g.size()} Nodes, Solution {i}, Obj {round(obj_score)}"
        output.append((g, title))

output = output[::-1]
print(len(output))
multiplot(output)

# solutions[-1][0].plot()
