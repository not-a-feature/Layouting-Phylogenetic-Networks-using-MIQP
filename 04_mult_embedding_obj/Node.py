"""
Basic Node / Edge class

@author: Jules Kreuer
@contact: jules.kreuer@uni-tuebingen.de
"""
from collections import Counter
from dataclasses import dataclass


@dataclass
class Edge:
    source: str
    target: str
    hybrid: bool  # true if hybrid-edge

    def __init__(self, source: str, target: str, hybrid: bool):
        self.source = source
        self.target = target
        self.hybrid = hybrid  # true if non hybrid-edge

    def __eq__(self, o):
        return self.target == o.target and self.source == o.source

    def __hash__(self):
        return hash(f"{self.target}_/_{self.source}")

    def gml_edge(self):
        """
        Returns the GML representation of this edge.
        """
        out = f"\tedge [\n\t\tsource {self.source}\n\t\ttarget {self.target}\n"
        if self.hybrid:
            out += "\t\thybrid 1\n"
        out += "\t]\n"
        return out


@dataclass
class Node:
    name: str
    # node_id: None  # unique id of the node, used for gml
    posx: int  # x position of node
    posy: int  # y position of node
    angle: float  # angle of node, used for gml / splitstree
    dummy: bool

    def __init__(
        self,
        name: str = None,
        node_id: str = None,  # unique id of the node, used for gml
        posx: int = None,  # x position of node
        posy: int = None,  # y position of node
        angle: float = None,  # angle of node, used for gml / splitstree
        dummy: bool = False,  # bool, is the node a later-added dummy-node
    ):
        self.name = name
        self.id = node_id
        self.posx = posx
        self.posy = posy
        self.angle = angle
        self.dummy = dummy

    def gml_node(self):
        """
        Returns the GML string representation of this node.
        """
        out = f"\tnode [\n\t\tid {self.id}\n\t\tlabel {self.name}\n"
        if self.posx is not None:
            out += f"""\t\tx "{self.posx}"\n"""
        if self.posy is not None:
            out += f"""\t\ty "{self.posy}"\n"""
        if self.angle is not None:
            out += f"""\t\tangle "{self.angle}"\n"""
        out += "\t]\n"
        return out
