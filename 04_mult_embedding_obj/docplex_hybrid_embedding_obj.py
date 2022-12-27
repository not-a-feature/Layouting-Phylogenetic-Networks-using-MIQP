"""
Automatic ILP implementation using docplex/CPLEX.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de

------------------------

"""
from docplex.mp.model import Model
from docplex.mp.progress import *
from itertools import combinations, permutations
from Graph import Graph
from math import ceil
from typing import List
from copy import deepcopy


def solve_tree(g: Graph, model_name="y-pos", model_setting=None, export=False) -> List[Graph]:
    """
    Input:
        g: Graph object, graph to position
        model_name: string, name of the model
        model_setting: dict, key: name of const/objective, value: bool / regularisation
        export: bool, Export ILP to folder ./lp_output/
    Returns:
        d: Graph object, with y-positions
        obj: float, Score of objective function
    """
    default_model_setting = {
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
        "c_close": 0,  # int, children should be close together
        "p_cent_c": 1,  # int, parents should be centered in between the children
        "min_direct_crossing": 10,  # int, minimize direct crossings
        "min_hybrid_length": 1,  # int, minimize vertical length of hybrid-edges
        # Solve settings
        "dummy_nodes": True,  # Add dummy nodes for multi layer spanning edges
        "time_limit": 20,  # int or None, max time to solve in s
        "verbose": True,  # bool, print model and solving infos
    }

    if model_setting is None:
        model_setting = default_model_setting
    else:
        # Fill missing custom settings with default values
        for setting in default_model_setting.keys():
            if setting not in model_setting:
                model_setting[setting] = default_model_setting[setting]

    # Begin of the  ILP
    model = Model(name=model_name)

    if model_setting["time_limit"] is not None:
        model.set_time_limit(model_setting["time_limit"])

    if model_setting["dummy_nodes"]:
        g.add_dummy_nodes()

    names = g.names()

    tree_layers = g.get_layers()

    # All variables (y-positions to solve)
    model_int_vars = {name: model.integer_var(name=name) for name in names}

    ################################################################################################
    """
    Constraints
    """

    """
    Set lower bound to 0
    """
    for node_name in names:
        model.add_constraint(0 <= model_int_vars[node_name])

    ################################################################################################
    """
    Vertical distance > model_setting["distance_geq"]
    """
    # For evey combination of nodes in one layer/layer of tree
    if model_setting["distance_geq"]:
        for tree_layer in tree_layers.values():
            for name_a, name_b in combinations(tree_layer, 2):
                model.add_constraint(
                    model.abs(model_int_vars[name_a] - model_int_vars[name_b])
                    >= model_setting["distance_geq"]
                )

    ################################################################################################
    """
    Maximum vertical height
    Number of nodes in layer * model_setting["distance_geq"]
    """
    if model_setting["max_height_by_nodes"]:
        max_nodes_per_layer = max((len(s) for s in tree_layers.values())) + 1
        for node_name in names:
            model.add_constraint(
                model_int_vars[node_name]
                <= max_nodes_per_layer
                * model_setting["distance_geq"]
                * model_setting["max_height_factor"]
            )

    ################################################################################################
    """
    Children must withing range to parent.
    c.y <= p.y + num_cildren/2
    c.y >= p.y - num_cildren/2
    """
    if model_setting["c_withing_range"]:
        for node_name in g.nodes:

            children = g.get_children(node_name)
            if children == set():
                continue

            delta_to_parent = ceil(
                len(children)
                * model_setting["distance_geq"]
                * model_setting["c_withing_range_factor"]
                / 2
            )
            mvar_node = model_int_vars[node_name]
            mvar_children = [model_int_vars[c] for c in children]

            for child_var in mvar_children:
                model.add_constraint(child_var <= mvar_node + delta_to_parent)
                model.add_constraint(child_var >= mvar_node - delta_to_parent)

    ################################################################################################
    """
    Don't allow crossing of edges from layer n to n+1.
    Crossing from n to n+k, k ≥ 2 are not affected.
    """
    if model_setting["no_direct_crossing"]:
        for tree_layer in tree_layers.values():
            for node_a_name, node_b_name in combinations(tree_layer, 2):

                mvar_node_a = model_int_vars[node_a_name]
                mvar_node_b = model_int_vars[node_b_name]

                node_a_children = g.get_children(node_a_name)
                node_b_children = g.get_children(node_b_name)

                mvar_children_a = [model_int_vars[c] for c in node_a_children]
                mvar_children_b = [model_int_vars[c] for c in node_b_children]

                for mvar_child_a in mvar_children_a:
                    for mvar_child_b in mvar_children_b:
                        model.add_constraint(
                            model.logical_or(
                                model.logical_and(
                                    mvar_node_a <= mvar_node_b, mvar_child_a <= mvar_child_b
                                ),
                                model.logical_and(
                                    mvar_node_b <= mvar_node_a, mvar_child_b <= mvar_child_a
                                ),
                            ),
                        )
    ################################################################################################
    """
    Don't allow parents of hybrids to be on the same level
    """
    if model_setting["no_horiz_overlap"]:
        for hybrid_name in g.get_hybrids():
            parents = g.get_parents(hybrid_name)

            for parent_a_name, parent_b_name in combinations(parents, 2):
                mvar_parent_a = model_int_vars[parent_a_name]
                mvar_parent_b = model_int_vars[parent_b_name]
                model.add_constraint(model.logical_not(mvar_parent_a == mvar_parent_b))

    ################################################################################################
    """
    Objective Function
    """

    objective = []

    """
    Children close together
    """
    if model_setting["c_close"]:

        obj_c_close = []

        for node_name in names:
            node = g.get_node(node_name)
            children = g.get_children(node_name)
            for child_a_name, child_b_name in combinations(children, 2):
                mvar_child_a = model_int_vars[child_a_name]
                mvar_child_b = model_int_vars[child_b_name]

                obj_c_close.append(mvar_child_a - mvar_child_b)

        objective.append(model_setting["c_close"] * model.sumsq(obj_c_close))

    ################################################################################################
    """
    Parent close to center in between children
    Miminize distance to mean position of children
    """
    if model_setting["p_cent_c"]:

        obj_p_cent_c = []

        for node_name in names:
            node = g.get_node(node_name)
            children = g.get_children(node_name)
            if len(children) == 0:
                continue

            mvar_node = model_int_vars[node_name]
            mvar_children = [model_int_vars[c] for c in children]

            obj_p_cent_c.append(mvar_node - (model.sum(mvar_children) / len(mvar_children)))

        objective.append(model_setting["p_cent_c"] * model.sumsq(obj_p_cent_c))
    ################################################################################################
    """
    Minimise crossing of hybrid edges from layer n to n+1 against regular edges.
    Crossing from n to n+k, k ≥ 2 are not affected.
    """
    if model_setting["min_direct_crossing"]:

        def low(a, b):
            """
            Checks if a < b.
            Returns 0 if true, -1 otherwise.
            """
            return model.max((b - a) - model.abs(b - a), -1)

        obj_min_direct_crossing = []

        for tree_layer in tree_layers.values():
            for node_a_name, node_b_name in permutations(tree_layer, 2):

                mvar_node_a = model_int_vars[node_a_name]
                mvar_node_b = model_int_vars[node_b_name]

                # minimize crossings of hybrid edge againts regular edges.
                node_a_hybrid_children = g.get_hybrid_children(node_a_name)
                node_b_children = g.get_children(node_b_name)

                mvar_hybrid_children_a = [model_int_vars[c] for c in node_a_hybrid_children]
                mvar_children_b = [model_int_vars[c] for c in node_b_children]

                for mvar_hybrid_child_a in mvar_hybrid_children_a:
                    for mvar_child_b in mvar_children_b:
                        """
                        Non-comparision implementation of
                        (a < b and a' < b') or (b < a and b' < a')
                        """
                        q1 = low(mvar_node_a, mvar_node_b) + low(mvar_hybrid_child_a, mvar_child_b)
                        q2 = model.abs(
                            low(mvar_node_b, mvar_node_a) + low(mvar_child_b, mvar_hybrid_child_a)
                        )
                        obj_min_direct_crossing.append((model.abs(q1 + q2) / 2) - 1)

        objective.append(
            model_setting["min_direct_crossing"] * model.sumsq(obj_min_direct_crossing)
        )
    ################################################################################################
    """
    Minimize vertical length of Hybrid-Edges.
    """
    if model_setting["min_hybrid_length"]:
        obj_hybrid_min_length = []

        for e in g.get_hybrid_edges():

            mvar_node = model_int_vars[e.source]
            mvar_children = model_int_vars[e.target]

            obj_hybrid_min_length.append(mvar_node - mvar_children)

        objective.append(model_setting["min_hybrid_length"] * model.sumsq(obj_hybrid_min_length))

    ################################################################################################
    # Sense of objective: minimise
    model.minimize(sum(objective))

    # Export model
    if export:
        model.export_as_lp(path="./lp_output/")

    # Print model infos
    if model_setting["verbose"]:
        model.print_information()

    # Record intermediate solutions
    sol_recorder = SolutionRecorder()
    model.add_progress_listener(sol_recorder)

    # Solve and show output
    model.solve(log_output=model_setting["verbose"], clean_before_solve=True)

    # Return all / the best solution
    solved_graphs = []
    for sol in sol_recorder.iter_solutions():
        y_pos = {}

        for k, v in sol.iter_var_values():
            k = str(k)
            if k in names:
                y_pos[str(k)] = v
        solved_g = deepcopy(g)

        if model_setting["dummy_nodes"]:
            solved_g.remove_dummy_nodes()

        solved_g.set_posy(y_pos)
        solved_graphs.append((solved_g, sol.objective_value))

    model.end()

    return solved_graphs
