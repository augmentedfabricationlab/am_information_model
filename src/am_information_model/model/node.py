from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame

__all__ = ['Node']


class Node:
    """Data structure representing a discrete nodes of an model.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The frame of the node.

    _tool_frame : :class:`compas.geometry.Frame`
        The frame of the node where the robot's tool should attach to.

    radius : for joined nodes, a blend radius is required

    Examples
    --------

    """

    def __init__(self, frame=None, radius=0):
        self.frame = frame
        self.radius = radius
        self.robot_vel = 0
        self.is_constructed = False
        self.ext_state = 0
        self.ext_speed = 0
        self.material_supply = 0

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
    def pose_quaternion(self):
        """ formats the node's tool frame to a pose quaternion and returns the pose"""
        return list(self.frame.point) + list(self.frame.quaternion)

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
        node = cls()
        node.data(data)
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
        d = dict()
        d['frame'] = self.frame.to_data()
        d['radius'] = self.radius
        d['robot_vel'] = self.robot_vel
        d['is_constructed'] = self.is_constructed
        d['ext_state'] = self.ext_state
        d['ext_speed'] = self.ext_speed
        d['material_supply'] = self.material_supply
        return d

    @data.setter
    def data(self, data):
        self.frame = Frame.from_data(data['frame'])
        self.radius = data['radius']
        self.robot_vel = data['robot_vel']
        self.is_constructed = data['is_constructed']
        self.ext_state = data['ext_state']
        self.ext_speed = data['ext_speed']
        self.material_supply = data['material_supply']

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
        node.radius = self.radius
        node.robot_vel = self.robot_vel
        node.is_constructed = self.is_constructed
        node.ext_state = self.ext_state
        node.ext_speed = self.ext_speed
        node.material_supply = self.material_supply
        return node
