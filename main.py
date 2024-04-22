"""
Runs an interactive visualization of subway data with NiceGUI.
This includes buttons that allow the user to view spread of ridership, add and remove stations,
and add and remove lines, as well as view the visualized graph.
"""
if __name__ in {"__main__", "__mp_main__"}:
    import transit_map
    from map_visualization import visualize_graph
    from nicegui import ui
    from plotly.graph_objs import Figure

    subway_graph = transit_map.load_subway_map('subway.csv', 'subway_lines.csv')

    def add_station(graph: transit_map.Graph, inputs: dict[str, list[str]]) -> None:
        if inputs['Name']:
            name = inputs['Name'][len(inputs['Name']) - 1]
            if inputs['Neighbours'] and 'No Stations' not in inputs['Neighbours']:
                neighbours = {neighbour for neighbour in inputs['Neighbours']
                              if neighbour in {v.item for v in graph.get_all_vertices(set())}}
            else:
                neighbours = set()
            if inputs['Lines'] and 'No Lines' not in inputs['Lines']:
                lines = {line for line in inputs['Lines']
                         if line in graph.get_all_lines()}
            else:
                lines = set()
            graph.add_station(name, neighbours, lines)
            update_graph(graph)
            refresh_add_station()

    def remove_station(graph: transit_map.Graph, station: str) -> None:
        if station in {v.item for v in graph.get_all_vertices(set())}:
            graph.remove_station(station)
            update_graph(graph)
            refresh_remove_station()

    def add_line(graph: transit_map.Graph, inputs: dict[str, list[str]]) -> None:
        if inputs['Name']:
            name = inputs['Name'][len(inputs['Name']) - 1]
            if inputs['Stations']:
                stations = [station for station in inputs['Stations']
                            if station in {v.item for v in graph.get_all_vertices(set())}]
            else:
                stations = set()
            graph.add_line(name, stations)
            update_graph(graph)
            refresh_add_line()

    def remove_line(graph: transit_map.Graph, line: str) -> None:
        if line in graph.get_all_lines():
            graph.remove_line(line)
            update_graph(graph)
            refresh_remove_line()

    def reset_map() -> None:
        reset_graph = transit_map.load_subway_map('subway.csv', 'subway_lines.csv')
        update_graph(reset_graph)

    def update_graph(g: transit_map.Graph = subway_graph) -> None:
        fig.data = []
        for trace in visualize_graph(g):
            fig.add_trace(trace)
        fig.update_layout(
            {'showlegend': False},
            margin=dict(l=5, r=20, t=20, b=20),
        )
        fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
        plot.update()

        select_neighbours.refresh()
        select_lines.refresh()
        select_remove.refresh()
        select_stations.refresh()
        select_remove_line.refresh()

    ui.html('Are You Smarter Than Rick Leary? The TTC Improvement Game'
            ).classes('w-full text-center').style('color: black; font-size: 275%; font-weight: 500')
    with ui.row().classes('w-full justify-center'):
        ui.button('View Spread of Ridership',
                  on_click=lambda: label.set_text(
                      f'The average TTC station deviates from the mean ridership per day by '
                      f'{str(subway_graph.spread_of_ridership(set()))} riders per day.'))
        label = ui.label().classes('w-full text-center').style('color: black; font-size: 100%; font-weight: 500')
    with ui.row().classes('w-full justify-center'):
        ui.button('Reset Map', on_click=lambda: reset_map())

    with ui.grid(columns=2).classes('w-full justify-center'):
        add_station_inputs = {'Name': [], 'Neighbours': [], 'Lines': []}
        with ui.row().style('background-color: #90EE90'):
            def update_selected_add_station(key: str, value: str) -> None:
                add_station_inputs[key].append(value)
                selected_neighbours_label.refresh()
                selected_lines_label.refresh()

            def refresh_add_station() -> None:
                for value in add_station_inputs.values():
                    del value[:]

            @ui.refreshable
            def select_neighbours() -> None:
                stations = sorted([v.item for v in subway_graph.get_all_vertices(set())])
                stations.append('No Stations')
                ui.select(stations, label='Neighbours',
                          on_change=lambda e: update_selected_add_station('Neighbours', e.value))

            @ui.refreshable
            def select_lines() -> None:
                lines = sorted(subway_graph.get_all_lines())
                lines.append('No Lines')
                ui.select(lines, label='Lines',
                          on_change=lambda e: update_selected_add_station('Lines', e.value))
            ui.label('Add Station')
            ui.input(label='Name of station to be added',
                     on_change=lambda e: add_station_inputs['Name'].append(e.value))
            select_neighbours()
            select_lines()
            ui.button('Click to add station', on_click=lambda: add_station(subway_graph, add_station_inputs)
                      ).props('color=positive')

        remove_station_input = []
        with ui.row().style('background-color: #FF7F7F'):
            def update_selected_remove_station(value: str) -> None:
                remove_station_input.append(value)
                selected_station_label.refresh()

            def refresh_remove_station() -> None:
                remove_station_input.clear()

            @ui.refreshable
            def select_remove() -> None:
                ui.select(sorted([v.item for v in subway_graph.get_all_vertices(set())]),
                          label='Select a station to remove',
                          on_change=lambda e: update_selected_remove_station(e.value))
            ui.label('Remove Station')
            select_remove()
            ui.button('Click to remove station',
                      on_click=lambda: remove_station(subway_graph, remove_station_input[len(remove_station_input) - 1])
                      ).props('color=negative')

        with ui.row():
            @ui.refreshable
            def selected_neighbours_label() -> None:
                ui.label(f'Selected Neighbours (select multiple to add multiple): '
                         f'{', '.join(n for n in add_station_inputs['Neighbours'])}')

            @ui.refreshable
            def selected_lines_label() -> None:
                ui.label(f'Selected Lines: {', '.join(n for n in add_station_inputs['Lines'])}')

            selected_neighbours_label()
            selected_lines_label()

        with ui.row():
            @ui.refreshable
            def selected_station_label() -> None:
                station = ''
                if len(remove_station_input) > 0:
                    station = remove_station_input[len(remove_station_input) - 1]
                ui.label(f'Selected Station to Remove: {station}')

            selected_station_label()

        add_line_inputs = {'Name': [], 'Stations': []}
        with ui.row().style('background-color: #90EE90'):
            def update_selected_add_line(value: str) -> None:
                add_line_inputs['Stations'].append(value)
                selected_stations_label.refresh()

            def refresh_add_line() -> None:
                for value in add_line_inputs.values():
                    del value[:]

            @ui.refreshable
            def select_stations() -> None:
                stations = sorted([v.item for v in subway_graph.get_all_vertices(set())])
                ui.select(stations, label='Stations. Select multiple to add multiple stations.',
                          on_change=lambda e: update_selected_add_line(e.value))
            ui.label('Add Line')
            ui.input(label='Name of line to be added',
                     on_change=lambda e: add_line_inputs['Name'].append(e.value))
            select_stations()
            ui.button('Click to add line', on_click=lambda: add_line(subway_graph, add_line_inputs)
                      ).props('color=positive')

        remove_line_input = []
        with ui.row().style('background-color: #FF7F7F'):
            def update_selected_remove_line(value: str) -> None:
                remove_line_input.append(value)
                selected_remove_line_label.refresh()

            def refresh_remove_line() -> None:
                remove_line_input.clear()

            @ui.refreshable
            def select_remove_line() -> None:
                lines = sorted(subway_graph.get_all_lines())
                ui.select(lines, label='Select a line to remove',
                          on_change=lambda e: update_selected_remove_line(e.value))
            ui.label('Remove Line')
            select_remove_line()
            ui.button('Click to remove line',
                      on_click=lambda: remove_line(subway_graph, remove_line_input[len(remove_line_input) - 1])
                      ).props('color=negative')

        with ui.row():
            @ui.refreshable
            def selected_stations_label() -> None:
                ui.label(f'Selected Stations (select multiple to add multiple): '
                         f'{', '.join(n for n in add_line_inputs['Stations'])}')

            selected_stations_label()

        with ui.row():
            @ui.refreshable
            def selected_remove_line_label() -> None:
                line = ''
                if len(remove_line_input) > 0:
                    line = remove_line_input[len(remove_line_input) - 1]
                ui.label(f'Selected Line to Remove: {line}')

            selected_remove_line_label()

    (ui.label('TTC Map (circa 2017, Scarborough RT excluded)').classes('w-full text-center')
     .style('color: black; font-size: 200%; font-weight: 400'))
    data1 = visualize_graph(subway_graph)
    fig = Figure(data=data1)
    fig.update_layout(
        {'showlegend': False},
        margin=dict(l=5, r=20, t=20, b=20),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    plot = ui.plotly(fig).classes('w-full h-full')

    ui.run()
