from .graph import ExtendedGraph

from compas.geometry import Frame

__all__ = [
    'InformationModel'
]


class InformationModel(ExtendedGraph):
    def __init__(self, name="InformationModel", **kwargs):
        super(InformationModel, self).__init__(name, *kwargs)
        self.attributes.update({
            "_last_element" : None
        })

    def robots(self, data=False):
        return self.get_nodes_where({"node_type": "robot"}, data)

    def elements(self, data=False):
        return self.get_nodes_where({"node_type": "element"}, data, "element")

    def get_robot(self, key):
        return self.get_node(key, "robot")

    def get_element(self, key):
        return self.get_node(key, "element")

    def add_robot(self, robot, key=None):
        # if robots is not an empty list
        if self.robots() and key is None:
            key = self.get_next_key(self.robots(), "robot_")
        elif key in self.robots():
            print("Key already in database, value is overwritten")
        self.add_node(key, node_type="robot", robot=robot)

    def add_element(self, element, key=None,
                    parent_element="last", parent_robot="any"):
        self.add_named_node(element, key, parent_element)



# if __name__ == "__main__":
#     from compas.geometry import Frame
#     from compas.geometry import Translation
#     from am_information_model.model import Path, Node, Element

#     frames = [Frame.worldXY()]*5
    
#     nodes = []
#     for i,frame in enumerate(frames):
#         nodes.append(Node(frame=frame))
#     path = Path.from_nodes(nodes)

#     layers = 15
#     layer_height = 0.005
#     element = Element()

#     for l in range(layers):
#         T = Translation.from_vector([0,0,layer_height*l])
#         new_path = path.transformed(T)
#         element.add_path(new_path)
#         print(new_path.get_node("node_0", True, "node")[1].frame)

#     print(element.data)