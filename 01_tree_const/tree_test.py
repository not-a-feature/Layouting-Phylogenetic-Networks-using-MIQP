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
from time import time
from collections import defaultdict

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
    "time_limit": 20,  # int or None, max time to solve in s
    "verbose": False,  # bool, print model and solving infos
}


def mass_solve(file_names, settings, index_offset):
    solved_graphs = []
    times = defaultdict(list)

    for i, name in enumerate(file_names):
        i = i + index_offset
        print(f"Processing {name}")
        with open(in_path + name) as f:
            gml = f.read()

        g = Graph(gml=gml)
        # g.auto_root()
        # g.auto_posx()

        startTime = time()
        solutions = solve_tree(g, model_setting=settings)
        timeDiff = time() - startTime

        times[g.size()].append(timeDiff)
        print(g.size(), timeDiff)

        if solutions:
            g, obj_score = solutions[-1]
            obj_score = round(obj_score, 3)
        else:
            g, obj_score = Graph(), "DNF"

        solved_graphs.append((g, f"{name}, obj {obj_score}"))

        if len(solved_graphs) == 16:
            multiplot(solved_graphs, path=out_path + f"t{i-15}-{i}.png")
            print(f"Saved {i-15}-{i}")
            solved_graphs = []

    multiplot(solved_graphs, path=f"{out_path}t{i-len(solved_graphs)+1}-{i}.png")
    for key, val in times.items():
        val = str(val)
        val = val.replace("[", "")
        val = val.replace("]", "")
        print(f"{key}, {val}")


"""
Test 1000 Trees
"""
# in_path = "Trees/unbalanced/"
# file_names = listdir(in_path)
# file_names = natsorted(file_names)

# out_path = "Figures/unbalanced/"
# settings["time_limit"] = 20
# mass_solve(file_names, settings, 0)

in_path = "Trees/balanced/"
file_names = listdir(in_path)
file_names = natsorted(file_names)

out_path = "Figures/balanced/"
settings["time_limit"] = 20
mass_solve(file_names, settings, 0)
