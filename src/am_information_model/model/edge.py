
from compas.datastructures import Datastructure
from compas.geometry import Vector

__all__ = [
    'Edge'
]


class Edge(Datastructure):
    def __init__(self, name="edge", vector=None, **kwargs):
        super(Edge, self).__init__()
        self._vector = None
        self.vector = vector
        self.key = None
        self.attributes= {
            "name" : name
        }

    @classmethod
    def from_node_to_node(cls, node_0, node_1):
        vec = Vector.from_start_end(node_0.frame.point, node_1.frame.point)
        return cls(vector=vec)

    @property
    def length(self):
        return self.vector.length

    @property
    def vector(self):
        if not self._vector:
            self._vector = None
        return self._vector
    
    @vector.setter
    def vector(self, vector):
        self._vector = vector

    @property
    def data(self):
        data = {
            "attributes": self.attributes,
            "key": self.key,
            "vector": self.vector.data
        }
        return data
    
    @data.setter
    def data(self, data):
        self.attributes.update(data["attributes"] or {})
        self.key = data["key"]
        self.vector.data = data["vector"]
    