from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame

from .node import Node

from .utilities import _deserialize_from_data

__all__ = ['Layer']


class Layer:
    """Data structure representing a discrete set of nodes of an model.

    Attributes
    ----------
    nodes : :list:class:`Node`
        Nodes discribing the layer geometry

    trajectory : :class:`compas_fab.robots.JointTrajectory`
        The robot trajectory in joint space

    path : :list: :class:`compas.geometry.Frame`
        The robot tool path in cartesian space

    Examples
    --------

    """

    def __init__(self, nodes=None):
        self.nodes = nodes
        self.trajectory = None

    @classmethod
    def from_nodes(cls, nodes):
        """Class method for constructing a layer from a Node objects.

        Parameters
        ----------
        nodes :list: :class:`Node`
            List of Node objects.
        """
        return cls(nodes)

    @property
    def start_node(self):
        if self.nodes:
            return self.nodes[0]
        else:
            return "No nodes defined"

    @property
    def end_node(self):
        if self.nodes:
            return self.nodes[len(self.nodes)-1]
        else:
            return "No nodes defined"

    @property
    def path(self):
        if self.nodes:
            return [node.frame for node in self.nodes]
        else:
            return "No nodes defined"

    @path.setter
    def path(self, p):
        self.__path = p


    @classmethod
    def from_data(cls, data):
        """Construct an layer from its data representation.

        Parameters
        ----------
        data : :obj:`dict`
            The data dictionary.

        Returns
        -------
        Layer
            The constructed layer.
        """
        layer = cls()
        layer.data = data
        return layer

    def to_data(self):
        """
        docstring
        """
        return self.data

    @property
    def data(self):
        """Returns the data dictionary that represents the layer.

        Returns
        -------
        dict
            The layer data.

        Examples
        --------
        >>> layer = Layer()
        >>> print(layer.data)
        """
        d = dict()

        if self.nodes:
            d['nodes'] = [f.to_data() for f in self.nodes]
        if self.trajectory:
            d['trajectory'] = [f.to_data() for f in self.trajectory]
        if self.path:
            d['path'] = [f.to_data() for f in self.path]

        return d

    @data.setter
    def data(self, data):
        if 'nodes' in data:
            self.nodes = [Node.from_data(d) for d in data['nodes']]
        if 'trajectory' in data:
            self.trajectory = _deserialize_from_data(data['trajectory'])
        if 'path' in data:
            self.path = [Frame.from_data(d) for d in data['path']]

    def transform(self, transformation):
        for n in self.nodes:
            n.transform(transformation)
        pass

    def transformed(self, transformation):
        layer = self.copy()
        layer.nodes = [n.transformed(transformation) for n in layer.nodes]
        return layer

    def copy(self):
        """Returns a copy of this layer.

        Returns
        -------
        Layer
        """
        layer = Layer.from_nodes(self.nodes)
        return layer
