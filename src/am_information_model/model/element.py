from .graph import ExtendedGraph
from compas.geometry import Frame

__all__ = [
    'Element'
]

class Element(ExtendedGraph):
    def __init__(self, name="element", frame=None, **kwargs):
        super(Element, self).__init__(name, *kwargs)
        self.state = False
        self.attributes.update({
            "frame": frame,
            "_last_path": None
            "connection_ua": None,
            "connection_ub": None,
            "connection_va": None,
            "connection_vb": None,
            "connection_wa": None,
            "connection_wb": None
        })

    @classmethod
    def from_paths(cls, paths):
        element = cls()
        for path in paths:
            element.add_path(path)

    @property
    def frame(self):
        return self.attributes["frame"]

    @frame.setter
    def frame(self, frame):
        self.attributes["frame"] = frame

    def check_state(self):
        pass

    def set_connection_frames(self, connection_frames=None):
        path_0 = self.get_path("path_0")
        self.attributes.update({
            "connection_ua": path_0.get_node("node_0").frame,
            "connection_ub": path_0.get_node(path_0.attributes.get("_last_node")).frame,
            "connection_va": path_0.get_node("node_0").frame,
            "connection_vb": path_0.get_node("node_1").frame,
            "connection_wa": path_0.get_node("node_0").frame,
            "connection_wb": self.get_path(self.attributes.get("_last_path")).get_node("node_0").frame
        })
        if isinstance(connection_frames, dict):
            self.attributes.update(connection_frames)


    def paths(self, data=False):
        return self.get_nodes_where({"node_type": "path"}, data, "path")

    def get_path(self, key):
        return self.get_node(key, "path")

    def add_path(self, path, key=None, 
                 parent_path="last", parent_robot="any"):
        self.add_named_node(path, key, parent_path)
    
    def transform(self, T):
        for key, path in self.paths(data=True):
            path.transform(T)
    
    def transformed(self, T):
        element = self.copy()
        element.transform(T)
        return element