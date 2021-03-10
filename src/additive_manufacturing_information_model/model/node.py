from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame

from .utilities import _deserialize_from_data

__all__ = ['Node']


class Node:
    """Data structure representing a discrete nodes of an model.

    Attributes
    ----------
    _frame : :class:`compas.geometry.Frame`
        The frame of the node.

    _tool_frame : :class:`compas.geometry.Frame`
        The frame of the node where the robot's tool should attach to.

    node_type : node type identifier
        0: starting node
        1: joined node
        2: ending node

    radius : for joined nodes, a blend radius is required

    Examples
    --------

    """

    def __init__(self, frame, radius=0):
        self.frame = frame
        self._tool_frame = frame

        self.radius = radius

    @classmethod
    def from_frame(cls, frame):
        """Class method for constructing a node from a compas frame.

        Parameters
        ----------
        frame : :class:`Frame`
            Origin frame of the node.
        """
        node = cls(frame)
        return node

    @property
    def frame(self):
        """Frame of the node."""
        return self._frame

    @frame.setter
    def frame(self, frame):
        self._frame = frame.copy()

    @property
    def tool_frame(self):
        """tool frame of the node"""
        if not self._tool_frame:
            self._tool_frame = self.frame.copy()

        return self._tool_frame

    @tool_frame.setter
    def tool_frame(self, frame):
        self._tool_frame = frame.copy()

    @property
    def pose_quaternion(self):
        """ formats the node's tool frame to a pose quaternion and returns the pose"""
        return list(self._tool_frame.point) + list(self._tool_frame.quaternion)

    @classmethod
    def from_data(cls, data):
        """Construct an node from its data representation.

        Parameters
        ----------
        data : :obj:`dict`
            The data dictionary.

        Returns
        -------
        Node
            The constructed node.
        """
        node = cls(Frame.worldXY())
        node.data = data
        return node

    def to_data(self):
        return self.data

    @property
    def data(self):
        """Returns the data dictionary that represents the node.

        Returns
        -------
        dict
            The node data.

        Examples
        --------
        >>> node = Node(Frame.worldXY())
        >>> print(node.data)
        """
        d = dict(frame=self.frame.to_data())

        # Only include gripping plane if attribute is really set
        # (unlike the property getter that defaults to `self.frame`)
        if self._tool_frame:
            d['_tool_frame'] = self._tool_frame.to_data()
        d['radius'] = self.radius

        return d

    @data.setter
    def data(self, data):
        self.frame = Frame.from_data(data['frame'])
        if '_tool_frame' in data:
            self.tool_frame = Frame.from_data(data['_tool_frame'])
        self.radius = data['radius']


    def transform(self, transformation):
        """Transforms the node.

        Parameters
        ----------
        transformation : :class:`Transformation`

        Returns
        -------
        None

        Examples
        --------
        """
        self.frame.transform(transformation)
        if self._tool_frame:
            self.tool_frame.transform(transformation)

    def transformed(self, transformation):
        """Returns a transformed copy of this node.

        Parameters
        ----------
        transformation : :class:`Transformation`

        Returns
        -------
        Node

        Examples
        --------
        """
        node = self.copy()
        node.transform(transformation)
        return node

    def copy(self):
        """Returns a copy of this node.

        Returns
        -------
        Node
        """
        node = Node(self.frame.copy())
        if self._tool_frame:
            node.tool_frame = self.tool_frame.copy()
        return node
