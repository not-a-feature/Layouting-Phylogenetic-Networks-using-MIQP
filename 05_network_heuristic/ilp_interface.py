#!/usr/bin/python3
"""
Interface for splitstree.
Reads a GML file, calls the solver and writes the output.
Call it in splitstree with:
/path/to/ilp_interface.py /path/to/input/splitstree.gml /path/to/output/ilp.gml

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from docplex_network_heur_obj import solve_tree
import argparse
from Graph import Graph


def main():
    parser = argparse.ArgumentParser(
        description="Reads a GML file, calls the solver and writes the output."
    )
    parser.add_argument("filenames", type=str, nargs=2, help="Inputfile Outputfile")
    args = parser.parse_args()

    input_file = args.filenames[0]
    output_file = args.filenames[1]

    with open(input_file) as f:
        gml = f.read()

    g = Graph(gml=gml)
    g.auto_root()
    g.auto_posx()
    g = solve_tree(g)[-1][0]
    gml = g.get_gmlstring()

    with open(output_file, "w") as f:
        gml = f.write(gml)


if __name__ == "__main__":
    main()
