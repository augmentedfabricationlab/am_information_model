
from compas.data import Data
from compas.geometry import Vector

__all__ = [
    'Edge'
]


class Edge(Data):
    
    DATASCHEMA = {
        "type": "object",
        "properties": {
            "attributes": {"type": "object"},
        },
        "required": [
            "attributes",
        ],
    }

    def __init__(self, u=None, v=None, name="edge", vector=None, **kwargs):
        super(Edge, self).__init__()
        self.name = name
        self.attributes = {
            "obj_type": name,
            "u": u,
            "v": v,
            "vector": vector,
        }
        self.attributes.update(kwargs)
    
    @property
    def __data__(self):
            return self.attributes
    
    @property
    def u(self):
        return self.attributes.get("u")
    
    @property
    def v(self):
        return self.attributes.get("v")

    @classmethod
    def from_node_to_node(cls, node_0, node_1):
        vec = Vector.from_start_end(node_0.frame.point, node_1.frame.point)
        return cls(vector=vec)

    @property
    def length(self):
        if isinstance(self.vector, Vector):
            return self.vector.length
        return None

    @property
    def vector(self):
        return self.attributes.get("vector")
    
    @vector.setter
    def vector(self, vector):
        self.attributes["vector"] = vector
    