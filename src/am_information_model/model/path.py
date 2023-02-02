
from am_information_model.model import ExtendedGraph
from compas.geometry import Frame

__all__ = [
    'Path'
]

class Path(ExtendedGraph):
    def __init__(self, name="path"):
        super(Path, self).__init__(name)
        self._last_node = None
        self.PCF = Frame.worldXY()

    @classmethod
    def from_nodes(cls, nodes):
        path = cls()
        path.add_nodes(nodes)
        return path

    def add_node(self, node, key=None, parent_node="last"):
        if parent_node == "last":
            parent_node = self.get_last_key(node.attributes.get("name"))
        if self.nodes() and key is None:
            key = self.get_next_key(self.nodes(), "node_")
        elif key in self.nodes():
            print("Key already in database, value is overwritten")
        super(Path, self).add_node(key, node=node)
        self._last_node = key
        if parent_node is not None:
            self.add_edge(parent_node, key)

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