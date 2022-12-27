"""
Performes a gridsearch on medium sized trees, to measure the fastest parameter combination.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""
from Graph import Graph
from docplex_tree import solve_tree
from multiplot import multiplot
from itertools import product
from time import time
from copy import deepcopy
from os import path


basePath = path.dirname(path.realpath(__file__))
# Load trees
tree_files = [path.join(basePath, "Trees", "balanced", f"t{i}.gml") for i in range(100, 300)]

trees = []
for tree in tree_files:
    with open(tree, "r") as f:
        gml = f.read()
        g = Graph(gml=gml)
        g.auto_root()
        g.auto_posx()

        trees.append(g)

# Set default settings explicitly
settings = {
    # Constraints
    "distance_geq": 1,  # int, mimumum node distance should be ≥ 1
    "max_height_by_nodes": True,  # bool, maximum height is determined by number of nodes
    "max_height_factor": 2,  # float, factor * number of nodes * distance_geq
    "c_withing_range": True,  # bool, children at max distance from parent
    "c_withing_range_factor": 1,  # int, distance factor. max dist: num_cildren/2 * factor
    # bool, don't allow crossing of edges from layer n to n+1.
    "no_direct_crossing": True,
    # Objectives
    # Relative regularisation parameters
    "c_close": 0,  # int, children should be close together
    "p_cent_c": 1,  # int, parents should be centered in between the children
    # Solve settings
    "time_limit": 20,  # int or None, max time to solve in s
    "verbose": False,  # bool, print model and solving infos
}


time_measurements = {}
for grid_pos in product([True, False], repeat=2):
    # Adapt settings for each grid-point
    settings["max_height_by_nodes"] = grid_pos[0]  # bool, maximum height
    settings["c_withing_range"] = grid_pos[1]  # bool, children at max distance from parent

    # Measure time for each tree
    times = []
    for tree in trees:

        new_g = deepcopy(tree)
        startTime = time()

        sol = solve_tree(new_g, model_setting=settings)
        if sol:
            times.append(time() - startTime)

    time_measurements[grid_pos] = times
    print("Done: ", grid_pos, times)

print("##########################")

for key, val in time_measurements.items():
    key = str(key)
    key = key.replace("True", "T")
    key = key.replace("False", "F")
    key = key.replace(",", "")
    key = key.replace("(", "")
    key = key.replace(")", "")

    val = str(val)
    val = val.replace("[", "")
    val = val.replace("]", "")

    print(f"{key}, {val}")
