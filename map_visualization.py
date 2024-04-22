"""
Converts a NetworkX graph into a list of plotly Scatters.
The function visualize_graph() is a heavily modified implementation of our visualizations of book data
from Exercises 3 and 4. Instead of returning a Figure, visualize_graph() returns a list of Scatters.
This allows the graph in the interactive component to be updated with each addition, instead of
making a new graph every time.
"""

import networkx as nx
from plotly.graph_objs import Scatter

import transit_map

# Colours for lines, based on the line colours the TTC uses.
LINE_1_COLOUR = 'rgb(255, 255, 0)'  # yellow
LINE_2_COLOUR = 'rgb(0, 181, 48)'  # green
LINE_4_COLOUR = 'rgb(181, 0, 114)'  # purpley-pink
BIKE_SHARE_COLOUR = 'rgb(254, 116, 77)'  # orange
# (a little bit lighter because it's very hard to tell the difference between red and regular orange)
SURFACE_COLOUR = 'rgb(255, 0, 0)'  # red
GENERAL_COLOUR = 'rgb(0, 0, 0)'  # black


def visualize_graph(graph: transit_map.Graph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 5000) -> list[Scatter]:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
    """
    graph_nx = graph.to_networkx(max_vertices)

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = [(f'{k}, '
               f'{' and '.join(str(n) for n in list(graph_nx.nodes[k]['kind'])) if len(list(graph_nx.nodes[k]['kind'])) > 0 else 'No Lines'}, '
               f'{graph_nx.nodes[k]['usage']} riders per day') for k in graph_nx.nodes]

    kinds = [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes]
    colours = [LINE_1_COLOUR if '1 Yonge-University' in kind
               else LINE_2_COLOUR if '2 Bloor-Danforth' in kind
               else LINE_4_COLOUR if '4 Sheppard' in kind
               else SURFACE_COLOUR if 'Surface' in kind
               else BIKE_SHARE_COLOUR if 'Bike Share' in kind
               else GENERAL_COLOUR for kind in kinds]

    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=GENERAL_COLOUR, width=3),
                     hoverinfo='none',
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=5,
                                 color=colours,
                                 line=dict(color=colours, width=2)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    return [trace3, trace4]


if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'W0221'],
        'extra-imports': ['plotly', 'networkx', 'transit_map'],
        'max-nested-blocks': 5
    }, output='pyta_report.html')
