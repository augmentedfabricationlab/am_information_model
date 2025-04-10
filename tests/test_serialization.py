import os, sys

# Insert the absolute path to the src directory at the start of sys.path.
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

import unittest
import tempfile
from pathlib import Path

from am_information_model.model.informationmodel import InformationModel
from am_information_model.model.element import Element
from am_information_model.model.node import Node
from am_information_model.model.edge import Edge
from am_information_model.model.path import Path as Pathobject
from am_information_model.model.graph import ExtendedGraph

from compas.geometry import Frame, Point, Vector
from compas.data import Data
from compas.datastructures import Datastructure, Mesh, Graph

class TestNode(ExtendedGraph):
    def __init__(self, name="test_node", **kwargs):
        super(TestNode, self).__init__(name, **kwargs)
        # self.name = name
        # self.attributes["name"] = name
        # self.attributes["node_type"] = name
        # self.attributes = {}
        self.attributes["test_attr"] = "test_value"
    
    @classmethod
    def __from_data__(cls, data):
        return super(TestNode, cls).__from_data__(data)


class TestSerialization(unittest.TestCase):
    """Test serialization and deserialization of model classes."""
    
    def setUp(self):
        """Set up temporary directory for test files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = r"C:\Users\gido\Documents\workspace\am_information_model\tests\testdir"

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_graph_serialization(self):
        """Test Graph serialization and deserialization."""
        # Create test graph
        graph = Graph(name="test_graph")
        graph.default_node_attributes = {}
        graph.default_edge_attributes = {}
        
        # Add nodes
        graph.add_node(key=1, attr_dict={"data": "test_data_1"})
        graph.add_node(key=2, attr_dict={"data": 123})

        obj = TestNode(name="test_node")
        # obj.name = "test_node"
        obj_type = obj.attributes.get("obj_type")
        graph.add_node(key=3, attr_dict={obj_type: obj})
        
        
        # Add edge
        graph.add_edge(1, 2, attr_dict={"weight": 10.0})
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "graph.json")
        graph.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_graph = Graph.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(graph.name, restored_graph.name)
        self.assertEqual(len(list(graph.nodes())), len(list(restored_graph.nodes())))
        self.assertEqual(len(list(graph.edges())), len(list(restored_graph.edges())))
        self.assertEqual(graph.node_attribute(3, "attributes"), restored_graph.node_attribute(3, "attributes"))


    def test_extendedgraph_serialization(self):
        """Test ExtendedGraph serialization and deserialization."""
        # Create test graph
        graph = ExtendedGraph(name="test_graph")
        
        # Add nodes
        graph.add_node(key=1, attr_dict={"data": "test_data_1"})
        graph.add_node(key=2, attr_dict={"data": 123})


        obj = TestNode(name="test_node")
        # obj.name = "test_node"
        graph.add_named_node(obj=obj, key=3)
        
        # Add edge
        graph.add_edge(1, 2, attr_dict={"weight": 10.0})
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "extgraph.json")
        graph.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_graph = ExtendedGraph.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(graph.name, restored_graph.name)
        self.assertEqual(len(list(graph.nodes())), len(list(restored_graph.nodes())))
        self.assertEqual(len(list(graph.edges())), len(list(restored_graph.edges())))
        self.assertEqual(graph.node_attribute(3, "attributes"), restored_graph.node_attribute(3, "attributes"))


    def test_node_serialization(self):
        """Test Node serialization and deserialization."""
        # Create a test node
        node = Node(name="test_node", frame=Frame([0, 0, 0], [1, 0, 0], [0, 1, 0]))
        node.attributes["nozzle_size"] = "0.025"
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "node.json")
        node.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_node = Node.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(node.name, restored_node.name)
        self.assertEqual(node.attributes["nozzle_size"], restored_node.attributes["nozzle_size"])

    def test_edge_serialization(self):
        """Test Edge serialization and deserialization."""
        # Create test edge
        edge = Edge(u=1, v=2, name="test_edge")
        edge.attributes["weight"] = 5.0
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "edge.json")
        edge.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_edge = Edge.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(edge.name, restored_edge.name)
        self.assertEqual(edge.u, restored_edge.u)
        self.assertEqual(edge.v, restored_edge.v)
        self.assertEqual(edge.attributes["weight"], restored_edge.attributes["weight"])

    def test_path_serialization(self):
        """Test Path serialization and deserialization."""
        # Create test path
        frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        pathobj = Pathobject(name="test_path", frame=frame)
        pathobj.attributes["velocity"] = 100

        for i in range(4):
            point = Point(i, i, 0)
            vector = Vector(1, 0, 0)
            pathobj.add_node(key=i, attr_dict={"point": point, "vector": vector})
        # Test serialization
        json_path = os.path.join(self.test_dir, "path.json")
        pathobj.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        self.assertEqual(len(list(pathobj.nodes())), 4)
        
        # Test deserialization
        restored_path = Pathobject.from_json(str(json_path))
        # Test equality
        self.assertEqual(pathobj.name, restored_path.name)
        self.assertEqual(pathobj.attributes["velocity"], restored_path.attributes["velocity"])
        self.assertEqual(pathobj.frame.point, restored_path.frame.point)

    def test_element_serialization(self):
        """Test Element serialization and deserialization."""
        # Create test element with mesh
        frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        mesh = Mesh.from_vertices_and_faces(
            [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
            [[0, 1, 2, 3]]
        )
        element = Element.from_mesh(mesh, frame)
        
        # Add a path to the element
        # path = Pathobject(name="test_path", frame=frame)
        # element.add_path(path, key=0)
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "element.json")
        element.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_element = Element.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(element.frame.point, restored_element.frame.point)
        self.assertEqual(len(list(element.paths())), len(list(restored_element.paths())))

    def test_information_model_serialization(self):
        """Test InformationModel serialization and deserialization."""
        # Create test information model
        model = InformationModel(name="test_model")
        
        # Add an element
        frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        element = Element(name="test_element", frame=frame)
        model.add_element(element)
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "model.json")
        model.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_model = InformationModel.from_json(str(json_path))
        
        # Test equality
        self.assertEqual(model.name, restored_model.name)
        self.assertEqual(len(list(model.elements())), len(list(restored_model.elements())))

    def test_full_model_roundtrip(self):
        """Test a complete model roundtrip with nested objects."""
        # Create a comprehensive information model
        model = InformationModel(name="complex_model")
        
        # Add multiple elements with paths
        for i in range(3):
            frame = Frame([i, 0, 0], [1, 0, 0], [0, 1, 0])
            element = Element(name="element", frame=frame)
            
            # Add paths to element
            for j in range(2):
                path_frame = Frame([i, j, 0], [1, 0, 0], [0, 1, 0])
                path = Pathobject(name="path", frame=path_frame)
                element.add_path(path, key=None)
            
            model.add_element(element, key=None)
            
        # Add relationships between elements
        elements = list(model.elements(data=True))
        if len(elements) >= 2:
            model.add_edge(elements[0][0], elements[1][0], attr_dict={"relation": "next_to"})
        
        # Test serialization
        json_path = os.path.join(self.test_dir, "complex_model.json")
        model.to_json(str(json_path), pretty=True)
        self.assertTrue(Path(json_path).exists())
        
        # Test deserialization
        restored_model = InformationModel.from_json(str(json_path))
        
        # Verify model structure
        self.assertEqual(len(list(model.elements())), len(list(restored_model.elements())))
        self.assertEqual(len(list(model.edges())), len(list(restored_model.edges())))
        
        # Check paths in elements
        for element_key, element_data in restored_model.elements(data=True):
            element = element_data
            self.assertEqual(2, len(list(element.paths())))


if __name__ == "__main__":
    unittest.main()