# Solving networks.
This subproject solves the y positioning networks.
Constraints are applied on the tree backbone.
Dummy nodes are introduces to split edges spanning multiple layers.

# Files
## docplex_network_heur_obj.py
Takes any networks and solves the y-positions using Docplex/CPLEX.

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

### Parents of hybrids not on same level
Don't allow parents of hybrids to be on the same level (y-pos) to avoid P1 -- P2 == H

## Objective
Following objectives can be de / activated ($\lambda \neq 0$ or $\lambda > 0$).

### Children close together
- The children of a node shall be close together. For every combination of children A, B:

### Parent close to center in between children
- The distance of the parent node to the vertical center of its direct children shall be minimised.

### Maximise distance of grandchildren.
- Maximise distance of group of siblings.

### Center hybrids to LCSA.
- Minimise the distance of a hybrid-node to its last common stable ancestor.

### Minimise hybrid legth.
- Minimise length of hybid edges.

### Minimise crossing of edges.
- Minimise the number of edges that cross. Computational heavy objective.