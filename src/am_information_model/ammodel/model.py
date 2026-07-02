from compas.data import Data
from compas.datastructures import Graph

import uuid
from copy import deepcopy


__all__ = [
    'AMModel'
]

HIERARCHY = {
    "robot": [],
    "element": ["path"],
    "path": [],
    "waypoint": [],
}

class AMModel(Data):
    def __init__(self, name="AMModel", **kwargs):
        super().__init__(name=name)
        self._graph = Graph(name=name)
        self._type_index = {}  # node_type -> set of keys
        self._name_index = {}  # object name -> set of keys

    # --- Create and link ---

    def add_object(self, obj, node_type, parent_key=None, seq=None):
        """Add any object to the graph with optional parent edge."""
        key = self._generate_node_key(node_type)
        self._graph.add_node(key, node_type=node_type, obj=obj)
        self._add_type_index(node_type, key)
        self._add_name_index(obj, key)

        if parent_key is not None:
            self.add_edge(parent_key, key, edge_type="contains", seq=seq)

        return key

    def add_edge(self, parent_key, child_key, edge_type="contains", seq=None):
        child_type = self._node_type(child_key)
        self._assert_relation_allowed(parent_key, child_type)

        self._graph.add_edge(parent_key, child_key, edge_type=edge_type)
        if edge_type == "contains":
            if seq is None:
                seq = self._next_sequence(parent_key, child_type)
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
        if path_key is None:
            raise ValueError("Waypoints are stored inside a path. Provide a path_key.")

        path = self.get_object(path_key)
        if not hasattr(path, "add_waypoint"):
            raise TypeError("Path object does not support waypoint storage.")

        return path.add_waypoint(waypoint, seq=seq)
    
    def add_robot(self, robot):
        return self.add_object(robot, "robot")

    def add_path_with_waypoints(
        self,
        path,
        waypoints,
        element_key=None,
        path_seq=None,
        waypoint_start_seq=None,
    ):
        """Create a path and attach waypoint subcomponents in one call.

        Parameters
        ----------
        path : object
            Path object to add.
        waypoints : iterable
            Waypoint objects to add under the created path.
        element_key : str, optional
            Parent element key. If None, the path is added unlinked.
        path_seq : int, optional
            Sequence value for the element->path edge.
        waypoint_start_seq : int, optional
            If provided, waypoints use explicit consecutive seq values starting here.
            If None, waypoint seq is auto-assigned.

        Returns
        -------
        tuple[str, list[str]]
            Created path key and created waypoint keys.
        """
        path_key = self.add_path(path, element_key=element_key, seq=path_seq)

        waypoint_keys = []
        for index, waypoint in enumerate(waypoints):
            seq = None
            if waypoint_start_seq is not None:
                seq = int(waypoint_start_seq) + index
            waypoint_key = self.add_waypoint(waypoint, path_key=path_key, seq=seq)
            waypoint_keys.append(waypoint_key)

        return path_key, waypoint_keys

    # --- Sequence methods ---

    def _next_seq(self, object_key, child_type):
        seqs = self._sequence(object_key, child_type)
        return (max(seqs) + 1) if seqs else 0

    def _sequence(self, object_key, child_type):
        return [
            int(s)
            for child_key, _ in self._children(object_key, child_type)
            for s in [self._graph.edge_attribute((object_key, child_key), "seq")]
            if s is not None
        ]

    def ordered_children(self, parent_key, child_type):
        if child_type == "waypoint" and self._node_type(parent_key) == "path":
            return self.path_waypoints(parent_key)

        items = list(self._children(parent_key, child_type))  # [(key, obj), ...]
        items.sort(key=lambda item: self._graph.edge_attribute((parent_key, item[0]), "seq"))
        return items

    def set_sequence(self, parent_key, child_type, ordered_child_keys):
        if child_type == "waypoint" and self._node_type(parent_key) == "path":
            path = self.get_object(parent_key)
            path.set_waypoint_sequence(ordered_child_keys)
            return

        child_keys = {k for k, _ in self._children(parent_key, child_type)}
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

    def objects_by_name(self, name):
        """Yield (key, obj) pairs for objects with the given name."""
        for key in self._name_index.get(str(name), []):
            yield key, self._graph.node_attribute(key, "obj")

    def find_first_by_name(self, name):
        """Return the first (key, obj) match for a name, or (None, None)."""
        for key, obj in self.objects_by_name(name):
            return key, obj
        return None, None


    def link_path_to_element(self, path_key, element_key, seq=None):
        return self.add_edge(element_key, path_key, edge_type="contains", seq=seq)

    def link_waypoint_to_path(self, waypoint_key, path_key, seq=None):
        return self.add_edge(path_key, waypoint_key, edge_type="contains", seq=seq)

    # --- Query ---

    def get_object(self, key):
        return self._graph.node_attribute(key, "obj")

    def objects(self, node_type=None):
        if node_type is None:
            for key in self._graph.nodes():
                yield key, self._graph.node_attribute(key, "obj")
            return

        for key in self._type_index.get(node_type, []):
            yield key, self._graph.node_attribute(key, "obj")

    # --- Typed query ---

    def elements(self):
        return self._typed("element")

    def paths(self, element_key=None):
        return self._typed("path", parent_key=element_key)

    def waypoints(self, path_key=None):
        if path_key is not None:
            return self.path_waypoints(path_key)

        for path_key, _ in self.paths():
            for waypoint_uid, waypoint in self.path_waypoints(path_key):
                yield waypoint_uid, waypoint

    # --- Ordering ---

    def ordered_children(self, parent_key, child_type):
        items = list(self._children(parent_key, child_type))  # [(key, obj), ...]
        items.sort(key=lambda item: self._graph.edge_attribute((parent_key, item[0]), "seq"))
        return items

    def set_sequence(self, parent_key, child_type, ordered_child_keys):
        child_keys = {k for k, _ in self._children(parent_key, child_type)}
        if set(ordered_child_keys) != child_keys:
            raise ValueError("ordered_child_keys must match exactly the current children.")
        for i, child_key in enumerate(ordered_child_keys):
            self._graph.edge_attribute((parent_key, child_key), "seq", i)

    # --- Convenience typed order wrappers ---

    def element_paths(self, element_key):
        return self._typed("path", parent_key=element_key, ordered=True)

    def path_waypoints(self, path_key):
        path = self.get_object(path_key)
        if not hasattr(path, "waypoint_items"):
            return []
        return path.waypoint_items()

    # --- Copy API ---

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
                old_parent_key, _ = self._parent(root_key)
                if old_parent_key is not None and self._graph.has_edge((old_parent_key, root_key)):
                    old_seq = self._graph.edge_attribute((old_parent_key, root_key), "seq")
                    if old_seq is not None:
                        old_seq = int(old_seq)

                # siblings under new_parent_key are of type == node_type
                existing = set(self._sequence(new_parent_key, node_type))

                if old_seq is not None and old_seq not in existing:
                    seq = old_seq
                else:
                    seq = self._next_sequence(new_parent_key, node_type)

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
        path = self.get_object(path_key)
        if not hasattr(path, "get_waypoint"):
            raise TypeError("Path object does not support waypoint storage.")

        waypoint = path.get_waypoint(waypoint_key)
        if waypoint is None:
            raise ValueError("copy_waypoint expects a waypoint uid belonging to the target path.")

        waypoint_copy = self._copy_payload(waypoint, T=T)
        return self.add_waypoint(waypoint_copy, path_key=path_key, seq=seq)

    # --- Serialization ---

    @property
    def __data__(self):
        return {
            "graph": self._graph.__data__,
            "type_index": {k: list(v) for k, v in self._type_index.items()},
            "name_index": {k: list(v) for k, v in self._name_index.items()},
        }

    @classmethod
    def from_data(cls, data):
        model = cls()
        model._graph = Graph.from_data(data["graph"])
        model._type_index = {k: set(v) for k, v in data.get("type_index", {}).items()}
        model._name_index = {k: set(v) for k, v in data.get("name_index", {}).items()}

        # Rebuild indexes if missing (older files) or if inconsistent.
        if not model._type_index:
            model._rebuild_type_index()
        if not model._name_index:
            model._rebuild_name_index()

        return model

    # --- Internal helpers ---

    def _generate_node_key(self, node_type):
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

    def _object_name(self, obj):
        name = getattr(obj, "name", None)
        if name is None and hasattr(obj, "attributes") and isinstance(obj.attributes, dict):
            name = obj.attributes.get("name")
        if name is None:
            return None
        return str(name)

    def _add_name_index(self, obj, key):
        name = self._object_name(obj)
        if not name:
            return
        self._name_index.setdefault(name, set()).add(key)

    def _rebuild_type_index(self):
        self._type_index = {}
        for key in self._graph.nodes():
            node_type = self._graph.node_attribute(key, "node_type")
            self._add_type_index(node_type, key)

    def _rebuild_name_index(self):
        self._name_index = {}
        for key in self._graph.nodes():
            obj = self._graph.node_attribute(key, "obj")
            self._add_name_index(obj, key)

    def _next_sequence(self, object_key, child_type):
        seqs = self._sequence(object_key, child_type)
        return (max(seqs) + 1) if seqs else 0

    def _sequence(self, object_key, child_type):
        return [
            int(s)
            for child_key, _ in self._children(object_key, child_type)
            for s in [self._graph.edge_attribute((object_key, child_key), "seq")]
            if s is not None
        ]

    def _typed(self, node_type, parent_key=None, ordered=False):
        if node_type == "waypoint":
            if parent_key is None:
                return self.waypoints()
            return self.path_waypoints(parent_key)

        if parent_key is None:
            return self.objects(node_type)
        if ordered:
            return self.ordered_children(parent_key, node_type)
        return self._children(parent_key, node_type)

    def _children(self, parent_key, child_type=None):
        """Get all children of a node, optionally filtered by type."""
        for nbr in self._graph.neighbors(parent_key):
            if self._graph.has_edge((parent_key, nbr)):
                if child_type is None or self._graph.node_attribute(nbr, "node_type") == child_type:
                    yield nbr, self._graph.node_attribute(nbr, "obj")

    def _parent(self, child_key):
        """Get the parent of a node (the node pointing to it)."""
        for nbr in self._graph.neighbors(child_key):
            if self._graph.has_edge((nbr, child_key)):
                return nbr, self._graph.node_attribute(nbr, "obj")
        return None, None

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
    
    # --- Visualization ---

    def visualise_graph_matplotlib(self, dx=3.0, dy=1.5, figsize=(12, 8), show_seq=True, savepath=None):
        """Backward-compatible wrapper that delegates to the dedicated visualizer class."""
        from .visualisation import Visualizer

        visualizer = Visualizer(self)
        return visualizer.visualise_matplotlib(
            dx=dx,
            dy=dy,
            figsize=figsize,
            show_seq=show_seq,
            savepath=savepath,
        )