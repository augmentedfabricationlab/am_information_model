
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
        # rvel = self.attributes.get("robot_velocity")
        # if (None not in [self.path_width, self.path_height,
        #                  self.extrusion_rate]
        #    and rvel is None):
        #     self.attributes["robot_velocity"] = self.calculate_robot_velocity()
        # elif rvel is None:
        #     print("Robot velocity is not set, and cannot be calculated!")
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
        # erate = self.attributes.get("extrusion_rate")
        # if (None not in [self.path_width, self.path_height,
        #                  self.robot_velocity]
        #    and erate is None):
        #     self.attributes["extrusion_rate"] = self.calculate_extrusion_rate()
        # elif erate is None:
        #     print("Extrusion rate is not set, and cannot be calculated!")
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
    
    def transform(self, T):
        self.frame.transform(T)
    
    def transformed(self, T):
        node = self.copy()
        node.transform(T)
        return node