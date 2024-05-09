"""
Models TTC and Bike Share Toronto ridership data using a graph that incorporates
subway stops, aboveground transit (streetcar and bus) stops, and bike docking stations.
"""
from __future__ import annotations
import csv
from typing import Any, Optional
import statistics
import networkx as nx


class _Vertex:
    """
    A vertex in a transit graph. Each vertex represents a stop, aboveground transit line, or bike docking station,
    and an edge between vertices represents a connection between two stops.
    """
    item: Any
    lines: set[str]
    usage: int
    neighbours: set[_Vertex]
    position: tuple[int, int]

    def __init__(self, item: Any, lines: set[str], usage: int, position: tuple[int, int] = (0, 0)) -> None:
        """Initialize a new vertex with the given item, line, and usage.

        This vertex is initialized with no neighbours
        """
        self.item = item
        self.lines = lines
        self.usage = usage
        self.neighbours = set()
        self.position = position

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def check_connected(self, target_item: Any, visited: set[_Vertex]) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited.

        Preconditions:
            - self not in visited
        """
        if self.item == target_item:
            return True
        else:
            visited.add(self)
            for u in self.neighbours:
                if u not in visited:
                    if u.check_connected(target_item, visited):
                        return True

            return False

    def check_connected_path(self, target_item: Any, visited: set[_Vertex]) -> Optional[list]:
        """Return a path between self and the vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited.

        The returned list contains the ITEMS stored in the _Vertex objects, not the _Vertex
        objects themselves. The first list element is self.item, and the last is target_item.
        If there is more than one such path, any of the paths is returned.

        Return None if no such path exists (i.e., if self is not connected to a vertex with
        the target_item). Note that this is very similar to _Vertex.check_connected, except
        this method returns an Optional[list] instead of a bool.

        Go to Graph.connected_path() for doctests.

        Preconditions:
            - self not in visited
        """
        if self.item == target_item:
            return [self.item]

        path = [self.item]
        visited.add(self)

        for u in self.neighbours:
            if u not in visited:
                neighbours_path = u.check_connected_path(target_item, visited)
                if neighbours_path:
                    return path + neighbours_path

        return None


class Graph:
    """
    A transit graph. Represented by a dictionary of subway stations, aboveground lines, and bike docking stations.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, lines: set[str], usage: int, position: tuple[int, int]) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, lines, usage, position)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        elif item1 not in self._vertices:
            raise ValueError(f"no station called {item1}")
        else:
            raise ValueError(f"no station called {item2}")

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, lines: set[str]) -> set:
        """Return a set of all vertices in this graph.

        If lines != set(), only return the vertices of the given line(s).
        """
        if lines != set():
            return {v for v in self._vertices.values() if any(line in v.lines for line in lines)}
        else:
            return set(self._vertices.values())

    def connected_path(self, item1: Any, item2: Any) -> Optional[list]:
        """Return a path between item1 and item2 in this graph.

        The returned list contains the ITEMS along the path.
        Return None if no such path exists, including when item1 or item2
        do not appear as vertices in this graph.
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.connected_path('CHRISTIE', 'ST. CLAIR WEST')
        ['CHRISTIE', 'BATHURST', 'SPADINA', 'DUPONT', 'ST. CLAIR WEST']
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected_path(item2, set())
        else:
            return None

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """
        Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note: This implementation passes the lines and usage parameters into NetworkX,
        which allows the user to see those parameters when they hover over a node in the graph
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.lines, usage=round(v.usage), position=v.position)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(v.item, kind=v.lines, usage=round(v.usage), position=v.position)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def spread_of_ridership(self, lines: set[str]) -> float:
        """
        Calculate the spread of ridership of this graph by finding the standard deviation
        of the daily usage of every vertex in the graph.
        If lines != set(), spread will be calculated for the lines given only.
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.spread_of_ridership(set())
        58583.62942764618
        """
        if lines != set():
            return statistics.pstdev([self._vertices[v].usage for v in self._vertices if v.line in lines])
        else:
            return statistics.pstdev([self._vertices[v].usage for v in self._vertices])

    def add_station(self, name: str, neighbours: set[str], lines: set[str]) -> None:
        """
        Add a new station to the transit graph, and update the usage numbers for this station and
        connected stations accordingly.
        We will assume that a new station takes 1/3 of the ridership from each connected station.

        Preconditions:
            - all([neighbour in self._vertices for neighbour in neighbours])
            - all([line in self.get_all_lines() for line in lines])
            - all(any([line in self._vertices[neighbour].lines for neighbour in neighbours) for line in lines])
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph = load_extras(my_graph, 'bikeshare_cleaned.csv', 'surface.csv')
        >>> my_graph.add_station('New Bike Share Station', set(), {'Bike Share'})
        >>> stations = [v.item for v in my_graph.get_all_vertices(set())]
        >>> 'New Bike Share Station' in stations
        True
        >>> my_graph.get_neighbours('New Bike Share Station')
        set()
        >>> my_graph.add_station('chrossington', {'CHRISTIE', 'OSSINGTON'}, {'2 Bloor-Danforth'})
        >>> christie_neighbours = my_graph.get_neighbours('CHRISTIE')
        >>> 'chrossington' in christie_neighbours
        True
        >>> 'OSSINGTON' in christie_neighbours
        False
        """
        position = (0, 0)

        if len(neighbours) == 0:
            position = (-20, 20)
        elif len(neighbours) == 1:
            for nb in neighbours:
                nb_vert = self._vertices[nb]
                nb_x = nb_vert.position[0]
                nb_y = nb_vert.position[1]
                if len(nb_vert.neighbours) == 0:
                    position = (nb_x + 1, nb_y)
                else:
                    x_diffs = []
                    y_diffs = []
                    for nb2_vert in nb_vert.neighbours:
                        nb2_x = nb2_vert.position[0]
                        nb2_y = nb2_vert.position[1]
                        x_diffs.append(nb_x - nb2_x)
                        y_diffs.append(nb_y - nb2_y)
                    if len(nb_vert.neighbours) == 1:
                        position = (nb_x + x_diffs[0], nb_y + y_diffs[0])
                    else:
                        diffs = []
                        for i in range(len(x_diffs)):
                            diffs.append((x_diffs[i], y_diffs[i]))
                        if all(diff != (1, 0) for diff in diffs):
                            position = (nb_x + 1, nb_y)
                        elif all(diff != (-1, 0) for diff in diffs):
                            position = (nb_x - 1, nb_y)
                        elif all(diff != (0, 1) for diff in diffs):
                            position = (nb_x, nb_y + 1)
                        else:
                            position = (nb_x, nb_y - 1)
        else:
            position = get_midpoint([self._vertices[neighbour].position for neighbour in neighbours])

        self.add_vertex(name, lines, 0, position)

        usage = 0
        for neighbour in neighbours:
            for neighbour2 in neighbours:
                if self.adjacent(neighbour, neighbour2):
                    neighbour_vertex = self._vertices[neighbour]
                    neighbour2_vertex = self._vertices[neighbour2]
                    neighbour_vertex.neighbours.remove(neighbour2_vertex)
                    neighbour2_vertex.neighbours.remove(neighbour_vertex)
            self.add_edge(name, self._vertices[neighbour].item)
            usage += round(self._vertices[neighbour].usage / 3)
            self._vertices[neighbour].usage *= (2 / 3)
        self._vertices[name].usage = usage

    def remove_station(self, name: str) -> None:
        """
        Remove a station from the transit graph, and update the usage numbers for this station and
        connected stations accordingly.
        Since a new station takes 1/3 of the ridership from each connected station, we will reverse the
        process for removal, with each neighbour station getting 3/2 of its original ridership.

        Preconditions:
            - name in self._vertices
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.add_station('ST. GEORGE 2.0', {'ST. GEORGE', 'SPADINA', 'MUSEUM'},
        ... {'1 Yonge-University', '2 Bloor-Danforth'})
        >>> stations = [v.item for v in my_graph.get_all_vertices(set())]
        >>> 'ST. GEORGE 2.0' in stations
        True
        >>> my_graph.remove_station('ST. GEORGE 2.0')
        >>> stations = [v.item for v in my_graph.get_all_vertices(set())]
        >>> 'ST. GEORGE 2.0' in stations
        False
        >>> 'SPADINA' in my_graph.get_neighbours('MUSEUM')
        True
        """
        for neighbour in self.get_neighbours(name):
            self._vertices[neighbour].usage += (self._vertices[name].usage / self._vertices[name].degree())
            for neighbour2 in self.get_neighbours(name):
                if neighbour2 not in self.get_neighbours(neighbour):
                    self.add_edge(neighbour, neighbour2)
                    for line in self._vertices[neighbour].lines:
                        self._vertices[neighbour2].lines.add(line)
                    self._vertices[neighbour].lines = self._vertices[neighbour2].lines
        for v in self._vertices:
            if self._vertices[name] in self._vertices[v].neighbours:
                self._vertices[v].neighbours.remove(self._vertices[name])
        del self._vertices[name]

    def add_line(self, name: str, stations: list[str]) -> None:
        """
        Add a new line to the transit graph, and update the usage numbers for this station and
        connected stations accordingly.
        We will assume that if this new line provides a faster way to get between endpoints than the
        way that already exists, each station on the new line will take 1/3 of the ridership from
        each station on the old path.

        Preconditions:
            - all([station in self._vertices for station in stations])
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.add_station('Mississauga 1', {'KIPLING'}, set())
        >>> my_graph.add_station('Mississauga 2', {'Mississauga 1'}, set())
        >>> my_graph.add_station('Mississauga 3', {'Mississauga 2'}, set())
        >>> my_graph.add_line('5 Mississauga', ['Mississauga 1', 'Mississauga 2', 'Mississauga 3'])
        >>> sauga = [v.item for v in my_graph.get_all_vertices({'5 Mississauga'})]
        >>> 'Mississauga 3' in sauga
        True
        >>> my_graph.add_line('Christie Pits', ['CHRISTIE', 'ST. CLAIR WEST'])
        >>> my_graph.adjacent('CHRISTIE', 'ST. CLAIR WEST')
        True
        """
        path_before = self.connected_path(stations[0], stations[len(stations) - 1])

        for station in stations:
            self._vertices[station].lines.add(name)

        for i in range(len(stations) - 2):
            if self._vertices[stations[i + 1]] not in self._vertices[stations[i]].neighbours:
                self.add_edge(stations[i + 1], stations[i])
        if self._vertices[stations[len(stations) - 1]] not in self._vertices[stations[len(stations) - 1]].neighbours:
            self.add_edge(stations[len(stations) - 2], stations[len(stations) - 1])

        if len(path_before) > len(stations):
            for station in path_before:
                self._vertices[station].usage *= (2 / 3)
            for station in stations:
                self._vertices[station].usage *= (3 / 2)

    def remove_line(self, name: str) -> None:
        """
        Remove a line from the transit graph.
        If a station is only serviced by this line, the station is removed.
        Preconditions:
            - name in self.get_all_lines()
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.add_station('Mississauga 1', {'KIPLING'}, set())
        >>> my_graph.add_station('Mississauga 2', {'Mississauga 1'}, set())
        >>> my_graph.add_station('Mississauga 3', {'Mississauga 2'}, set())
        >>> my_graph.add_line('5 Mississauga', ['KIPLING', 'Mississauga 1', 'Mississauga 2', 'Mississauga 3'])
        >>> my_graph.remove_line('5 Mississauga')
        >>> not_sauga = [v.item for v in my_graph.get_all_vertices(set())]
        >>> 'Mississauga 3' in not_sauga
        False
        >>> 'KIPLING' in not_sauga
        True
        """
        to_be_removed = set()
        line_to_be_removed = set()
        for v in self._vertices:
            if name in self._vertices[v].lines:
                if len(self._vertices[v].lines) == 1:
                    to_be_removed.add(v)
                else:
                    line_to_be_removed.add(v)
        for item in to_be_removed:
            self.remove_station(item)
        for item in line_to_be_removed:
            self._vertices[item].lines.remove(name)

    def get_all_lines(self) -> list[str]:
        """
        Returns a set of all lines in this graph. This is used in the interface to create drop-down menus.
        >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
        >>> my_graph.add_station('Mississauga 1', {'KIPLING'}, set())
        >>> my_graph.add_station('Mississauga 2', {'Mississauga 1'}, set())
        >>> my_graph.add_station('Mississauga 3', {'Mississauga 2'}, set())
        >>> my_graph.add_line('5 Mississauga', ['KIPLING', 'Mississauga 1', 'Mississauga 2', 'Mississauga 3'])
        >>> '5 Mississauga' in my_graph.get_all_lines()
        True
        """
        lst = [v.lines for v in self.get_all_vertices(set())]
        result = []
        for station in lst:
            for line in station:
                if line not in result:
                    result.append(line)
        return result


def get_midpoint(points: list[tuple[int, int]]) -> tuple[int, int]:
    """
    Helper function for add_station in the Graph class.
    Returns the midpoint of two or more stations, which helps determine the position of a new station.
    """
    mid = midpoint(points[0][0], points[0][1], points[1][0], points[1][1])

    if len(points) > 2:
        for point in points[2:]:
            mid = midpoint(mid[0], mid[1], point[0], point[1])

    return mid


def midpoint(x1, y1, x2, y2):
    """
    Helper function for get_midpoint, as defined above.
    Calculates the midpoint of two points (x1, y1) and (x2, y2).
    """
    return (x1 + x2) / 2, (y1 + y2) / 2


def load_subway_map(subway_file: str, lines_file: str) -> Graph:
    """
    Returns a Graph of subway data only. This is useful for the
    interactive component because it only works with subway data.
    >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
    >>> stations = [v.item for v in my_graph.get_all_vertices(set())]
    >>> 'DONLANDS' in stations
    True
    >>> usages = [v.usage for v in my_graph.get_all_vertices(set())]
    >>> 18996 in usages
    True
    """
    g = Graph()

    # subway
    with open(subway_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] in [a.item for a in g.get_all_vertices(set())]:
                c = [b for b in g.get_all_vertices(set()) if b.item == row[1]][0]
                c.lines.add(row[2])
                c.usage += int(row[5].strip())
            else:
                g.add_vertex(row[1], {row[2]}, int(row[5].strip()), (int(row[6]), int(row[7])))
    with open(lines_file, 'r') as file:
        reader = csv.reader(file)
        first = True
        for row in reader:
            if not first:
                for i in range(len(row) - 1):
                    g.add_edge(row[i], row[i + 1])
            first = False

    return g


def load_extras(g: Graph, bikeshare_file: str, surface_file: str) -> Graph:
    """
    Adds surface and Bike Share data to an existing Graph for analysis purposes.
    Not used in the visualization component, so positions don't matter and are hard-coded as (0, 0).
    >>> my_graph = load_subway_map('subway.csv', 'subway_lines.csv')
    >>> my_graph_extra = load_extras(my_graph, 'bikeshare_cleaned.csv', 'surface.csv')
    >>> surface_routes = [v.item for v in my_graph.get_all_vertices({'Surface'})]
    >>> 'Carlton' in surface_routes
    True
    """
    # bikeshare
    with open(bikeshare_file, 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if count != 0:  # gets around the beginning of the file
                g.add_vertex(row[1], {'Bike Share'}, int(row[2]), (0, 0))
            count += 1

    # surface
    with open(surface_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            g.add_vertex(row[1], {'Surface', f'{row[0]} {row[1]}'}, int(row[2].strip()), (0, 0))

    return g
