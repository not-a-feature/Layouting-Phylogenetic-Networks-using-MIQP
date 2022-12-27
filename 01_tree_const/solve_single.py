"""
Reads trees, solves them using different settings and plot the results.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from Graph import Graph
from docplex_tree import solve_tree
from multiplot import multiplot
from os import listdir
from natsort import natsorted
from tree_gen import rand_tree

settings = {
    # Constraints
    "distance_geq": 1,  # int, mimumum node distance should be ≥ 1
    "max_height_by_nodes": True,  # bool, maximum height is determined by number of nodes
    "max_height_factor": 2,  # float, factor * number of nodes * distance_geq
    "c_withing_range": False,  # bool, children at max distance from parent
    "c_withing_range_factor": 1,  # int, distance factor. max dist: num_cildren/2 * factor
    # bool, don't allow crossing of edges from layer n to n+1.
    "no_direct_crossing": True,
    # Objectives
    # Relative regularisation parameters
    "c_close": 0,  # int, children should be close together
    "p_cent_c": 1,  # int, parents should be centered in between the children
    # Solve settings
    "time_limit": None,  # int or None, max time to solve in s
    "verbose": True,  # bool, print model and solving infos
}

g = rand_tree(1, 4, 40)

# tree_file = "Trees/t25.gml"

# with open(tree_file) as f:
#    gml = f.read()


# g = Graph(gml=gml)
g.auto_root()
g.auto_posx()

solutions = solve_tree(g, model_setting=settings)
print(solutions)

# multiplot(solutions)
solutions[-1][0].plot()
