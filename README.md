# the-ttc-improvement-game

A final project for CSC111 at the University of Toronto.

In this project, I used data from the TTC and Bike Share Toronto to analyze public transit and bike traffic on Toronto's major roadways. With this data, I created a tool to analyze the question: Where can the current TTC and Bike Share systems be improved by adding or removing service, and what effect might these improvements have on TTC ridership?

I modelled TTC and Bike Share Toronto ridership data using a graph that incorporates subway stops, aboveground transit (streetcar and bus) stops, and bike docking stations. A vertex in the graph represents a stop, aboveground transit line, or bike docking station, and an edge between vertices represents a connection between two stops. I used Python's networkx and plotly libraries to create and plot the resulting graphs. I also created a graphical user interface (GUI) using NiceGUI that allows a user to edit the subway graph directly by adding and removing stations and lines, as well as see the effects of these edits on spread of ridership. (The spread of ridership across stations is significant because it shows us whether the burden of large traffic volumes is shared equally among stations. We want the spread of ridership to be lower because that would mean a lower number of stations that have too many or too few passengers.)

To run the interactive visualization, run main.py. The visualization only supports subway data.
