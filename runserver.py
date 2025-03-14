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

# Get unique participant names
participants = df["participants"].dropna().unique()


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


# Initialize Dash app
app = dash.Dash(__name__)


def participant_map():
    return [
        # Dropdown for participant selection
        dcc.Dropdown(
            id="participant-dropdown",
            options=[{"label": p, "value": p} for p in participants],
            placeholder="Select a participant",
            clearable=True),
        dl.Map(
            id="map",
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="markers")],
            center=[df["latitude"].mean(), df["longitude"].mean()],
            # Default center
            zoom=10,  # Default zoom level
            style={"height": "600px", "width": "600px"})]


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
        dcc.Graph(id='species-pie-chart')
    ]


# Layout
app.layout = html.Div(
    className="container",
    children=[
        html.Div(
            children=[html.H1("Fly Collection Heatmap")]),
        html.Div(children=participant_map()),
        html.Div(children=sample_table()),
        html.Div(children=sample_pie_chart()),
    ])


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


@app.callback([Output("markers", "children"),
               Output("map", "center"),
               Output("map", "zoom")], Input("participant-dropdown", "value"))
def update_map(selected_participant):
    markers = []
    zoom = 10  # Default zoom level when no participant is selected
    center = [df["latitude"].mean(),
              df["longitude"].mean()]  # Default center when no selection

    if selected_participant:
        # Filter data for the selected participant
        filtered_df = df[df["participants"] == selected_participant]

        # Get the first entry for the selected participant to zoom in on
        # their location
        center = [filtered_df["latitude"].iloc[0],
                  filtered_df["longitude"].iloc[0]]
        zoom = 14

    # Add markers for each row in the filtered dataframe
    for _, row in df.iterrows():
        base_color = get_color(row["total_flies"])
        color = base_color  # Highlight selected participant

        markers.append(dl.CircleMarker(
            center=[row["latitude"], row["longitude"]],
            radius=10,
            color="black",  # Border color
            fillColor=color,  # Fill color based on heatmap logic
            fillOpacity=0.8,
            children=dl.Tooltip(
                f"{row['participants']} - {row['total_flies']} flies")
        ))

    return markers, center, zoom


@app.callback(
    Output('species-table', 'data'),
    Input('participant-dropdown', 'value'))
def update_species_table(selected_participant):
    # Filter the dataframe by the selected participant (if any)
    filtered_df = df
    if selected_participant:
        filtered_df = filtered_df[
            filtered_df['participants'] == selected_participant]

    # Prepare the data for the table
    table_data = []
    sample_ids = filtered_df['sampleId'].unique()

    for sample_id in sample_ids:
        row = {'sampleId': sample_id}

        # Get the counts for each species in the species list
        sample_data = filtered_df[filtered_df['sampleId'] == sample_id]
        for species in species_list:
            species_count = sample_data[
                species].sum()  # Sum the count of flies for each species
            row[species] = species_count

        table_data.append(row)

    return table_data


@app.callback(
    Output('species-pie-chart', 'figure'),
    Input('sample-dropdown', 'value'))
def update_pie_chart(selected_sample):
    filtered_df = df
    if selected_sample:
        sample_data = filtered_df[filtered_df['sampleId'] == selected_sample]
        species_counts = {species: sample_data[species].sum() for species in
                          species_list if sample_data[species].sum() > 0}
        pie_chart = go.Figure(data=[go.Pie(labels=list(species_counts.keys()),
                                           values=list(
                                               species_counts.values()))])
    else:
        pie_chart = go.Figure()  # Empty chart when no sample is selected
    return pie_chart


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
