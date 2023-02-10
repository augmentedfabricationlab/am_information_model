from compas.datastructures import Graph


__all__ = ['ExtendedGraph']


class ExtendedGraph(Graph):
    def __init__(self, name="ExtendedGraph", **kwargs):
        super(ExtendedGraph, self).__init__(name, *kwargs)

    def get_nodes_where(self, arg, data=False, attr=None):
        for key in self.nodes_where(arg):
            if data:
                yield key, self.node_attribute(key, attr)
            else:
                yield key

    def get_node(self, key, attr="node"):
        if self.has_node(key):
            return self.node_attribute(key, attr)
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
        return self.create_key(id, prefix)

    def add_named_node(self, object, key=None, parent_object="last"):
        if parent_object == "last":
            parent_object = self.get_last_key(object.attributes.get("name"))
        if self.objects(object.name) and key is None:
            key = self.get_next_key(self.objects(object.name), object.name+'_')
        elif key in self.objects(object.name):
            print("Key already in database, value is overwritten")
        self.add_node(key, node_type=object.name, attr_dict={object.attributes.get("name"): object})
        self.attributes.update({"_last_{}".format(object.attributes.get("name")): key})
        if parent_object is not None:
            self.add_edge(parent_object, key)

    def objects(self, obj_type="node", data=False):
        return self.get_nodes_where({"node_type": obj_type}, data, obj_type)