from .graph import ExtendedGraph
from .edge import Edge

from compas.geometry import Frame

__all__ = [
    'Path'
]

class Path(ExtendedGraph):
    def __init__(self, name="path", frame=None, **kwargs):
        super(Path, self).__init__(name=name, *kwargs)
        self.attributes.update({
            "node_type": "path",
            "frame": frame,
            "direction": "clockwise",
            "_last_node" : None
        })

    @property
    def data(self):
        data = {
            "attributes": self.attributes
        }
        return data
    
    @classmethod
    def __from_data__(cls, data):
        path = cls()
        path.attributes.update(data["attributes"])
        return path

    @property
    def frame(self):
        return self.attributes["frame"]

    @frame.setter
    def frame(self, frame):
        self.attributes["frame"] = frame

    @classmethod
    def from_nodes(cls, nodes):
        path = cls(frame=nodes[0].frame)
        path.add_nodes(nodes)
        return path

    def get_edge_length(self, u, v):
        if self.has_edge(u, v, True):
            return self.edge_attribute((u,v),"edge").length
        else:
            return None

    def add_node(self, node, key=None, parent_node="last"):
        if parent_node == "last":
            parent_node = self.get_last_key("node")
        if self.nodes() and key is None:
            key = self.get_next_key(self.nodes(), "node_")
        elif key in self.nodes():
            print("Key already in database, value is overwritten")
        super(Path, self).add_node(key, node=node)
        self.attributes["_last_node"] = key
        if parent_node is not None:
            self.add_edge(parent_node, key)

    def add_edge(self, u, v):
        nu = self.node_attribute(u, "node")
        nv = self.node_attribute(v, "node")
        edge = Edge.from_node_to_node(nu, nv)
        super(Path, self).add_edge(u,v, edge=edge)

    def add_nodes(self, nodes, keys=None):
        if keys is None:
            keys = [None]*len(nodes)
        for node, key in zip(nodes, keys):
            if key in self.nodes():
                print("Key already in database, value is overwritten")
            self.add_node(node, key)

    def transform(self, T):
        for key, node in self.nodes(data=True):
            node["node"].transform(T)
    
    def transformed(self, T):
        path = self.copy()
        path.transform(T)
        return path