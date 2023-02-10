
from compas.datastructures import Datastructure
from compas.geometry import Frame

__all__ = [
    'Node'
]


class Node(Datastructure):
    def __init__(self, name="node", frame=None, **kwargs):
        super(Node, self).__init__()
        self._frame = None
        self.frame = frame
        self.key = None
        self.attributes= {
            "name" : name,
            "state" : None,
            "path_width" : None,
            "path_height" : None,
            "extrusion_rate" : None,
            "robot_velocity" : None
        }
        
    @property
    def frame(self):
        if not self._frame:
            self._frame = Frame.worldXY()
        return self._frame
    
    @frame.setter
    def frame(self, frame):
        self._frame = frame

    @property
    def data(self):
        data = {
            "attributes": self.attributes,
            "key": self.key,
            "frame": self.frame.data
        }
        return data
    
    @data.setter
    def data(self, data):
        self.attributes.update(data["attributes"] or {})
        self.key = data["key"]
        self.frame.data = data["frame"]
    
    @property
    def robot_velocity(self):
        if (None not in [self._path_width, self._path_height,
                         self._extrusion_rate]
           and self._robot_velocity is None):
            self.robot_velocity()
        elif self._robot_velocity is None:
            print("Robot velocity is not set, and cannot be calculated!")
        return self._robot_velocity

    @robot_velocity.setter
    def robot_velocity(self, robot_velocity=None):
        if robot_velocity is not None:
            self._robot_velocity = robot_velocity
        else:
            area = self._path_width*self._path_height
            # m3
            nozzle_size = 0.007
            volume = area*nozzle_size
            # profile must be achieved within length of the nozzle
            velocity = (volume*1000)/self._extrusion_rate
            # m/min
            self._robot_velocity = (velocity*1000)/60
            # mm/s

    @property
    def extrusion_rate(self):
        if (None not in [self._path_width, self._path_height,
                         self._robot_velocity]
           and self._extrusion_rate is None):
            self.extrusion_rate()
        elif self._extrusion_rate is None:
            print("Extrusion rate is not set, and cannot be calculated!")
        return self._extrusion_rate

    @extrusion_rate.setter
    def extrusion_rate(self, extrusion_rate=None):
        if extrusion_rate is not None:
            self._extrusion_rate = extrusion_rate
        else:
            area = self._path_width*self._path_height
            # m3
            nozzle_size = 0.007
            volume = area*nozzle_size
            # profile must be achieved within length of the nozzle
            self._extrusion_rate = (volume*1000)/((self._robot_velocity*1000)/60)

    @property
    def path_profile(self):
        if (None not in [self._robot_velocity, self._extrusion_rate]
           and None in [self.path_width, self.path_height]):
            self.path_profile()
        elif None in [self.path_width, self.path_height]:
            print("Path profile is not set, and cannot be calculated!")
        return self._path_width, self._path_height

    @path_profile.setter
    def path_profile(self, path_width=None, path_height=None):
        if None not in [path_width, path_height]:
            self._path_width = path_width
            self._path_height = path_height
        else:
            velocity = (self.robot_velocity/1000)*60
            volume = (velocity*self._extrusion_rate)/1000
            nozzle_size = 0.007
            area = volume/nozzle_size
            if path_width is None and path_height is None:
                path_heights = range(0.002, 0.006, 0.001)
                for h in path_heights:
                    w = area/h
                    if w > 0.007 and w < 0.014:
                        self._path_width = w
                        self._path_height = h
                        break
                if self._path_height is None and self._path_width is None:
                    path_widths = range(0.007, 0.014, 0.0001)
                    for w in path_widths:
                        h = area/w
                        if h > 0.002 and h < 0.006:
                            self._path_width = w
                            self._path_height = h
                            break
            elif path_width is None:
                self._path_height = path_height
                self._path_width = area/path_height
                if self._path_width < 0.007:
                    print("calculated path width smaller than nozzle size")
                elif self._path_width > 0.014:
                    print("calculated path width larger than twice the nozzle size")

            elif path_height is None:
                self._path_width = path_width
                self._path_height = area/path_width
                if self._path_height < 0.002:
                    print("calculated path height smaller than two millimeter")
                elif self._path_height > 0.007:
                    print("calculated path height larger than the nozzle diameter")
    
    def transform(self, T):
        self.frame.transform(T)
    
    def transformed(self, T):
        node = self.copy()
        node.transform(T)
        return node