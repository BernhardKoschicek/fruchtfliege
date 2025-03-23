import dash
import numpy as np
from dash import dash_table, dcc, html
import dash_leaflet as dl
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go



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
                *[{'name': species, 'id': species} for species in species_list]
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
            id="species-dropdown",
            options=[{"label": s, "value": s} for s in species_list],
            placeholder="Select a species",
            clearable=True

        ),
        dl.Map(
            id="species-map",
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="species-markers")
            ],
            center=[df["latitude"].mean(), df["longitude"].mean()],
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

        html.Div([
            dcc.Dropdown(
                id='participant-dropdown',
                options=[{'label': p, 'value': p} for p in df['participants'].unique()],
                value=df['participants'].unique()[0]  # Initialer Wert
            )
        ], style={'width': '100%', 'display': 'inline-block'}),  # Dropdown für Teilnehmer

        html.Div(
            id='map-container',
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black', 'height': '600px', 'width': '600px'},
            children=participant_map()  # Initialisiere die Karte hier
        ),
        html.Div(
            children=sample_table(),
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'}
        ),
        html.Div(
            children=sample_pie_chart(),
            style={'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'}
        ),

        html.Div([
            dcc.Dropdown(
                id='common-species-dropdown',
                options=[{'label': s, 'value': s} for s in species_list],
                value=species_list[0]  # Initialer Wert
            ),
            html.Div(
                style={'display': 'flex'},  # Flexbox-Container
                children=[
                    html.Div(
                        style={'flex': '1', 'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'},  # Flex-Item
                        children=[
                            html.H3("Species Collection Trend Over Time"),
                            dcc.Graph(id="species-time-series")
                        ]
                    ),
                    html.Div(
                        style={'flex': '1', 'resize': 'both', 'overflow': 'auto', 'border': '1px solid black'},  # Flex-Item
                        children=[
                            html.H3("Species Collection Map"),
                            dl.Map(
                                id="species-map",
                                children=[dl.TileLayer(), dl.LayerGroup(id="species-markers")],
                                center=[df["latitude"].mean(), df["longitude"].mean()],
                                zoom=10,
                                style={"height": "400px", "width": "400px"}
                            )
                        ]
                    )
                ]
            )
        ])
    ]
)


@app.callback(
    Output('sample-dropdown', 'options'),
    Input('participant-dropdown', 'value')
)
def update_sample_dropdown(selected_participant):
    """Updates the sample dropdown based on selected participant"""
    if selected_participant:
        sample_ids = df[df["participants"] == selected_participant][
            "sampleId"].unique()
        return [{"label": s, "value": s} for s in sample_ids]
    return []  # Return empty if no participant is selected

@app.callback(
    [Output('markers', 'children'),
     Output('map-container', 'children')],
    Input('participant-dropdown', 'value')
)
def update_map_components(selected_participant):
    if selected_participant:
        filtered_df = df[df['participants'] == selected_participant].copy()

        # Fehlende und ungültige Werte behandeln
        filtered_df['latitude'] = pd.to_numeric(filtered_df['latitude'], errors='coerce').fillna(0)
        filtered_df['longitude'] = pd.to_numeric(filtered_df['longitude'], errors='coerce').fillna(0)

        markers = [dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            radius=10,
            color="black",
            fillColor=get_color(row['total_flies']),
            fillOpacity=0.8,
            children=dl.Tooltip(f"{row['participants']} - {row['total_flies']} flies")
        ) for index, row in filtered_df.iterrows()]

        # Berechne den Mittelpunkt und Zoom basierend auf den gefilterten Daten
        center = [filtered_df['latitude'].mean(), filtered_df['longitude'].mean()]
        zoom = 14  # Du kannst den Zoom-Wert anpassen

        map_component = dl.Map(
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="markers", children=markers) # Hinzugefügt: LayerGroup mit id="markers"
            ],
            center=center,
            zoom=zoom,
            style={'width': '100%', 'height': '100%'}
        )
        return markers, map_component
    else:
        # Fehlende und ungültige Werte behandeln
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0)
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0)

        markers = [dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            radius=10,
            color="black",
            fillColor=get_color(row['total_flies']),
            fillOpacity=0.5,
            children=dl.Tooltip(f"{row['participants']} - {row['total_flies']} flies")
        ) for index, row in df.iterrows()]

        # Berechne den Mittelpunkt und Zoom basierend auf allen Daten
        center = [df['latitude'].mean(), df['longitude'].mean()]
        zoom = 10  # Du kannst den Zoom-Wert anpassen

        map_component = dl.Map(
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="markers", children=markers) # Hinzugefügt: LayerGroup mit id="markers"
            ],
            center=center,
            zoom=zoom,
            style={'width': '100%', 'height': '100%'}
        )
        return markers, map_component
def get_color(total_flies):
    # Beispielhafte Farbzuordnung basierend auf der Anzahl der Fliegen
    if total_flies < 10:
        return "green"
    elif 10 <= total_flies < 50:
        return "orange"
    else:
        return "red"


# Callback

@app.callback(
    Output('species-table', 'data'),
    Input('participant-dropdown', 'value')
)
def update_species_table(selected_participant):
    print("Callback wurde aufgerufen!")  # Überprüfen, ob der Callback ausgelöst wird

    filtered_df = df
    if selected_participant:
        filtered_df = filtered_df[filtered_df['participants'] == selected_participant].copy()

    filtered_df['sampleId'] = filtered_df['sampleId'].astype(str).str.strip()

    table_data = []
    sample_ids = filtered_df['sampleId'].unique()

    for sample_id in sample_ids:
        sample_data = filtered_df[filtered_df['sampleId'] == sample_id].copy()
        row = {'sampleId': sample_id}
        for species in species_list:
            sample_data.loc[:, species] = pd.to_numeric(sample_data[species], errors='coerce').fillna(0)
            species_count = sample_data[species].sum()
            row[species] = species_count
        table_data.append(row)

    if selected_participant:
        participant_sum = filtered_df[species_list].sum()
        sum_row = {'sampleId': 'Participant Total'}
        for species in species_list:
            participant_sum = pd.to_numeric(participant_sum, errors = 'coerce').fillna(0)
            sum_row[species] = participant_sum[species]
        table_data.append(sum_row)

    print(table_data)  # Überprüfen der Daten vor der Übergabe
    return table_data


import plotly.graph_objects as go


@app.callback(
    [Output('sample-species-pie-chart', 'figure'),
     Output('participant-species-pie-chart', 'figure')],
    Input('sample-dropdown', 'value'),
    Input('participant-dropdown', 'value')
)
def update_pie_chart(selected_sample, selected_participant):
    # Pie-Chart für Sample
    if selected_sample:
        sample_data = df[df['sampleId'] == selected_sample]
        sample_species_counts = {species: sample_data[species].sum() for species in species_list if sample_data[species].sum() > 0}
        sample_colors = [get_species_color(species) for species in sample_species_counts.keys()]
        sample_pie_chart = go.Figure(data=[go.Pie(
            labels=list(sample_species_counts.keys()),
            values=list(sample_species_counts.values()),
            marker=dict(colors=sample_colors)
        )])
    else:
        sample_pie_chart = go.Figure()

    # Pie-Chart für Participant
    if selected_participant:
        participant_data = df[df['participants'] == selected_participant]
        participant_species_counts = {species: participant_data[species].sum() for species in species_list if participant_data[species].sum() > 0}
        participant_colors = [get_species_color(species) for species in participant_species_counts.keys()]
        participant_pie_chart = go.Figure(data=[go.Pie(
            labels=list(participant_species_counts.keys()),
            values=list(participant_species_counts.values()),
            marker=dict(colors=participant_colors)
        )])
    else:
        participant_pie_chart = go.Figure()

    return sample_pie_chart, participant_pie_chart
@app.callback(
    Output("species-time-series", "figure"),
    Input("common-species-dropdown", "value")
)
def update_species_histogram(selected_species):
    if not selected_species:
        return go.Figure()  # Return empty figure if no species is selected

    # Ensure collectionEnd is a date format
    df["collectionEnd"] = pd.to_datetime(df["collectionEnd"], dayfirst=True, errors="coerce")


    # Filter and group by collectionEnd date
    species_counts = df.groupby("collectionEnd")[
        selected_species].sum().reset_index()

    # Convert date to string format (DD-MM-YYYY)
    species_counts["collectionEnd"] = species_counts[
        "collectionEnd"].dt.strftime("%d-%m-%Y")

    # Create histogram
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=species_counts["collectionEnd"],
        y=species_counts[selected_species],
        marker=dict(color=get_species_color(selected_species)),
        name=selected_species
    ))

    fig.update_layout(
        title=f"Total {selected_species} Count Over Time",
        xaxis_title="Collection End Date",
        yaxis_title="Total Count",
        xaxis=dict(type="category"),  # Keeps discrete date values
        template="plotly_white",
        bargap=0.2  # Adds spacing between bars
    )

    return fig


@app.callback(
    Output("species-markers", "children"),
    Input("common-species-dropdown", "value")
)
def update_species_map(selected_species):
    if not selected_species:
        return []  # Return empty markers if no species is selected

    # Bestimme die Farbe basierend auf der definierten Farbkodierung
    marker_color = get_species_color(selected_species)

    # Filter data where the species count is greater than zero
    filtered_df = df[df[selected_species] > 0]

    markers = []
    for _, row in filtered_df.iterrows():
        markers.append(dl.CircleMarker(
            center=[row["latitude"], row["longitude"]],
            radius=8,  # Adjust size based on visibility needs
            color="black",  # Border color
            fillColor=marker_color,  # Marker color based on species
            fillOpacity=0.8,
            children=dl.Tooltip(
                f"Participant: {row['participants']} | "
                f"Date: {row['collectionEnd']} | "
                f"Count: {row[selected_species]}"
            )
        ))

    return markers



# Run the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)