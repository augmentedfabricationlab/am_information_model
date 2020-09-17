from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

from compas.datastructures import Network

from .node import Node

from .utilities import FromToData
from .utilities import FromToJson

__all__ = ['AMIM']


class AMIM(FromToData, FromToJson):
    """A data structure for non-discrete element fabrication.

    A model is essentially a network of nodes.
    Each geometrical node is represented by a node of the network.
    Each line drawn between nodes is represented by an edge of the network.

    Attributes
    ----------
    network : :class:`compas.Network`, optional
    nodes : list of :class:`Node`, optional
        A list of model nodes.
    attributes : dict, optional
        User-defined attributes of the model.
        Built-in attributes are:
        * name (str) : ``'Assembly'``
    default_element_attribute : dict, optional
        User-defined default attributes of the elements of the model.
        The built-in attributes are:
        * is_planned (bool) : ``False``
        * is_placed (bool) : ``False``
    default_connection_attributes : dict, optional
        User-defined default attributes of the connections of the model.

    Examples
    --------

    """

    def __init__(self,
                 nodes=None,
                 attributes=None,
                 default_node_attribute=None,
                 default_connection_attributes=None):

        self.network = Network()
        self.network.attributes.update({'name': 'Assembly'})

        if attributes is not None:
            self.network.attributes.update(attributes)

        self.network.default_node_attributes.update({
            'is_planned': False,
            'is_placed': False
        })

        if default_node_attribute is not None:
            self.network.default_node_attributes.update(default_node_attribute)

        if default_connection_attributes is not None:
            self.network.default_edge_attributes.update(default_connection_attributes)

        if nodes:
            for node in nodes:
                self.add_node(node)

    @property
    def name(self):
        """str : The name of the model."""
        return self.network.attributes.get('name', None)

    @name.setter
    def name(self, value):
        self.network.attributes['name'] = value

    def number_of_nodes(self):
        """Compute the number of nodes of the model.

        Returns
        -------
        int
            The number of nodes.

        """
        return self.network.number_of_nodes()

    def number_of_connections(self):
        """Compute the number of connections of the model.

        Returns
        -------
        int
            the number of connections.

        """
        return self.network.number_of_edges()

    @property
    def data(self):
        """Return a data dictionary of the model.
        """
        # Network data does not recursively serialize to data...
        d = self.network.data

        # so we need to trigger that for elements stored in nodes
        node = {}
        for vkey, vdata in d['node'].items():
            node[vkey] = {key: vdata[key] for key in vdata.keys() if key != 'node'}
            node[vkey]['node'] = vdata['node'].to_data()

        d['node'] = node

        return d

    @data.setter
    def data(self, data):
        # Deserialize elements from node dictionary
        for _vkey, vdata in data['node'].items():
            vdata['node'] = Node.from_data(vdata['node'])

        self.network = Network.from_data(data)

    def clear(self):
        """Clear all the model data."""
        self.network.clear()

    def add_node(self, node, key=None, attr_dict={}, **kwattr):
        """Add an element to the model.

        Parameters
        ----------
        element : Element
            The element to add.
        attr_dict : dict, optional
            A dictionary of element attributes. Default is ``None``.

        Returns
        -------
        hashable
            The identifier of the element.
        """
        attr_dict.update(kwattr)
        x, y, z = node.frame.point
        key = self.network.add_node(key=key, attr_dict=attr_dict,
                                      x=x, y=y, z=z, node=node)
        if key == 0:
            pass
        else:
            self.add_edge(key-1, key)
        return key

    def add_edge(self, u, v, attr_dict=None, **kwattr):
        """Add a connection between two elements and specify its attributes.

        Parameters
        ----------
        u : hashable
            The identifier of the first element of the connection.
        v : hashable
            The identifier of the second element of the connection.
        attr_dict : dict, optional
            A dictionary of connection attributes.
        kwattr
            Other connection attributes as additional keyword arguments.

        Returns
        -------
        tuple
            The identifiers of the elements.
        """
        return self.network.add_edge(u, v, attr_dict, **kwattr)

    def transform(self, transformation):
        """Transforms this model.

        Parameters
        ----------
        transformation : :class:`Transformation`

        Returns
        -------
        None
        """
        for _k, node in self.nodes(data=False):
            node.transform(transformation)

    def transformed(self, transformation):
        """Returns a transformed copy of this model.

        Parameters
        ----------
        transformation : :class:`Transformation`

        Returns
        -------
        Assembly
        """
        manufacturing = self.copy()
        manufacturing.transform(transformation)
        return manufacturing

    def copy(self):
        """Returns a copy of this model.
        """
        raise NotImplementedError

    def node(self, key, data=False):
        """Get an element by its key."""
        if data:
            return self.network.node[key]['node'], self.network.node[key]
        else:
            return self.network.node[key]['node']

    def nodes(self, data=False):
        """Iterate over the elements of the model.

        Parameters
        ----------
        data : bool, optional
            If ``True``, yield both the identifier and the attributes.

        Yields
        ------
        2-tuple
            The next element as a (key, element) tuple, if ``data`` is ``False``.
        3-tuple
            The next element as a (key, element, attr) tuple, if ``data`` is ``True``.

        """
        if data:
            for vkey, vattr in self.network.nodes(True):
                yield vkey, vattr['node'], vattr
        else:
            for vkey in self.network.nodes(data):
                yield vkey, self.network.node[vkey]['node']

    def connections(self, data=False):
        """Iterate over the connections of the network.

        Parameters
        ----------
        data : bool, optional
            If ``True``, yield both the identifier and the attributes.

        Yields
        ------
        2-tuple
            The next connection identifier (u, v), if ``data`` is ``False``.
        3-tuple
            The next connection as a (u, v, attr) tuple, if ``data`` is ``True``.

        """
        return self.network.edges(data)

