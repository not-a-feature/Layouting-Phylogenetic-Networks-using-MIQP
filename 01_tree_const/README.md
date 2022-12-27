# Solving Trees using Constraints.
This subproject solves the y positioning of trees using constraints.

# Files
## docplex_tree.py
Takes any tree with and solves the y-positions using Docplex/CPLEX.

## Graph.py
Graph structure and parser.

## ilp_interface.py
Interface for splitstree.
Reads a GML file, calls the solver and writes the output.
Call it in splitstree with: `/path/to/ilp_interface.py /path/to/input/splitstree.gml /path/to/output/ilp.gml`

## multiplot.py
Plots multiple trees with title in one figure.

## Node.py
Simple node / edge class.

## perf_gridsearch.py
Performes a gridsearch on medium sized trees, to measure the fastest parameter combination.

## solve_single.py
Solves a single tree and plots the result. Used for dev-purposes.

## tree_gen.py
Generates 1000x random trees with horizontal hybrids and saves them.

## tree_test.py
Reads trees, solves them using different settings and plot the result.

# Folders
## Figures
Plots of balanced and unbalaced trees produces by tree_test.py

## perf_1000_trees
Time measurements of tree_test.py run. Time so solve a balanced / unbalanced tree with up to 40 nodes.

## perf_gridsearch
Time measurements of perf_gridsearch.py to find the fastest parameter combination.

## Trees
GML files of balanced and unbalance trees.

# ILP Objectives / Constraints

## Constraints
Following constraints can be de / activated using the model_setting

### Vertical distance
Nodes in each layer must have a minimal distance of model_setting["distance_geq"]:

### Maximum vertical height
Maximum vertical height is determined by the maximum number of nodes in a Layer.

### Children must withing range to parent
Children must be within number_of_children/2 of parent

### No direct crossing
Don't allow crossing of edges from layer n to n+1. Crossing from n to n+k, k ≥ 2 are not affected.

## Objective
Following objectives can be de / activated ($\lambda \neq 0$ or $\lambda > 0$).

### Children close together
- The children of a node shall be close together. For every combination of children A, B:

### Parent close to center in between children
- The distance of the parent node to the vertical center of its direct children shall be minimised.