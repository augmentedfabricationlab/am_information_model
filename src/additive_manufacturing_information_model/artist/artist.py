from compas_ghpython.artists import NetworkArtist

class FabricationArtist(NetworkArtist):
    """Rudimentary model artist for GHpython
    """

    def draw_nodes(self, keys=None):
        yield self.draw_vertices(keys=keys)

    def draw_node(self, key):
        yield self.draw_vertices(keys=key)

    def draw_edge(self, key):
        yield self.draw_edges(keys=key)
