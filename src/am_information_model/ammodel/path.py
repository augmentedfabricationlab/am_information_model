from compas.data import Data
from copy import deepcopy

__all__ = [
    'Path'
]


class Path(Data):
    def __init__(self, name=None, waypoints=None, waypoint_seq=None, **kwargs):
        super().__init__()
        self.name = name
        self._waypoints = {}      # uid -> Waypoint
        self._waypoint_seq = {}   # uid -> int (sequence number, mirrors graph edge seq)
        self.attributes = kwargs

        if waypoints:
            for uid, waypoint in (waypoints.items() if isinstance(waypoints, dict) else [(wp.uid, wp) for wp in waypoints]):
                self._waypoints[uid] = waypoint
        if waypoint_seq:
            self._waypoint_seq.update(waypoint_seq)

    # --- Waypoint management ---

    def add_waypoint(self, waypoint, seq=None):
        """Add a waypoint. seq mirrors graph edge seq; auto-increments if None."""
        uid = waypoint.uid
        self._waypoints[uid] = waypoint
        if seq is None:
            seq = (max(self._waypoint_seq.values()) + 1) if self._waypoint_seq else 0
        self._waypoint_seq[uid] = int(seq)
        return uid

    def get_waypoint(self, uid):
        return self._waypoints.get(uid)

    def waypoint_items(self):
        """Return (uid, waypoint) pairs ordered by seq."""
        return sorted(self._waypoints.items(), key=lambda kv: self._waypoint_seq.get(kv[0], 0))

    @property
    def waypoints(self):
        """Ordered list of waypoints."""
        return [wp for _, wp in self.waypoint_items()]

    def set_waypoint_sequence(self, ordered_waypoint_uids):
        """Re-assign seq values by providing an ordered list of uids."""
        if set(ordered_waypoint_uids) != set(self._waypoints):
            raise ValueError("ordered_waypoint_uids must match exactly the current waypoints.")
        for i, uid in enumerate(ordered_waypoint_uids):
            self._waypoint_seq[uid] = i

    # --- Transform ---

    def transform(self, T):
        for waypoint in self._waypoints.values():
            waypoint.transform(T)

    def copy(self):
        new_path = Path(name=self.name, **deepcopy(self.attributes))
        for uid, waypoint in self._waypoints.items():
            new_wp = waypoint.copy(refresh_uid=True)
            new_path._waypoints[new_wp.uid] = new_wp
            new_path._waypoint_seq[new_wp.uid] = self._waypoint_seq.get(uid, 0)
        return new_path

    def transformed(self, T):
        path = self.copy()
        path.transform(T)
        return path

    # --- Serialization ---

    @property
    def __data__(self):
        return {
            "name": self.name,
            "waypoints": self._waypoints,
            "waypoint_seq": self._waypoint_seq,
            "attributes": self.attributes,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            name=data.get("name"),
            waypoints=data.get("waypoints", {}),
            waypoint_seq=data.get("waypoint_seq", {}),
            **data.get("attributes", {})
        )

    def __repr__(self):
        return f"Path(name={self.name}, waypoints={len(self._waypoints)}, attributes={self.attributes})"