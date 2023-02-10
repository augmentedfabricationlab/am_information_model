from .graph import ExtendedGraph
from compas.geometry import Frame

__all__ = [
    'Element'
]

class Element(ExtendedGraph):
    def __init__(self, name="element"):
        super(Element, self).__init__(name)
        self.state = False
        self._last_path = None
        self.ECF = Frame.worldXY()

    def check_state(self):
        pass

    def paths(self, data=False):
        return self.get_nodes_where({"node_type": "path"}, data, "path")

    def get_path(self, key, data=False):
        self.get_node(key, data, "path")

    def add_path(self, path, key=None, 
                 parent_path="last", parent_robot="any"):
        self.add_named_node(path, key, parent_path)
        self._last_path = key