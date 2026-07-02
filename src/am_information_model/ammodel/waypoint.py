from compas.data import Data
from compas.geometry import Frame
from copy import deepcopy
import uuid

__all__ = ['Waypoint']


class Waypoint(Data):
    def __init__(self, frame=None, name=None, uid=None, **kwargs):
        super().__init__()
        self.frame = frame or Frame.worldXY()
        self.name = name
        self.uid = uid or str(uuid.uuid4())
        self.attributes = kwargs

    @property
    def __data__(self):
        return {
            "frame": self.frame,
            "name": self.name,
            "uid": self.uid,
            "attributes": self.attributes,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            frame=data.get("frame"),
            name=data.get("name"),
            uid=data.get("uid"),
            **data.get("attributes", {})
        )
    
    @classmethod
    def from_frame(cls, frame, name=None, **kwargs):
        return cls(frame=frame, name=name, **kwargs)

    def transform(self, T):
        self.frame.transform(T)

    def copy(self, refresh_uid=True):
        waypoint = deepcopy(self)
        if refresh_uid:
            waypoint.uid = str(uuid.uuid4())
        return waypoint

    def transformed(self, T):
        wp = self.copy(refresh_uid=True)
        wp.transform(T)
        return wp

    def __repr__(self):
        return f"Waypoint(frame={self.frame}, name={self.name}, uid={self.uid})"