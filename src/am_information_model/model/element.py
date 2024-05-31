from .graph import ExtendedGraph
from compas.geometry import Frame
from compas.datastructures import Mesh
from .utilities import _deserialize_from_data
from .utilities import _serialize_to_data

__all__ = [
    'Element'
]

class Element(ExtendedGraph):
    def __init__(self, name="element", frame=None, **kwargs):
        super(Element, self).__init__(name, **kwargs)
        self.frame = frame
        self._tool_frame = None

        self._source = None
        self._mesh = None

        self.state = False
        self.attributes.update({
            "frame": frame,
            "node_type": name,
            "_last_path": None
        })
        self.attributes.update(kwargs)

    @property
    def __data__(self):
        data = super(Element, self).__data__
        data.update({
            "state": self.state,
            "frame": self.frame.__data__,
            # "_tool_frame": _serialize_to_data(self.tool_frame),
            # "_source": _serialize_to_data(self._source),
            # "_mesh": _serialize_to_data(self._mesh)
        })
        return data

    # @data.setter
    # def data(self, data):
    #     super(Element, self.__class__).data.fset(self, data)
    #     self.state = data.get("state")
    #     if data.get('frame'):
    #         self.frame = Frame.from_data(data.get('frame'))
    #         self.tool_frame = Frame.from_data(data.get('frame'))
    #     if data.get('_source'):
    #         self._source = _deserialize_from_data(data.get('_source'))
    #     if data.get('_mesh'):
    #         self._mesh = Mesh.from_data(data.get('_mesh'))

    @classmethod
    def from_paths(cls, paths):
        element = cls()
        for path in paths:
            element.add_path(path)

    @classmethod
    def __from_data__(cls, data):
        new_element = cls(
            name = data.get("name"),
            frame = Frame.__from_data__(data.get("frame"))
            

        )
        print(data.get("attributes"))
        # new_element.attributes.update(data["attributes"])
        return new_element

    @classmethod
    def from_mesh(cls, mesh, frame):
        element = cls(frame=frame)
        element._source = element._mesh = mesh
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
    def mesh(self):
        """Mesh of the element."""
        if not self._source:
            return None

        if self._mesh:
            return self._mesh

        if isinstance(self._source, Mesh):
            return self._source
        else:
            self._mesh = Mesh.from_shape(self._source)
            return self._mesh
        
    @mesh.setter
    def mesh(self, mesh):
        self._source = self._mesh = mesh

    @property
    def frame(self):
        """Frame of the element."""
        return self._frame

    @frame.setter
    def frame(self, frame):
        if frame is not None:
            self._frame = frame.copy()
        else:
            self._frame = None
    
    @property
    def tool_frame(self):
        """tool frame of the element"""
        if self._tool_frame is None and self.frame is not None:
            self._tool_frame = self.frame.copy()
        return self._tool_frame

    @tool_frame.setter
    def tool_frame(self, frame):
        if frame is not None:
            self._tool_frame = frame.copy()
        else:
            self._tool_frame = None

    @property
    def centroid(self):
        return self._mesh.centroid()

    def paths(self, data=False):
        return self.get_nodes_where({"node_type": "path"}, data, "path")

    def get_path(self, key):
        return self.get_node(key, "path")

    def add_path(self, path, key=None, 
                 parent_path="last", parent_robot="any"):
        self.add_named_node(path, key, parent_path)
    
    def transform(self, T):
        self.frame.transform(T)
        self.tool_frame.transform(T)
        if self._source:
            self._source.transform(T)
        if self._mesh:
            self._mesh.transform(T)
        for key, path in self.paths(data=True):
            path.transform(T)
    
    def transformed(self, T):
        element = self.copy()
        element.transform(T)
        return element