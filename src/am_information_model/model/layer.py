from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame
from compas.datastructures import Network

from .node import Node

from .utilities import _deserialize_from_data

__all__ = ['Layer']


class Layer:
    """Data structure representing a discrete set of nodes of an model.

    Attributes
    ----------
    network : :class:`compas.Network`, optional
    nodes : :list:class:`Node`, optional
        Nodes discribing the layer geometry
    attributes : dict, optional
        User-defined attributes of the model.
        Built-in attributes are:
        * name (str) : ``'Layer'``
    trajectory : :class:`compas_fab.robots.JointTrajectory`
        The robot trajectory in joint space
    path : :list: :class:`compas.geometry.Frame`
        The robot tool path in cartesian space

    Examples
    --------

    """

    def __init__(self, nodes=None, attributes=None, edges=None):
        self.network = Network()
        self.network.attributes.update({'name': 'Layer'})
        self.is_constructed = False

        if attributes is not None:
            self.network.attributes.update(attributes)
        
        if nodes:
            for node in nodes:
                self.add_node(node)

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
    def name(self):
        """str : The name of the layer."""
        return self.network.attributes.get('name', None)

    @name.setter
    def name(self, value):
        self.network.attributes['name'] = value
    
    def number_of_nodes(self):
        return self.network.number_of_nodes()
    
    def number_of_edges(self):
        return self.network.number_of_edges()

    def node(self, key, data=False):
        if data:
            return self.network.node[key]['node'], self.network.node[key]
        else:
            return self.network.node[key]['node']

    def nodes(self, data=False):
        if data:
            for vkey, vattr in self.network.nodes(True):
                yield vkey, vattr['node'], vattr
        else:
            for vkey in self.network.nodes(data):
                yield vkey, self.network.node[vkey]['node']

    def edges(self, data=False):
        return self.network.edges(data)

    @property
    def path(self):
        return [node.frame for key, node in self.nodes(False)]

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
        d = self.network.data
        
        node = {}
        for vkey, vdata in d['data']['node'].items():
            node[vkey] = {key: vdata[key] for key in vdata.keys() if key != 'node'}
            node[vkey]['node'] = vdata['node'].to_data()

        d['data']['node'] = node

        if self.trajectory:
            d['data']['attributes']['trajectory'] = [f.to_data() for f in self.trajectory]
        if self.path:
            d['data']['attributes']['path'] = [f.to_data() for f in self.path]

        return d

    @data.setter
    def data(self, data):
        for _vkey, vdata in data['data']['node'].items():
            vdata['node'] = Node.from_data(vdata['node'])
        
        if 'trajectory' in data:
            self.trajectory = _deserialize_from_data(data['data']['attributes']['trajectory'])
        if 'path' in data:
            self.path = [Frame.from_data(d) for d in data['data']['attributes']['path']]
        
        self.network = Network.from_data(data)

    def add_node(self, node, key=None, attr_dict={}, **kwattr):
        attr_dict.update(kwattr)
        key = self.network.add_node(key=key, attr_dict=attr_dict, node=node)
        return key
    
    def add_edge(self, u, v, attr_dict=None, **kwattr):
        return self.network.add_edge(u, v, attr_dict, **kwattr)

    def transform(self, transformation):
        for key, node in self.nodes(data=False):
            node.transform(transformation)

    def transformed(self, transformation):
        layer = self.copy()
        layer.transform(transformation)
        return layer

    def copy(self):
        """Returns a copy of this layer.

        Returns
        -------
        Layer
        """
        nodes = []
        for key, node in self.nodes():
            nodes.append(node.copy())
        print(nodes)
        return Layer(nodes, self.network.attributes)
        
