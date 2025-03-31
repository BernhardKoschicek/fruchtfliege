import dash
import numpy as np
import requests
from dash import dash_table, dcc, html
import dash_leaflet as dl
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from dash_extensions.enrich import ClientsideFunction

# Load CSV
df = pd.read_csv("flies.csv")

# Ensure total_flies column is numeric
df["total_flies"] = pd.to_numeric(df["total_flies"], errors="coerce").fillna(0)

# Get min and max for normalization
min_flies = df["total_flies"].min()
max_flies = df["total_flies"].max()

# List of species to include in the table
species_list = ['melanogaster', 'simulans', 'suzukii', 'busckii', 'testacea',
                'hydei', 'mercatorum', 'repleta', 'funebris', 'immigrans',
                'phalerata', 'subobscura', 'virilis']

def get_species_data():
    # Alle Spalten mit Arten summieren pro participantid
    df_sum = df.groupby("participants")[species_list].sum().reset_index()

    # Gesamtzahl aller Fliegen pro participant berechnen
    df_sum["total_flies"] = df_sum.iloc[:, 1:].sum(axis=1)

    # Eine Zeile mit der Summe aller Fliegen über alle Teilnehmer hinzufügen
    total_row = df_sum[species_list].sum().to_frame().T
    total_row["participants"] = "TOTAL"
    total_row["total_flies"] = total_row[species_list].sum(axis=1)

    # Die Gesamtzeile an die Tabelle anhängen
    df_final = pd.concat([df_sum, total_row], ignore_index=True)

    # Rückgabe als Liste von Dictionaries (für Dash)
    return df_final.to_dict("records")

# Häufigkeit der Arten berechnen
species_counts = {species: df[species].sum() for species in species_list}

# Arten nach Häufigkeit sortieren
sorted_species = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)
species_rank = {species: rank for rank, (species, _) in enumerate(sorted_species)}

# Get unique participant names
participants = sorted(df["participants"].dropna().unique())


def get_color(value):
    """Returns a hex color from yellow to dark red with high contrast"""
    if max_flies == min_flies:  # Avoid division by zero
        return "#FFFF00"  # Default to yellow if all values are the same

    # Apply log scaling for better contrast (log1p prevents log(0) issues)
    log_min = np.log1p(min_flies)
    log_max = np.log1p(max_flies)
    log_value = np.log1p(value)

    ratio = (log_value - log_min) / (
            log_max - log_min)  # Normalize between 0-1

    # Stronger color contrast
    r = int(128 + (127 * ratio))  # Red increases from 128 → 255
    g = int(255 * (1 - ratio))  # Green decreases from 255 → 0
    b = int(64 * (1 - ratio))  # Blue slightly decreases from 64 → 0

    return f"#{r:02X}{g:02X}{b:02X}"  # Convert to hex format

#Funktion zur Farbkodierung
def get_species_color(species):
    rank = species_rank.get(species, len(species_list) - 1)
    color_scale = [
        "#880000",  # Dark Red (most frequent)
        "#FF0000",  # Red
        "#ec5252",  # Medium light red
        "#FF7F00",  # Orange
        "#ffa54d",  # Light orange
        "#FFFF00",  # Yellow
        "#cccc00",  # Dark yellow
        "#4dff4d",  # Light green
        "#00FF00",  # Green
        "#00b300",  # Dark green
        "#4d4dff",  # Light blue
        "#0000FF",  # Blue
        "#0000b3"  # Dark blue
    ]
    return color_scale[min(rank, len(color_scale) - 1)]


# Initialize Dash app
app = dash.Dash(__name__)

def participant_map():
    return dl.Map(
        id="map",
        children=[
            dl.TileLayer(),
            dl.LayerGroup(id="markers") # Stelle sicher, dass dies vorhanden ist
        ],
        center=[df["latitude"].mean(), df["longitude"].mean()],
        zoom=10,
        style={'height': '100%', 'width': '100%'}
    )

def sample_table():
    return [
        html.H3("Species Counts by Sample ID"),
        dash_table.DataTable(
            id='species-table',
            columns=[
                {'name': 'Sample ID', 'id': 'sampleId'},
                *[{'name': species, 'id': species} for species in species_list],
                {'name': 'Total per Sample', 'id': 'Total per Sample'},
                # Add species columns
            ],
            style_table={'height': '400px', 'overflowY': 'auto'},
            # Enable scrolling if needed
            style_cell={'textAlign': 'center', 'minWidth': '80px',
                        'width': '80px', 'maxWidth': '80px'},
            style_header={'backgroundColor': 'lightgray',
                          'fontWeight': 'bold'},
        )
    ]


def sample_pie_chart():
    return [
        html.H3('Species Distribution'),
        # Sample ID selection (populated dynamically)
        dcc.Dropdown(
            id="sample-dropdown",
            placeholder="Select a sample ID",
            clearable=True
        ),
        html.Div(
            style={'display': 'flex'},  # Flexbox-Container
            children=[
                dcc.Graph(id='sample-species-pie-chart', style={'flex': '1'}),  # Pie-Chart für Sample
                dcc.Graph(id='participant-species-pie-chart', style={'flex': '1'})  # Pie-Chart für Participant
            ]
        )
    ]



def species_time_series():
    return [
        html.H3("Species Collection Trend Over Time"),
        dcc.Dropdown(
            id="species-dropdown",
            options=[{"label": species, "value": species} for species in
                     species_list],
            placeholder="Select a species",
            clearable=True
        ),
        dcc.Graph(id="species-time-series")]


def species_map():
    return [
        html.H3("Species Collection Map"),
        dcc.Dropdown(
            id="common-species-dropdown",
            options=[{"label": s, "value": s} for s in species_list],
            placeholder="Select a species",
            clearable=True
        ),
        dl.Map(
            id="species-collection-map",
            children=[
                dl.TileLayer(),
                dl.FitBounds(
                    children=dl.LayerGroup(id="species-markers")
                )
            ],
            center=[48.2082, 16.3738],  # Diese Standardeinstellungen werden überschrieben, wenn Bounds vorhanden sind
            zoom=10,
            style={"height": "600p", "width": "600p"}
        )
    ]

# Layout
app.layout = html.Div(
    className="container",
    children=[
        html.Img(src="https://fairicube.wp2.nilu.no/wp-content/uploads/sites/21/2024/04/Logo-cityfly.png", style={'width': '200px'}),  # Füge das Bild hier hinzu
        html.Div(children=[html.H1("Vienna City Fly 2025")]),
        html.Div(
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black', 'height': '650px', 'width': '100%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'},
            children=[
                dcc.Dropdown(
                    id='participant-dropdown',
                    options=[{'label': p, 'value': p} for p in sorted(df['participants'].unique())],
                    value=df['participants'].unique()[0]  # Initialer Wert
                ),
                html.Div(
                    id='map-container',
                    style={'flex': '1', 'border': '1px solid black', 'position': 'relative'},
                    # Wichtig: position: relative
                    children=[
                        dl.Map(
                            id="map",
                            children=[dl.TileLayer(), dl.LayerGroup(id="markers")],
                            center=[df["latitude"].mean(), df["longitude"].mean()],
                            zoom=8,
                            style={"height": "100%", "width": "100%"}
                        ),
                    ],
                ),
                html.Script("""
                            const mapContainer = document.getElementById('map-container');
                            const resizeObserver = new ResizeObserver(entries => {
                                for (let entry of entries) {
                                    if (entry.target === mapContainer) {
                                        const size = { width: entry.contentRect.width, height: entry.contentRect.height };
                                        // Hier könntest du das 'size'-Property des map-container-Divs direkt manipulieren,
                                        // um den Clientside-Callback auszulösen (Workaround).
                                        mapContainer.setAttribute('data-size', JSON.stringify(size));
                                        // Oder du verwendest ein CustomEvent (sauberer):
                                        mapContainer.dispatchEvent(new CustomEvent('containerResize', { detail: size }));
                                    }
                                }
                            });
                            resizeObserver.observe(mapContainer);

                            // Clientside Callback, der auf das CustomEvent reagiert
                            window.dash_clientside = window.dash_clientside || {};
                            window.dash_clientside.clientside = {
                                resize_map: function(dummy_id) {
                                    const mapElement = document.getElementById('map');
                                    if (mapElement && mapElement.__leaflet_map__) {
                                        mapElement.__leaflet_map__.invalidateSize();
                                    }
                                    return window.dash_clientside.no_update;
                                }
                            };
                        """)
            ]
        ),
        html.Div(
            children=sample_table(),
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'}
        ),
        html.Div(
            children=sample_pie_chart(),
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'}
        ),

        html.Div(
            [
                dcc.Dropdown(
                    id='common-species-dropdown',
                    options=[{'label': s, 'value': s} for s in species_list],
                    value=species_list[0]  # Initialwert
                ),
                html.Div(
                    style={'display': 'flex'},
                    children=[
                        html.Div(
                            style={'flex': '1', 'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'},
                            children=[
                                html.H3("Species Collection Trend Over Time"),
                                dcc.Graph(id="species-time-series")
                            ]
                        ),
                        html.Div(
                            id='species-info',
                            style={'flex': '1', 'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'},
                            children=[html.H3("Species Info"), html.Div("Select a species to see details.")]
                        )
                    ]
                ),
                # Die Karte wird jetzt hier außerhalb des flex-Containers platziert
                html.Div(
                    style={'width': '100%', 'resize': 'both', 'overflow': 'auto', 'border': '1px solid black',
                           'margin-top': '20px'},
                    children=[
                        html.H3("Species Collection Map"),
                        dl.Map(
                            id="species-collection-map",
                            children=[dl.TileLayer(), dl.LayerGroup(id="species-markers")],
                            center=[df["latitude"].mean(), df["longitude"].mean()],
                            # Verwende den Durchschnitt aller Koordinaten als initialen Center
                            zoom=8,
                            style={"height": "600px", "width": "100%"}
                        )
                    ]
                 )
            ]
        )
   ]
)



app.clientside_callback(
    ClientsideFunction(
        namespace="clientside",
        function_name="resize_map"
    ),
    Output("map", "dummy_output"), # Ein Dummy-Output
    Input("map-container", "id") # Trigger bei Initialisierung
)

@app.callback(
    [Output('markers', 'children'),
     Output('map', 'center'),
     Output('map', 'zoom')],
    Input('participant-dropdown', 'value')
)
def update_map(selected_participant):
    # Fehlende und ungültige Werte einmalig außerhalb der if-Abfragen behandeln
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0)
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0)

    all_markers = [dl.CircleMarker(
        center=[row['latitude'], row['longitude']],
        radius=6,
        color="black",
        fillColor=get_color(row['total_flies']),
        fillOpacity=0.5,
        children=dl.Tooltip(f"{row['participants']} - {row['total_flies']} flies")
    ) for index, row in df.iterrows()]

    initial_center = [df['latitude'].mean(), df['longitude'].mean()]
    initial_zoom = 8 # Diesen Wert ggf. anpassen

    if selected_participant:
        filtered_df = df[df['participants'] == selected_participant].copy()

        if not filtered_df.empty:
            participant_lat = filtered_df['latitude'].mean()
            participant_lon = filtered_df['longitude'].mean()
            participant_center = [participant_lat, participant_lon]

            # Berechnung des Zooms basierend auf den Koordinaten des ausgewählten Teilnehmers
            # Hier ist eine einfachere Logik, die du verfeinern kannst
            zoom_level = 14 # Starte mit einem relativ hohen Zoom

            return all_markers, participant_center, zoom_level
        else:
            return all_markers, initial_center, initial_zoom
    else:
        return all_markers, initial_center, initial_zoom

def get_color(total_flies):
    if max_flies == min_flies:
        return "#FFFF00"
    log_min = np.log1p(min_flies)
    log_max = np.log1p(max_flies)
    log_value = np.log1p(total_flies)
    ratio = (log_value - log_min) / (log_max - log_min)
    r = int(128 + (127 * ratio))
    g = int(255 * (1 - ratio))
    b = int(64 * (1 - ratio))
    return f"#{r:02X}{g:02X}{b:02X}"

@app.callback(
    Output('species-info', 'children'),
    Input('common-species-dropdown', 'value')
)
def update_species_info(species):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/drosophila_{species}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return html.Div([
                html.H3(data.get('title', 'No Title')),
                html.Img(src=data.get('thumbnail', {}).get('source', ''), style={'max-width': '100%'}),
                html.P(html.I(data.get('extract', 'No information available')))
            ])
    except Exception as e:
        return html.Div(f"Error fetching data: {str(e)}")

    return html.Div("No data available.")

@app.callback(
    Output('sample-dropdown', 'options'),
    Input('participant-dropdown', 'value')
)
def update_sample_dropdown(selected_participant):
    """Updates the sample dropdown based on selected participant"""
    if selected_participant:
        sample_ids = df[df["participants"] == selected_participant]["sampleId"].unique()
        return [{"label": s, "value": s} for s in sample_ids]
    return []  # Return empty if no participant is selected

@app.callback(
    Output('species-table', 'data'),
    Input('participant-dropdown', 'value')
)
def update_species_table(selected_participant):
    print("Callback für Tabelle aufgerufen!")

    if selected_participant:
        filtered_df = df[df['participants'] == selected_participant].copy()

        # Gruppiere nach Sample ID und summiere die Arten (für die einzelnen Sample-Zeilen)
        species_by_sample = filtered_df.groupby('sampleId')[species_list].sum().reset_index()
        species_by_sample['Total per Sample'] = species_by_sample[species_list].sum(axis=1)

        # Berechne die Summe jeder Species über alle Samples des Participants
        species_totals = filtered_df[species_list].sum().to_frame().T
        species_totals['sampleId'] = 'Total per Participant' # Füge eine "Sample ID" für die Summenzeile hinzu
        species_totals['Total per Sample'] = species_totals[species_list].sum(axis=1) # Berechne die Gesamtsumme für den Participant
        print(f"Inhalt von species_totals nach Berechnung der Summe:\n{species_totals}")

        # Kombiniere die Sample-Daten mit der Summenzeile
        final_data = pd.concat([species_by_sample, species_totals], ignore_index=True)
        print(f"Daten für die Tabelle (final_data.to_dict('records')):\n{final_data.to_dict('records')}")
        return final_data.to_dict('records')
    else:
        return []

@app.callback(
    Output('participant-species-pie-chart', 'figure'),
    Input('participant-dropdown', 'value')
)
def update_participant_pie_chart(selected_participant):
    if selected_participant:
        participant_data = df[df['participants'] == selected_participant][species_list].sum()
        # Filtere Arten mit Werten größer als 0
        filtered_data = participant_data[participant_data > 0]
        labels = filtered_data.index
        values = filtered_data.values
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        return fig
    else:
        return go.Figure()

@app.callback(
    Output('sample-species-pie-chart', 'figure'),
    Input('sample-dropdown', 'value')
)
def update_sample_pie_chart(selected_sample):
    if selected_sample:
        sample_data = df[df['sampleId'] == selected_sample][species_list].sum()
        # Filtere Arten mit Werten größer als 0
        filtered_data = sample_data[sample_data > 0]
        labels = filtered_data.index
        values = filtered_data.values
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        return fig
    else:
        return go.Figure()

@app.callback(
    Output("species-time-series", "figure"),
    Input("common-species-dropdown", "value")
)
def update_time_series(selected_species):
    if selected_species:
        # Stelle sicher, dass die collectionEnd-Spalte im DataFrame ein datetime-Objekt ist
        df['collectionEnd'] = pd.to_datetime(df['collectionEnd'])

        filtered_df = df[df[selected_species] > 0].copy() # Nur Einträge mit Vorkommen der Spezies
        if not filtered_df.empty:
            # Verwende go.Bar für ein Säulendiagramm
            fig = go.Figure(data=[go.Bar(x=filtered_df['collectionEnd'], y=filtered_df[selected_species])])
            fig.update_layout(title=f"Collection Trend of {selected_species} Over Time",
                              xaxis_title="Time",
                              yaxis_title=f"Number of {selected_species}")
            return fig
        else:
            return go.Figure(data=[go.Bar(x=[], y=[])], # Leere Balken
                                 layout=go.Layout(title=f"No data found for {selected_species}"))
    else:
        return go.Figure() # Leerer Graph, wenn keine Spezies ausgewählt ist

@app.callback(
    [Output("species-markers", "children"),
     Output("species-collection-map", "bounds")],
    Input("common-species-dropdown", "value")
)
def update_species_map(selected_species):
    print(f"Ausgewählte Spezies: {selected_species}")
    color = get_species_color(selected_species)
    print(f"Farbe für {selected_species}: {color}")
    if selected_species:
        filtered_df = df[df[selected_species] > 0].copy() # Nur Einträge mit Vorkommen der Spezies
        if not filtered_df.empty:
            markers = [dl.CircleMarker(center=[row['latitude'], row['longitude']],
                                       radius=8,
                                       color=get_species_color(selected_species),
                                       fillColor=get_species_color(selected_species),
                                       fillOpacity=0.6,
                                       children=dl.Tooltip(f"{selected_species}"))
                       for index, row in filtered_df.iterrows()]
            # Berechne die Bounds der Marker
            lats = filtered_df['latitude'].tolist()
            lons = filtered_df['longitude'].tolist()
            if lats and lons:
                min_lat = min(lats)
                max_lat = max(lats)
                min_lon = min(lons)
                max_lon = max(lons)
                bounds = [[min_lat, min_lon], [max_lat, max_lon]]
                return markers, bounds
            else:
                return [], None # Keine Marker, keine Bounds
        else:
            return [], None # Keine Marker, keine Bounds
    else:
        return [], None # Keine Marker, keine Bounds



# Run the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)