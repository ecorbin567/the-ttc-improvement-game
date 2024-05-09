FROM zauberzeug/nicegui:1.4.24
RUN pip install --no-cache-dir networkx nicegui plotly statistics typing
COPY . /app