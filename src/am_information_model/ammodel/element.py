from compas.data import Data
from compas.geometry import Frame
from compas.datastructures import Mesh
from copy import deepcopy

__all__ = [
    'Element'
]

class Element(Data):
    def __init__(self, name=None, frame=None, mesh=None, source=None, **kwargs):
        super().__init__()
        self.name = name
        self.frame = frame
        self.mesh = mesh
        self.source = source
        self.attributes = kwargs


    @property
    def __data__(self):
        return {
            "name": self.name,
            "frame": self.frame,
            "mesh": self.mesh,
            "source": self.source,
            "attributes": self.attributes,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            name=data.get("name"),
            frame=data.get("frame"),
            mesh=data.get("mesh"),
            source=data.get("source"),
            **data.get("attributes", {})
        )

    @classmethod
    def from_mesh(cls, mesh, frame, name=None, **kwargs):
        element = cls(frame=frame, mesh=mesh, source=mesh, name=name, **kwargs)
        return element

    @classmethod
    def from_shape(cls, shape, frame, name=None, **kwargs):
        element = cls(frame=frame, source=shape, name=name, **kwargs)
        element.mesh = Mesh.from_shape(shape)
        return element

    @classmethod
    def from_box(cls, box, name=None, **kwargs):
        return cls.from_shape(box, box.frame, name=name, **kwargs)

    @property
    def centroid(self):
        return self.mesh.centroid()

    def transform(self, T):
        if self.frame:
            self.frame.transform(T)
        if self.source:
            self.source.transform(T)
        if self.mesh:
            self.mesh.transform(T)

    def transformed(self, T):
        element = deepcopy(self)
        element.transform(T)
        return element

    def __repr__(self):
        return f"Element(name={self.name}, frame={self.frame})"

