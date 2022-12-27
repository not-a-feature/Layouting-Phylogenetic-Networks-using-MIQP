"""
Graph class that allows different tree operations and parsing from NWK / GML string.

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""

from typing import List
from matplotlib import pyplot as plt
from collections import defaultdict, Counter
from Node import Node, Edge


class Graph:
    def __init__(self, nwk=None, root=None, gml=None, warning=False) -> None:
        self.nodes: dict = {}
        self.edges: set = set()
        self.root: str = root
        self.warning: bool = warning
        self.gml_header: str = """graph [
	comment "Rooted network with node coordinates"
	directed 1
	id 1
	label "Graph" """

        if nwk is not None and gml is not None:
            raise RuntimeError("Can't initialize Graph object with two sources.")

        if nwk is not None:
            self.nwk = nwk
            self.__parse_nwk()

        if gml is not None:
            self.gml = gml
            self.__parse_gml()

    def __str__(self) -> str:
        return f"Graph(Nodes: {self.nodes}, Edges: {self.edges})"

    def get_node(self, name):
        try:
            return self.nodes[name]
        except:
            return None

    def get_parents(self, node_name):
        """Returns a list of names. The parents of the node."""
        return [e.source for e in self.edges if e.target == node_name]

    def get_children(self, node_name, include_hybrid=False):
        """Returns a list of names. The children of the node."""
        return [
            e.target
            for e in self.edges
            if e.source == node_name and (include_hybrid or not e.hybrid)
        ]

    def get_hybrid_children(self, node_name):
        """Returns a list of names. The children of the node that are hybrids."""
        return [e.target for e in self.edges if e.source == node_name and e.hybrid]

    def get_hybrid_edges(self):
        """Returns a list of hybrid-edges."""
        return [e for e in self.edges if e.hybrid]

    def size(self) -> int:
        """Size of the graph. (Number of nodes)"""
        return len(self.nodes)

    def depth(self) -> int:
        """Depth of the graph. (Number of layers)"""
        return int(max(self.nodes.values(), key=lambda n: n.posx).posx)

    def names(self) -> str:
        return self.nodes.keys()

    def add_node(self, node, overwrite=False) -> None:
        """
        Adds a node to the graph.
        Input:
            node: Node, node to add
            overwrite: bool, overwrite potential existing node.
        returns:
            None
        """

        if not overwrite and node.name in self.names():
            raise RuntimeError(
                f"Can't add node with dublicate name to graph\nRelevant node: {node}\nExisting node: {self.get_node(node.name)}"
            )

        self.nodes[node.name] = node

    def remove_node(self, node_name):
        """Removes node from graph, Trows exception if node was not present."""
        self.nodes.pop(node_name)

    def add_edge(self, source: str, target: str, hybrid=None):
        """
        Adds an edge between two nodes.
        Input:
            source: str, name of the source node
            target: str, name of the target node
            hybrid: None / bool, is this a hybrid edge.
                    If none: detect automaticly.
        """

        # Check that all parents / children are present.
        if self.warning:
            if not source in self.names():
                raise RuntimeWarning("Source / Parent not in graph.")
            if not target in self.names():
                raise RuntimeWarning("Target / Child not in graph.")

        if hybrid is None:
            # Checks if new edge is a hybrid edge.
            parents = self.get_parents(target)

            if len(parents) == 0:
                # No existing parents
                hybrid = False
            else:
                hybrid = True

        self.edges.add(Edge(source, target, hybrid))

    def remove_edge(self, source: str, target: str):
        self.edges.remove(Edge(source, target, False))

    def add_dummy_nodes(self, prefix="d_"):
        """
        Adds dummy nodes with in-/outdegree to avoid edges spannig over multiples layers.
        """
        # Don't use self.get_layers().items() as we need to refresh the layer after each step.
        for layer_id in range(self.depth()):
            # Refresh layer after each step
            layer = self.get_layers()[layer_id]
            for node_name in layer:
                node = self.get_node(node_name)
                children = self.get_children(node_name)
                for child_name in children:
                    child = self.get_node(child_name)
                    # If direct child, skip
                    if node.posx + 1 == child.posx:
                        continue
                    self.__add_dummy_between(node_name, child_name, prefix)

    def __add_dummy_between(self, source_name, target_name, prefix):
        """
        Adds dummy node at source level + 1 and updates the child / parent relations.
        """
        source_node = self.get_node(source_name)
        target_node = self.get_node(target_name)

        dummy_name = f"{prefix}_{source_name}_{target_name}"
        dummy_node = Node(
            name=dummy_name,
            posx=source_node.posx + 1,
            dummy=True,
        )

        self.add_node(dummy_node)

        self.remove_edge(source_name, target_name)
        self.add_edge(source_name, dummy_name)
        self.add_edge(dummy_name, target_name, hybrid=False)

    def remove_dummy_nodes(self):
        """Removes all dummy nodes."""
        # Don't use self.get_layers().items() as we need to refresh the layer after each step.
        for layer_id in range(self.depth() + 1):
            # Refresh layer after each step
            layer = self.get_layers()[layer_id]
            for node_name in layer:
                node = self.get_node(node_name)
                if node.dummy:
                    self.__remove_dummy(node_name)

    def __remove_dummy(self, dummy_name):
        """
        Removes dummy node and updates the child / parent relations.
        """
        parents = self.get_parents(dummy_name)

        if not len(parents) == 1:
            RuntimeError("Can't remove dummy node with indegree != 1")

        parent_name = parents[0]
        parent_node = self.get_node(parent_name)

        children = self.get_children(dummy_name)

        if not len(children) == 1:
            RuntimeError("Can't remove dummy node with outdegree != 1")
        child_name = children[0]
        child_node = self.get_node(child_name)

        self.remove_edge(parent_name, dummy_name)
        self.remove_edge(dummy_name, child_name)

        self.remove_node(dummy_name)

        self.add_edge(parent_name, child_name)

    def auto_root(self) -> None:
        """
        Finds the node without parents and sets it as root.
        """
        edge_targets = [e.target for e in self.edges if not e.hybrid]
        root = [n for n in self.names() if not n in edge_targets]

        if not len(root) == 1:
            RuntimeError("Unknown / Multiple root for graph")
        self.root = root[0]

    def auto_posx(self) -> None:
        """
        Only works for rooted trees.
        """
        if self.root is None:
            raise RuntimeError("Can't position nodes without a root")

        def auto_node_posx(node_names, level):
            children = set()

            for name in node_names:
                node = self.get_node(name)
                if node.posx is None or node.posx < level:
                    self.nodes[name].posx = level

                children.update(set(self.get_children(name)))
            if not children == set():
                auto_node_posx(children, level + 1)

        auto_node_posx({self.root}, 0)

    def set_posy(self, pos_dict) -> None:
        """
        Takes a dict of y positions and update the graph
        """
        for name, posy in pos_dict.items():
            self.nodes[name].posy = posy

    def get_layers(self) -> dict:
        """
        Requires posx to be set.
        Returns dict of level (posx): names of this level.
        """

        tree_slices = defaultdict(list)
        for node_name in self.nodes:
            node = self.get_node(node_name)
            tree_slices[node.posx].append(node_name)

        return tree_slices

    def get_hybrids(self) -> set:
        """
        Retuns a set of names that have more than one parent.
        """
        return {e.target for e in self.edges if e.hybrid}

    def get_path(self, name) -> list:
        """
        Returns a lists of the shortest path from the root to a node.
        posx must be set.
        """
        global path_of_node
        path_of_node = {0: []}

        self.__get_path_add_to_list(name, 0)
        return min(path_of_node.values(), key=len)

    def __get_path_add_to_list(self, name, path_id) -> list:
        global path_of_node

        path_of_node[path_id].append(name)
        parents = self.get_parents(name)

        if name == self.root:
            return

        # Don't copy path if only one parent.
        if len(parents) == 1:
            self.__get_path_add_to_list(parents[0], path_id)
        else:
            # For every parent, copy path and follow it.
            for i, parent_name in enumerate(parents, start=1):
                pos_x = self.get_node(name).posx
                parent_pos_x = self.get_node(parent_name).posx

                if pos_x <= parent_pos_x:
                    continue

                new_path_id = path_id + i
                path_of_node[new_path_id] = path_of_node[path_id].copy()
                self.__get_path_add_to_list(parent_name, new_path_id)

    def get_lcsa(self, name):
        """
        Returns the name of the lowest common stable ancestor of a node.
        Does not always procude the correct result.
        Has a horrible runtime.
        """
        pos_x = self.get_node(name).posx

        parents = self.get_parents(name)
        parents = [p for p in parents if self.get_node(p).posx < pos_x]

        if len(parents) <= 1:
            return None

        paths = [self.get_path(p) for p in parents]

        if not all(len(p) == len(paths[0]) for p in paths):
            return None

        for i, pA in enumerate(paths[0]):
            if all(p[i] == pA for p in paths):
                return pA

        return self.root

    def get_gmlstring(self) -> str:
        """
        Returns the GML representation of the graph.
        """
        nodes_string = self.gml_header + "\n"

        for node in self.nodes.values():
            nodes_string += node.gml_node()

        edges_string = ""
        for edge in self.edges:
            edges_string += edge.gml_edge()

        return nodes_string + edges_string + "\n]"

    def plot(self, title=None, path=None):
        """
        Plots the graph.
        """

        for node in self.nodes.values():
            # Draws the node label
            plt.text(node.posx, node.posy, node.name, fontsize=17)

        # Draws the edge
        for edge in self.edges:
            if edge.hybrid:
                color = "orange"
            else:
                color = "black"

            parent = self.get_node(edge.source)
            child = self.get_node(edge.target)
            plt.plot([parent.posx, child.posx], [parent.posy, child.posy], color=color)

        if title is not None:
            plt.title(title)

        if path is not None:
            plt.savefig(path)
            return

        plt.show()

    def __parse_nwk(self):
        """
        Parses newick string.
        """
        self.nwk = self.nwk.strip(";").replace("\n", "")
        self.root = self.nwk.split(")")[-1]

        self.__parse_nwk_node(self.nwk)

    def __parse_nwk_node(self, nwk: str):
        """
        Parse newick string, all nodes must be labeled, no edgelength.
        """

        # Leaf
        if "," not in nwk and "(" not in nwk:
            self.add_node(Node(name=nwk), overwrite=True)
            return

        # Internal / Root
        # Split a last )
        nwk_rev_split = nwk[::-1].split(")", 1)
        # Name of highest node
        name = nwk_rev_split[0][::-1].strip()

        children_nwk = nwk_rev_split[1][::-1][1:]

        # List of nwk substring for each children
        children = self.__bracket_split(children_nwk)

        # Name of each children
        children_names = {nwk.split(")")[-1] for nwk in children}

        # Create current node with name of children
        self.add_node(Node(name=name), overwrite=True)
        for child_name in children_names:
            self.add_edge(name, child_name)

        # Parse children recursivly
        for nwk in children:
            self.__parse_nwk_node(nwk)

    def __bracket_split(self, nkw):
        """
        Splits a string a "," if and only if it is not enclosed by brackets.
        Input:
            nwk: str, string to split.
        Returns:
            splits: List[str], list of substrings.
        """
        splits = []
        level = 0
        next_split = []
        for c in nkw:
            if c == "," and level == 0:
                splits.append("".join(next_split))
                next_split = []
            else:
                if c == "(":
                    level += 1
                elif c == ")":
                    level -= 1
                next_split.append(c)
        splits.append("".join(next_split))
        return splits

    def __parse_gml(self):
        """
        Parses a Graph Markup Language string.
        """
        gml_split = self.gml.split("node [", 1)
        self.gml_header = gml_split[0].rstrip()

        gml_data = "node [" + gml_split[1]
        gml_data = gml_data.split("]")
        for element in gml_data:
            element = element.strip()
            if element == "":
                continue
            if element.startswith("node"):
                self.__parse_gml_node(element)
            elif element.startswith("edge"):
                self.__parse_gml_edge(element)
            else:
                raise RuntimeError(f"Unknown GML element: {element}")

    def __parse_gml_node(self, gml):
        """
        Takes a GML Node element and adds it to the graph.
        """
        node_dict = {"id": None, "label": None, "x": 0.0, "y": 0.0, "angle": "None"}

        for l in gml.split("\n")[1:]:
            l = l.strip().split(" ", 1)
            value = l[1].strip().strip('"').strip("'")
            if not value.lower() == "none":
                node_dict[l[0].strip()] = value
        # Check if all fields are set

        if node_dict["label"] is None:
            node_dict["label"] = node_dict["id"]

        if any(v is None for v in node_dict.values()):
            raise RuntimeError(f"Incomplete Node data: {node_dict}")

        node = Node(
            name=node_dict["label"],
            node_id=int(node_dict["id"]),
            posx=float(node_dict["x"]),
            posy=float(node_dict["y"]),
            angle=node_dict["angle"],
        )

        self.add_node(node)

    def __parse_gml_edge(self, gml):
        """
        Takes a GML Edge element and adds it to the graph.
        """
        edge_dict = {"source": None, "target": None, "hybrid": False}

        for l in gml.split("\n")[1:]:
            l = l.strip().split(" ", 1)
            edge_dict[l[0].strip()] = l[1].strip()

        # Check if all fields are set
        if any(v is None for v in edge_dict.values()):
            raise RuntimeError(f"Incomplete Edge data: {edge_dict}")

        self.add_edge(edge_dict["source"], edge_dict["target"], hybrid=edge_dict["hybrid"])
