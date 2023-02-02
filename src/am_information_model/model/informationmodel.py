from am_information_model.model import ExtendedGraph

from compas.geometry import Frame
from compas.geometry import Transformation

from compas.datastructures import Graph, Datastructure


__all__ = [
    'InformationModel'
]


class ExtendedGraph(Graph):
    def __init__(self, name="ExtendedGraph"):
        super(ExtendedGraph, self).__init__(name)

    def get_nodes_where(self, arg, data=False, attr=None):
        for key in self.nodes_where(arg):
            if data:
                yield key, self.node_attribute(key, attr)
            else:
                yield key

    def get_node(self, key, data=False, attr=None):
        if self.has_node(key):
            if data:
                return key, self.node_attribute(key, attr)
            else:
                return key
        else:
            return None

    def get_id(self, key):
        return int(key.split('_')[-1])

    def get_ids(self, keys):
        for key in keys:
            last = int(key.split('_')[-1])
            yield last
        if 'last' not in locals():
            yield -1

    def get_key(self, keys, id="first"):
        if id == "first":
            return next(keys)
        elif id == "last":
            for key in keys:
                pass
            if 'key' not in locals():
                key = None
            return key
        else:
            for key in keys:
                if id == self.get_id(key):
                    return key
            else:
                # No corresponding id was found
                raise IndexError

    def create_key(self, id, prefix=""):
        if prefix == "":
            return id
        else:
            return prefix+str(id)

    # def get_last_key(self, keys):
    #     return self.get_key(keys, "last")
    
    def get_last_key(self, node_type="node"):
        return getattr(self, "_last_{}".format(node_type))

    def get_next_key(self, keys, prefix=""):
        id = max(list(self.get_ids(keys)))+1
        return self.create_key(id, prefix)

    def add_named_node(self, object, key=None, parent_object="last"):
        if parent_object == "last":
            parent_object = self.get_last_key(object.attributes.get("name"))
        if self.objects(object.name) and key is None:
            key = self.get_next_key(self.objects(object.name), object.name+'_')
        elif key in self.objects(object.name):
            print("Key already in database, value is overwritten")
        self.add_node(key, node_type=object.name, attr_dict={object.attributes.get("name"): object})
        if parent_object is not None:
            self.add_edge(parent_object, key)

    def objects(self, obj_type="node", data=False):
        return self.get_nodes_where({"node_type": obj_type}, data, obj_type)


class InformationModel(ExtendedGraph):
    def __init__(self, name="InformationModel"):
        super(InformationModel, self).__init__(name)
        self._last_element = None

    def robots(self, data=False):
        return self.get_nodes_where({"node_type": "robot"}, data)

    def elements(self, data=False):
        return self.get_nodes_where({"node_type": "element"}, data)

    def get_robot(self, key, data=False):
        self.get_node(key, data, "robot")

    def get_element(self, key, data=False):
        self.get_node(key, data, "element")

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
        self._last_element = key



if __name__ == "__main__":
    from compas.geometry import Frame
    from compas.geometry import Translation

    frames = [Frame.worldXY()]*5
    
    nodes = []
    for i,frame in enumerate(frames):
        nodes.append(Node(frame=frame))
    path = Path.from_nodes(nodes)

    layers = 15
    layer_height = 0.005
    element = Element()

    for l in range(layers):
        T = Translation.from_vector([0,0,layer_height*l])
        new_path = path.transformed(T)
        element.add_path(new_path)
        print(new_path.get_node("node_0", True, "node")[1].frame)

    print(element.data)