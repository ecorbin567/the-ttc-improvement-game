"""
Converts a NetworkX graph into a list of plotly Scatters.
Used for visualizing subway data.
"""

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
                    max_vertices: int = 5000) -> list[Scatter]:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
    """
    graph_nx = graph.to_networkx(max_vertices)

    x_values = [graph_nx.nodes[k]['position'][0] for k in graph_nx.nodes]
    y_values = [graph_nx.nodes[k]['position'][1] for k in graph_nx.nodes]

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
        x_edges += [graph_nx.nodes[edge[0]]['position'][0], graph_nx.nodes[edge[1]]['position'][0], None]
        y_edges += [graph_nx.nodes[edge[0]]['position'][1], graph_nx.nodes[edge[1]]['position'][1], None]

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
