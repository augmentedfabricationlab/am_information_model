from .graph import ExtendedGraph
from .edge import Edge

from compas.geometry import Frame
from .utilities import _deserialize_from_data
from .utilities import _serialize_to_data

__all__ = [
    'Path'
]

class Path(ExtendedGraph):
    def __init__(self, name="path", frame=None, **kwargs):
        super(Path, self).__init__(name, **kwargs)
        self.frame = frame
        self.direction = "clockwise"

        self.attributes["obj_type"] = name
        self.attributes.update(kwargs)

    @property
    def frame(self):
        return self.attributes.get("frame")
    @frame.setter
    def frame(self, frame):
        if isinstance(frame, Frame):
            self.attributes["frame"] = frame
        elif isinstance(frame, dict):
            self.attributes["frame"] = Frame.from_data(frame)

    @classmethod
    def from_path_nodes(cls, nodes):
        path = cls(frame=nodes[0].frame)
        path.add_path_nodes(nodes)
        return path

    def get_edge_length(self, u, v):
        if self.has_edge(u, v, True):
            return self.edge_attribute((u,v),"edge").length
        else:
            return None

    def add_path_node(self, node, key=None):
        nid = self.add_named_node(obj=node, key=key)
        return nid

    def add_edge(self, u, v):
        nu = self.node_attribute(u, "node")
        nv = self.node_attribute(v, "node")
        edge = Edge.from_node_to_node(nu, nv)
        super(Path, self).add_edge(u,v, edge=edge)

    def add_path_nodes(self, nodes, keys=None):
        if keys is None:
            keys = range(len(nodes))
        for i, node in enumerate(nodes):
            if keys[i] in self.path_nodes():
                print("Key already in database, value is overwritten")
            self.add_named_node(obj=node, key=keys[i])

    def path_nodes(self, data=False):
        return self.objects("path_node", data)
    
    def transform(self, T):
        for key, node in self.nodes(data=True):
            node["path_node"].transform(T)
    
    def transformed(self, T):
        path = self.copy()
        path.transform(T)
        return path