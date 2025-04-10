
from compas.data import Data
from .graph import ExtendedGraph
from compas.geometry import Frame
from compas_robots import Configuration

__all__ = [
    'Node'
]

class Node(ExtendedGraph):
    DATASCHEMA = {
        "type": "object",
        "properties": {
            "attributes": {"type": "object"},
        },
        "required": [
            "attributes",
        ],
    }

    def __init__(self, name="path_node", frame=None, **kwargs):
        super(Node, self).__init__(name, **kwargs)

        self.frame = frame
        self.configuration = None
        self.attributes.update({
            "obj_type" : name,
            "state" : None,
            "nozzle_size" : None,
            "path_width" : None,
            "path_height" : None,
            "extrusion_rate" : None,
            "robot_velocity" : None
        })
        self.attributes.update(kwargs)
    
    @property
    def frame(self):
        return self.attributes.get("frame")
    @frame.setter
    def frame(self, frame):
        if isinstance(frame, Frame):
            self.attributes["frame"] = frame
        elif isinstance(frame, dict):
            self.attributes["frame"] = Frame.from_data(frame)

    @property
    def configuration(self):
        return self.attributes.get("configuration")
    @configuration.setter
    def configuration(self, configuration):
        if isinstance(configuration, Configuration):
            self.attributes["configuration"] = configuration
        elif isinstance(configuration, dict):
            self.attributes["configuration"] = Configuration.from_data(configuration)


    @property
    def nozzle_size(self):
        return self.attributes.get("nozzle_size")
    @nozzle_size.setter
    def nozzle_size(self, nozzle_size):
        self.attributes["nozzle_size"] = nozzle_size
    
    @property
    def path_width(self):
        return self.attributes.get("path_width")
    @path_width.setter
    def path_width(self, path_width):
        self.attributes["path_width"] = path_width
    
    @property
    def path_height(self):
        return self.attributes.get("path_height")
    @path_height.setter
    def path_height(self, path_height):
        self.attributes["path_height"] = path_height

    @property
    def robot_velocity(self):
        rvel = self.attributes.get("robot_velocity")
        if (None not in [self.path_width, self.path_height,
                         self.extrusion_rate]
           and rvel is None):
            self.attributes["robot_velocity"] = self.calculate_robot_velocity()
        elif rvel is None:
            print("Robot velocity is not set, and cannot be calculated!")
        return self.attributes.get("robot_velocity")
    
    @robot_velocity.setter
    def robot_velocity(self, robot_velocity):
        self.attributes["robot_velocity"] = robot_velocity

    def calculate_robot_velocity(self):
        area = self.path_width*self.path_height       # m3
        nozzle_size = self.nozzle_size
        volume = area*nozzle_size
        # profile must be achieved within length of the nozzle
        velocity = (volume*1000)/self.extrusion_rate   # m/min
        return (velocity*1000)/60       # mm/s

    @property
    def extrusion_rate(self):
        erate = self.attributes.get("extrusion_rate")
        if (None not in [self.path_width, self.path_height,
                         self.robot_velocity]
           and erate is None):
            self.attributes["extrusion_rate"] = self.calculate_extrusion_rate()
        elif erate is None:
            print("Extrusion rate is not set, and cannot be calculated!")
        return self.attributes.get("extrusion_rate")

    @extrusion_rate.setter
    def extrusion_rate(self, extrusion_rate):
        self.attributes["extrusion_rate"] = extrusion_rate        

    def calculate_extrusion_rate(self):
        area = self.path_width*self.path_height     # m3
        nozzle_size = 0.007
        volume = area*nozzle_size
        # profile must be achieved within length of the nozzle
        return (volume*1000)/((self._robot_velocity*1000)/60)

    # @property
    # def path_profile(self):
    #     if (None not in [self.robot_velocity, self.extrusion_rate]
    #        and None in [self.path_width, self.path_height]):
    #         self.path_profile()
    #     elif None in [self.path_width, self.path_height]:
    #         print("Path profile is not set, and cannot be calculated!")
    #     return self._path_width, self._path_height

    # @path_profile.setter
    # def path_profile(self, path_width=None, path_height=None):
    #     if None not in [path_width, path_height]:
    #         self._path_width = path_width
    #         self._path_height = path_height
    #     else:
    #         velocity = (self.robot_velocity/1000)*60
    #         volume = (velocity*self._extrusion_rate)/1000
    #         nozzle_size = 0.007
    #         area = volume/nozzle_size
    #         if path_width is None and path_height is None:
    #             path_heights = range(0.002, 0.006, 0.001)
    #             for h in path_heights:
    #                 w = area/h
    #                 if w > 0.007 and w < 0.014:
    #                     self._path_width = w
    #                     self._path_height = h
    #                     break
    #             if self._path_height is None and self._path_width is None:
    #                 path_widths = range(0.007, 0.014, 0.0001)
    #                 for w in path_widths:
    #                     h = area/w
    #                     if h > 0.002 and h < 0.006:
    #                         self._path_width = w
    #                         self._path_height = h
    #                         break
    #         elif path_width is None:
    #             self._path_height = path_height
    #             self._path_width = area/path_height
    #             if self._path_width < 0.007:
    #                 print("calculated path width smaller than nozzle size")
    #             elif self._path_width > 0.014:
    #                 print("calculated path width larger than twice the nozzle size")

    #         elif path_height is None:
    #             self._path_width = path_width
    #             self._path_height = area/path_width
    #             if self._path_height < 0.002:
    #                 print("calculated path height smaller than two millimeter")
    #             elif self._path_height > 0.007:
    #                 print("calculated path height larger than the nozzle diameter")
    
    def transform(self, T):
        self.frame.transform(T)
    
    def transformed(self, T):
        node = self.copy()
        node.transform(T)
        return node