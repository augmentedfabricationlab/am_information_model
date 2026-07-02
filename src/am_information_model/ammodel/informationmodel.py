from compas.data import Data
from compas.datastructures import Graph

import uuid
from copy import deepcopy

from am_information_model.src.am_information_model.ammodel.visualisation import AMInformationModelVisualizer

__all__ = [
    'AMModel'
]

HIERARCHY = {
    "robot": [],
    "element": ["path"],
    "path": ["waypoint"],
    "waypoint": [],
}

class AMModel(Data):
    def __init__(self, name="AMModel", **kwargs):
        super().__init__(name=name)
        self._graph = Graph(name=name)
        self._type_index = {}  # node_type -> set of keys

    # --- Core add/get ---
    def generate_node_key(self, node_type):
        return node_type + "-" + str(uuid.uuid4())

    def _node_type(self, key):
        return self._graph.node_attribute(key, "node_type")

    def _assert_relation_allowed(self, parent_key, child_type):
        parent_type = self._node_type(parent_key)
        allowed = HIERARCHY.get(parent_type, [])
        if child_type not in allowed:
            raise ValueError(f"Cannot add '{child_type}' as child of '{parent_type}'. Allowed: {allowed}")

    def _add_type_index(self, node_type, key):
        self._type_index.setdefault(node_type, set()).add(key)

    def add_object(self, obj, node_type, parent_key=None, seq=None):
        """Add any object to the graph with optional parent edge."""
        key = self.generate_node_key(node_type)
        self._graph.add_node(key, node_type=node_type, obj=obj)
        self._add_type_index(node_type, key)

        if parent_key is not None:
            self.add_edge(parent_key, key, edge_type="contains", seq=seq)

        return key

    def add_edge(self, parent_key, child_key, edge_type="contains", seq=None):
        child_type = self._node_type(child_key)
        self._assert_relation_allowed(parent_key, child_type)

        self._graph.add_edge(parent_key, child_key, edge_type=edge_type)
        if edge_type == "contains":
            if seq is None:
                seq = self._next_seq(parent_key, child_type)
            self._graph.edge_attribute((parent_key, child_key), "seq", int(seq))
        return child_key

    def get_object(self, key):
        return self._graph.node_attribute(key, "obj")

    # --- Typed accessors ---

    def add_element(self, element):
        return self.add_object(element, "element")

    def add_path(self, path, element_key=None, seq=None):
        return self.add_object(path, "path", parent_key=element_key, seq=seq)

    def add_waypoint(self, waypoint, path_key=None, seq=None):
        return self.add_object(waypoint, "waypoint", parent_key=path_key, seq=seq)
    
    def add_robot(self, robot):
        return self.add_object(robot, "robot")

    # --- Sequence methods ---

    def _next_seq(self, object_key, child_type):
        seqs = self._sequence(object_key, child_type)
        return (max(seqs) + 1) if seqs else 0

    def _sequence(self, object_key, child_type):
        return [
            int(s)
            for child_key, _ in self.children(object_key, child_type)
            for s in [self._graph.edge_attribute((object_key, child_key), "seq")]
            if s is not None
        ]

    def ordered_children(self, parent_key, child_type):
        items = list(self.children(parent_key, child_type))  # [(key, obj), ...]
        items.sort(key=lambda item: self._graph.edge_attribute((parent_key, item[0]), "seq"))
        return items

    def set_sequence(self, parent_key, child_type, ordered_child_keys):
        child_keys = {k for k, _ in self.children(parent_key, child_type)}
        if set(ordered_child_keys) != child_keys:
            raise ValueError("ordered_child_keys must match exactly the current children.")
        for i, child_key in enumerate(ordered_child_keys):
            self._graph.edge_attribute((parent_key, child_key), "seq", i)

    # --- Queries ---

    def objects(self, node_type=None):
        if node_type is None:
            for key in self._graph.nodes():
                yield key, self._graph.node_attribute(key, "obj")
            return

        for key in self._type_index.get(node_type, []):
            yield key, self._graph.node_attribute(key, "obj")

    def _typed(self, node_type, parent_key=None, ordered=False):
        if parent_key is None:
            return self.objects(node_type)
        if ordered:
            return self.ordered_children(parent_key, node_type)
        return self.children(parent_key, node_type)

    def children(self, parent_key, child_type=None):
        """Get all children of a node, optionally filtered by type."""
        for nbr in self._graph.neighbors(parent_key):
            if self._graph.has_edge((parent_key, nbr)):
                if child_type is None or self._graph.node_attribute(nbr, "node_type") == child_type:
                    yield nbr, self._graph.node_attribute(nbr, "obj")

    def parent(self, child_key):
        """Get the parent of a node (the node pointing to it)."""
        for nbr in self._graph.neighbors(child_key):
            if self._graph.has_edge((nbr, child_key)):
                return nbr, self._graph.node_attribute(nbr, "obj")
        return None, None

    def elements(self):
        return self._typed("element")

    def paths(self, element_key=None):
        return self._typed("path", parent_key=element_key)

    def waypoints(self, path_key=None):
        return self._typed("waypoint", parent_key=path_key)

    # --- Convenience wrappers ---

    def element_paths(self, element_key):
        return self._typed("path", parent_key=element_key, ordered=True)

    def path_waypoints(self, path_key):
        return self._typed("waypoint", parent_key=path_key, ordered=True)

    # --- Link helpers ---
    def link_path_to_element(self, path_key, element_key, seq=None):
        return self.add_edge(element_key, path_key, edge_type="contains", seq=seq)

    def link_waypoint_to_path(self, waypoint_key, path_key, seq=None):
        return self.add_edge(path_key, waypoint_key, edge_type="contains", seq=seq)

    # --- Serialization (COMPAS Data framework) ---

    @property
    def __data__(self):
        return {
            "graph": self._graph.__data__,
            "type_index": {k: list(v) for k, v in self._type_index.items()},
        }

    @classmethod
    def from_data(cls, data):
        model = cls()
        model._graph = Graph.from_data(data["graph"])
        model._type_index = {k: set(v) for k, v in data["type_index"].items()}
        return model
    
    # --- Copy methods ---

    def _copy_payload(self, obj, T=None):
        """Prefer object-level copy(), fallback to deepcopy."""
        if T is not None and hasattr(obj, "transformed") and callable(obj.transformed):
            return obj.transformed(T)
        
        if hasattr(obj, "copy") and callable(obj.copy):
            obj_copy = obj.copy()
        else:
            obj_copy = deepcopy(obj)

        if T is not None and hasattr(obj_copy, "transform") and callable(obj_copy.transform):
            obj_copy.transform(T)

        return obj_copy

    def copy_subtree(self, root_key, new_parent_key=None, T=None, seq=None):
        """
        Copy a node and all valid descendants based on HIERARCHY.
        Returns the new root key of the copied subtree.
        """
        node_type = self._node_type(root_key)
        obj = self.get_object(root_key)
        obj_copy = self._copy_payload(obj, T=T)

        if new_parent_key is None:
            new_root_key = self.add_object(obj_copy, node_type)
        else:
            if seq is None:
                old_seq = None
                old_parent_key, _ = self.parent(root_key)
                if old_parent_key is not None and self._graph.has_edge((old_parent_key, root_key)):
                    old_seq = self._graph.edge_attribute((old_parent_key, root_key), "seq")
                    if old_seq is not None:
                        old_seq = int(old_seq)

                # siblings under new_parent_key are of type == node_type
                existing = set(self._sequence(new_parent_key, node_type))

                if old_seq is not None and old_seq not in existing:
                    seq = old_seq
                else:
                    seq = self._next_seq(new_parent_key, node_type)

            new_root_key = self.add_object(obj_copy, node_type, parent_key=new_parent_key, seq=seq)

        # preserve descendant ordering
        for child_type in HIERARCHY.get(node_type, []):
            for child_key, _ in self.ordered_children(root_key, child_type):
                child_seq = self._graph.edge_attribute((root_key, child_key), "seq")
                self.copy_subtree(
                    child_key,
                    new_parent_key=new_root_key,
                    T=T,
                    seq=child_seq
                )

        return new_root_key

    def copy_element(self, element_key, T=None):
        if self._node_type(element_key) != "element":
            raise ValueError("copy_element expects an element key.")
        return self.copy_subtree(element_key, T=T)

    def copy_path(self, path_key, element_key, T=None, seq=None):
        if self._node_type(path_key) != "path":
            raise ValueError("copy_path expects a path key.")
        return self.copy_subtree(path_key, new_parent_key=element_key, T=T, seq=seq)

    def copy_waypoint(self, waypoint_key, path_key, T=None, seq=None):
        if self._node_type(waypoint_key) != "waypoint":
            raise ValueError("copy_waypoint expects a waypoint key.")
        return self.copy_subtree(waypoint_key, new_parent_key=path_key, T=T, seq=seq)
    def visualise_graph_matplotlib(self, dx=3.0, dy=1.5, figsize=(12, 8), show_seq=True, savepath=None):
        """Backward-compatible wrapper that delegates to the dedicated visualizer class."""
        from .visualization import Visualizer

        visualizer = Visualizer(self)
        return visualizer.visualise_matplotlib(
            dx=dx,
            dy=dy,
            figsize=figsize,
            show_seq=show_seq,
            savepath=savepath,
        )
    
if __name__ == "__main__":
    import os
    import sys

    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from am_information_model.ammodel.model import AMModel
    from am_information_model.ammodel.element import Element
    from am_information_model.ammodel.path import Path
    from am_information_model.ammodel.waypoint import Waypoint
    from compas.geometry import Frame

    model = AMModel()

    element = Element(frame=Frame.worldXY())
    ek = model.add_element(element)

    path = Path()
    pk = model.add_path(path, ek)

    for i in range(10):
        wp = Waypoint(frame=Frame.worldXY())
        model.add_waypoint(wp, pk)

    # query
    for key, wp in model.waypoints(pk):
        print(key, wp.frame)

    model.visualise_graph_matplotlib()