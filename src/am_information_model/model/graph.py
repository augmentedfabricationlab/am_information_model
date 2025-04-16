import warnings
from compas.datastructures import Graph


__all__ = ['ExtendedGraph']


class ExtendedGraph(Graph):
    def __init__(self, name="ExtendedGraph", **kwargs):
        super(ExtendedGraph, self).__init__(name=name, **kwargs)
        self.attributes["obj_type"] = name
        self.default_node_attributes = {}
        self.default_edge_attributes = {}
        self.key = kwargs.get("key")

    # @classmethod
    # def __from_data__(cls, data):
    #     super(ExtendedGraph, cls).__from_data__(data)

    def get_node(self, key, attr="node"):
        if self.has_node(key):
            return self.node_attribute(key, attr)
        else:
            return None

    def get_id(self, key):
        return int(key.split('_')[-1])

    def get_ids(self, keys):
        id_list = []
        for key in keys:
            id_list.append(self.get_id(key))
        
        if not id_list:
            return [-1]
        return id_list

    def get_key(self, id="first"):
        keys = self.nodes()
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
    
    def get_last_key(self, node_type="node"):
        return self.attributes.get("_last_{}".format(node_type))

    def get_next_key(self, keys, prefix=""):
        id = max(list(self.get_ids(keys)))+1
        return id

    def add_named_node(self, obj, key=None):
        # Get object type
        obj_type = obj.attributes.get("obj_type")
        # Generate key
        if key is None:
            keys = list(self.objects(obj_type))
            if keys == []:
                key = 0
            else:
                key = max([k for k in keys])+1
        else:
            if self.has_node(key):
                warnings.warn(f"Node with key {key} already exists.")
            
        # Add the node
        node = self.add_node(key, attr_dict={obj_type: obj})
        
        # Tracking last added object of type
        if isinstance(key, int):
            id = key
        else:
            id = self.get_id(key)
        
        self.attributes.update({f"_last_{obj_type}": id})
        return key

    def objects(self, obj_type="node", data=False):
        for key in self.nodes():
            node_attrs = self.node_attributes(key)
            if node_attrs.get(obj_type):
                if data:
                    yield key, node_attrs[obj_type]
                else:
                    yield key
    

if __name__ == "__main__":
    graph = Graph()

    graph.to_json("graph_test.json")
    new_graph = Graph.from_json("graph_test.json")
    assert graph == new_graph