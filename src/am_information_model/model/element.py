from .graph import ExtendedGraph
from compas.geometry import Frame
from compas.datastructures import Mesh

__all__ = [
    'Element'
]

class Element(ExtendedGraph):
    def __init__(self, name="element", frame=None, **kwargs):
        super(Element, self).__init__(name, **kwargs)
        self.frame = frame
        self.tool_frame = frame

        self.attributes["obj_type"] =  name
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

    @property
    def mesh(self):
        return self.attributes.get("mesh")
    @mesh.setter
    def mesh(self, mesh):
        if isinstance(mesh, Mesh):
            self.attributes["mesh"] = mesh
        elif isinstance(mesh, dict):
            self.attributes["mesh"] = Mesh.from_data(mesh)
    
    @property
    def source(self):
        return self.attributes.get("source")
    @source.setter
    def source(self, source):
        self.attributes["source"] = source
            
    
    @classmethod
    def from_paths(cls, paths):
        element = cls()
        for path in paths:
            element.add_path(path)

    @classmethod
    def from_mesh(cls, mesh, frame):
        element = cls(frame=frame)
        element.source = element.mesh = mesh
        return element

    @classmethod
    def from_shape(cls, shape, frame):
        element = cls(frame=frame)
        element._source = shape
        element._mesh = Mesh.from_shape(element._source)
    
    @classmethod
    def from_box(cls, box):
        """Construct an element from a box primitive.

        Parameters
        ----------
        box : :class:`compas.geometry.Box`
            Box primitive describing the element.

        Returns
        -------
        :class:`Element`
            New instance of element.
        """
        return cls.from_shape(box, box.frame)

    @property
    def centroid(self):
        return self._mesh.centroid()

    def paths(self, data=False):
        return self.objects("path", data)

    def get_path(self, key):
        return self.get_node(key, "path")

    def add_path(self, path, key=None):
        pid = self.add_named_node(obj=path, key=key)
        return pid
    
    def transform(self, T):
        self.frame.transform(T)
        if self.tool_frame:
            self.tool_frame.transform(T)
        if self.source:
            self.source.transform(T)
        if self.mesh:
            self.mesh.transform(T)
        for key, path in self.paths(data=True):
            path.transform(T)
    
    def transformed(self, T):
        element = self.copy()
        element.transform(T)
        return element

