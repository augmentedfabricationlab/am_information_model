from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

from compas.datastructures import Network

from .layer import Layer

from .utilities import FromToData
from .utilities import FromToJson

__all__ = ['AMModel']


class AMModel(FromToData, FromToJson):
    """A data structure for non-discrete element fabrication.

    A model is essentially a network of nodes.
    Each geometrical node is represented by a layer in fabrication.
    The sequence of layers in fabrication is represented by an edge of the network.

    Attributes
    ----------
    network : :class:`compas.Network`, optional
    layers : list of :class:`Layer`, optional
        A list of model layers.
    attributes : dict, optional
        User-defined attributes of the model.
        Built-in attributes are:
        * name (str) : ``'AMModel'``
    default_layer_attribute : dict, optional
        User-defined default attributes of the layers of the model.
        The built-in attributes are:
        * is_planned (bool) : ``False``
        * is_placed (bool) : ``False``

    Examples
    --------

    """

    def __init__(self,
                 layers=None,
                 attributes=None,
                 default_layer_attribute=None,
                 default_connection_attributes=None):

        self.network = Network()
        self.network.attributes.update({'name': 'AMModel'})

        if attributes is not None:
            self.network.attributes.update(attributes)

        self.network.default_node_attributes.update({
            'is_planned': False,
            'is_placed': False
        })

        if default_layer_attribute is not None:
            self.network.default_node_attributes.update(default_layer_attribute)

        if default_connection_attributes is not None:
            self.network.default_edge_attributes.update(default_connection_attributes)

        if layers:
            for layer in layers:
                self.add_layer(layer)
                

    @property
    def name(self):
        """str : The name of the model."""
        return self.network.attributes.get('name', None)

    @name.setter
    def name(self, value):
        self.network.attributes['name'] = value

    def number_of_layers(self):
        """Compute the number of layers of the model.

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
        #print(d.keys())
        # so we need to trigger that for layers stored in nodes
        node = {}
        for vkey, vdata in d['data']['node'].items():
            node[vkey] = {key: vdata[key] for key in vdata.keys() if key != 'layer'}
            node[vkey]['layer'] = vdata['layer'].to_data()

        d['data']['node'] = node
        return d

    @data.setter
    def data(self, data):
        # Deserialize elements from node dictionary
        for _vkey, vdata in data['data']['node'].items():
            vdata['layer'] = Layer.from_data(vdata['layer'])

        self.network = Network.from_data(data)

    def clear(self):
        """Clear all the model data."""
        self.network.clear()

    def add_layer(self, layer, key=None, attr_dict={}, **kwattr):
        """Add an element to the model.

        Parameters
        ----------
        layer : Layer
            The layer to add.
        attr_dict : dict, optional
            A dictionary of layer attributes. Default is ``None``.

        Returns
        -------
        hashable
            The identifier of the element.
        """
        attr_dict.update(kwattr)
        key = self.network.add_node(key=key, attr_dict=attr_dict, layer=layer)
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
        for _k, layer in self.layers(data=False):
            layer.transform(transformation)

    def transformed(self, transformation):
        """Returns a transformed copy of this model.

        Parameters
        ----------
        transformation : :class:`Transformation`

        Returns
        -------
        Assembly
        """
        model = self.copy()
        model.transform(transformation)
        return model

    def copy(self):
        """Returns a copy of this model.
        """
        layers = []
        for key, layer in self.layers():
            layers.append(layer.copy())
        return AMModel(layers, self.network.attributes)

    def layer(self, key, data=False):
        """Get an layer by its key."""
        if data:
            return self.network.node[key]['layer'], self.network.node[key]
        else:
            return self.network.node[key]['layer']

    def layers(self, data=False):
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
                yield vkey, vattr['layer'], vattr
        else:
            for vkey in self.network.nodes(data):
                yield vkey, self.network.node[vkey]['layer']

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

