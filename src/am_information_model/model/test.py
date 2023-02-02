# from compas.datastructures import Graph

# def yieldkeys(nodes):
#     for key in nodes:
#         yield key

# ds = Graph()

# # robot_0 = ds.add_node("robot_0", node_type="robot", robot="robot_0")
# # robot_1 = ds.add_node("robot_1", node_type="robot", robot="robot_1")
# # robot_2 = ds.add_node("robot_2", node_type="robot", robot="robot_2")
# # robot_3 = ds.add_node("robot_3", node_type="robot", robot="robot_3")
# for i in range(100):
#     ds.add_node("robot_{}".format(i), node_type="robot", robot="robot_{}".format(i))
# nodes = ds.nodes_where({"node_type":"robot"})

# def get_first_last():
#     nodes = ds.nodes_where({"node_type":"robot"})
#     robots = yieldkeys(nodes)
#     first = last = next(robots)
#     for last in robots:
#         pass
#     return first, last

# def get_first_last_list():
#     nodes = ds.nodes_where({"node_type":"robot"})
#     robots = yieldkeys(nodes)
#     genlist = list(robots)
#     first = genlist[0]
#     last = genlist[-1]
#     return first, last

# def get_next_key(keys, prefix=""):
#     ids = [int(key.split('_')[-1]) for key in keys]
#     return prefix + str(max(ids)+1)

# def get_id(key):
#     return int(key.split('_')[-1])

# def get_key(keys, id="first"):
#     if id == "first":
#         return next(keys)
#     elif id == "last":
#         for key in keys:
#             pass
#         return key
#     else:
#         for key in keys:
#             if id == get_id(key):
#                 return key
#         else: 
#             # No corresponding id was found
#             raise IndexError

# def get_last_key(keys):
#     ids = [int(key.split('_')[-1]) for key in keys]
#     return keys[ids.index(max(ids))]

# testnones = [0,0,0,None]
# if not None in testnones:
#     print("No Nones!")