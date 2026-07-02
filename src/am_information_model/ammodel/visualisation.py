import networkx as nx
import matplotlib.pyplot as plt

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import bounding_box

from .model import HIERARCHY

__all__ = ["Visualizer"]


class Visualizer:
    def __init__(self, model):
        self.model = model

    def _to_networkx(self):
        graph = nx.DiGraph()

        for key in self.model._graph.nodes():
            node_type = self.model._graph.node_attribute(key, "node_type")
            graph.add_node(
                key,
                node_type=node_type,
                label="{}\n{}".format(node_type, key[:8]),
            )

        for u, v in self.model._graph.edges():
            graph.add_edge(
                u,
                v,
                edge_type=self.model._graph.edge_attribute((u, v), "edge_type"),
                seq=self.model._graph.edge_attribute((u, v), "seq"),
            )

        return graph

    def _tree_layout(self, dx=3.0, dy=1.5):
        pos = {}
        roots = [key for key in self.model._graph.nodes() if self.model._parent(key)[0] is None]

        def add_subtree(node_key, depth, row):
            pos[node_key] = (depth * dx, -row * dy)

            next_row = row
            node_type = self.model._node_type(node_key)

            for child_type in HIERARCHY.get(node_type, []):
                for child_key, _ in self.model.ordered_children(node_key, child_type):
                    next_row += 1
                    next_row = add_subtree(child_key, depth + 1, next_row)

            return next_row

        row = 0
        for root in roots:
            row = add_subtree(root, 0, row)
            row += 1

        return pos

    def visualise_matplotlib(self, dx=3.0, dy=1.5, figsize=(12, 8), show_seq=True, savepath=None):
        graph = self._to_networkx()
        pos = self._tree_layout(dx=dx, dy=dy)

        fig, ax = plt.subplots(figsize=figsize)

        color_map = {
            "robot": "#f4a261",
            "element": "#2a9d8f",
            "path": "#e9c46a",
            "waypoint": "#90caf9",
        }

        node_colors = [
            color_map.get(graph.nodes[node].get("node_type"), "#cccccc")
            for node in graph.nodes()
        ]

        nx.draw_networkx_edges(
            graph,
            pos,
            ax=ax,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=16,
            edge_color="#666666",
            width=1.5,
        )

        nx.draw_networkx_nodes(
            graph,
            pos,
            ax=ax,
            node_color=node_colors,
            node_size=1800,
            edgecolors="#333333",
            linewidths=1.0,
        )

        labels = {node: graph.nodes[node]["label"] for node in graph.nodes()}
        nx.draw_networkx_labels(
            graph,
            pos,
            labels=labels,
            ax=ax,
            font_size=8,
            font_color="#111111",
        )

        if show_seq:
            edge_labels = {
                (u, v): data["seq"]
                for u, v, data in graph.edges(data=True)
                if data.get("seq") is not None
            }
            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels=edge_labels,
                ax=ax,
                font_size=8,
                rotate=False,
            )

        ax.set_title(self.model.name)
        ax.axis("off")
        ax.set_aspect("equal")

        if pos:
            xs = [p[0] for p in pos.values()]
            ys = [p[1] for p in pos.values()]
            pad_x = dx * 0.8
            pad_y = dy * 0.8
            ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
            ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

        ax.margins(0.1)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

        if savepath:
            fig.savefig(savepath, dpi=200, bbox_inches="tight", pad_inches=0.3)

        plt.show()
        return fig, ax

    # --- Grasshopper spatial export ---

    def _waypoint_point(self, waypoint):
        frame = getattr(waypoint, "frame", None)
        return frame.point if frame else None

    def _path_waypoint_points(self, path_key):
        points = []
        for waypoint_key, waypoint in self.model.path_waypoints(path_key):
            pt = self._waypoint_point(waypoint)
            if pt is not None:
                points.append((waypoint_key, pt))
        return points

    def _node_label(self, key):
        obj = self.model.get_object(key)
        name = getattr(obj, "name", None)
        node_type = self.model._node_type(key)
        if name:
            return "{}: {}".format(node_type, name)
        return "{}\n{}".format(node_type, key[:8])

    def _element_bbox_lines(self, element_key):
        element = self.model.get_object(element_key)

        coords = []

        mesh = getattr(element, "mesh", None)
        if mesh is not None:
            try:
                coords.extend(mesh.vertices_attributes("xyz"))
            except Exception:
                pass

        if not coords:
            for path_key, _ in self.model.element_paths(element_key):
                for _, pt in self._path_waypoint_points(path_key):
                    coords.append([pt.x, pt.y, pt.z])

        if not coords:
            frame = getattr(element, "frame", None)
            if frame:
                p = frame.point
                coords.append([p.x, p.y, p.z])

        if not coords:
            return [], None

        corners = [Point(*xyz) for xyz in bounding_box(coords)]

        # Corner index convention from compas.geometry.bounding_box
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]

        lines = [Line(corners[i], corners[j]) for i, j in edges]
        center = Point(
            sum(p.x for p in corners) / 8.0,
            sum(p.y for p in corners) / 8.0,
            sum(p.z for p in corners) / 8.0,
        )
        return lines, center

    def gh_spatial_visualisation_data(self):
        """Return GH-friendly spatial geometry and relation geometry.

        Returns
        -------
        tuple
            (
                waypoint_points,
                path_polylines,
                element_bbox_lines,
                relation_lines,
                relation_labels,
                relation_label_points,
                geometry_color_rgb,
                relation_color_rgb,
            )
        """
        try:
            from compas_rhino.conversions import line_to_rhino
            from compas_rhino.conversions import point_to_rhino
            from compas_rhino.conversions import polyline_to_rhino

            def to_rhino_point(point):
                return point_to_rhino(point)

            def to_rhino_line(line):
                return line_to_rhino(line)

            def to_rhino_polyline(polyline):
                return polyline_to_rhino(polyline)

        except Exception:
            # Fallback for non-Rhino contexts.
            def to_rhino_point(point):
                return point

            def to_rhino_line(line):
                return line

            def to_rhino_polyline(polyline):
                return polyline

        geometry_color_rgb = [244, 103, 103]
        relation_color_rgb = [11, 152, 152]

        waypoint_points = []
        path_polylines = []
        element_bbox_lines = []

        # Node anchors are used to draw relation lines spatially.
        anchors = {}

        for waypoint_key, waypoint in self.model.waypoints():
            pt = self._waypoint_point(waypoint)
            if pt is None:
                continue
            waypoint_points.append(pt)
            anchors[waypoint_key] = pt

        for path_key, _ in self.model.paths():
            wp_data = self._path_waypoint_points(path_key)
            if not wp_data:
                continue

            points = [pt for _, pt in wp_data]
            if len(points) >= 2:
                path_polylines.append(Polyline(points))

            anchors[path_key] = Point(
                sum(pt.x for pt in points) / len(points),
                sum(pt.y for pt in points) / len(points),
                sum(pt.z for pt in points) / len(points),
            )

        for element_key, _ in self.model.elements():
            bbox_lines, center = self._element_bbox_lines(element_key)
            element_bbox_lines.extend(bbox_lines)
            if center is not None:
                anchors[element_key] = center

        relation_lines = []

        # Keep return signature stable: relation_labels/points also include node labels.
        relation_labels = []
        relation_label_points = []

        # Add labels for entities first (waypoints, paths, elements) at anchor points.
        for key, anchor in anchors.items():
            relation_labels.append(self._node_label(key))
            relation_label_points.append(anchor)

        for parent_key in self.model._graph.nodes():
            parent_anchor = anchors.get(parent_key)
            if parent_anchor is None:
                continue

            parent_type = self.model._node_type(parent_key)
            for child_type in HIERARCHY.get(parent_type, []):
                for child_key, _ in self.model.ordered_children(parent_key, child_type):
                    child_anchor = anchors.get(child_key)
                    if child_anchor is None:
                        continue

                    relation_lines.append(Line(parent_anchor, child_anchor))

                    seq = self.model._graph.edge_attribute((parent_key, child_key), "seq")
                    if seq is not None:
                        relation_labels.append("seq {}".format(seq))
                        relation_label_points.append(
                            Point(
                                0.5 * (parent_anchor.x + child_anchor.x),
                                0.5 * (parent_anchor.y + child_anchor.y),
                                0.5 * (parent_anchor.z + child_anchor.z),
                            )
                        )

        rhino_waypoint_points = [to_rhino_point(pt) for pt in waypoint_points]
        rhino_path_polylines = [to_rhino_polyline(polyline) for polyline in path_polylines]
        rhino_element_bbox_lines = [to_rhino_line(line) for line in element_bbox_lines]
        rhino_relation_lines = [to_rhino_line(line) for line in relation_lines]
        rhino_relation_label_points = [to_rhino_point(pt) for pt in relation_label_points]

        return (
            rhino_waypoint_points,
            rhino_path_polylines,
            rhino_element_bbox_lines,
            rhino_relation_lines,
            relation_labels,
            rhino_relation_label_points,
            geometry_color_rgb,
            relation_color_rgb,
        )
