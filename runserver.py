import uuid
import io
from typing import Any

import dash
import dash_leaflet as dl
import pandas as pd
import plotly.graph_objects as go
import requests
from dash import html, dcc, State
from dash.dependencies import Input, Output, State
from dash.html import Div, Figure
from dash_leaflet import CircleMarker
from dash.exceptions import PreventUpdate


from files.data import df, species_list
from files.layout import layout
from files.util import get_color, get_species_color, make_popup

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
# Testen Sie die layout() Funktion direkt
try:
    test_layout = layout()
    print("Layout erfolgreich erstellt!")
    app.layout = layout()
except Exception as e:
    print(f"FEHLER in layout(): {e}")
    print(f"FEHLER in layout(): {e}")
    import traceback
    traceback.print_exc()


@app.callback(
    [Output('markers', 'children'),
     Output('map', 'center'),
     Output('map', 'zoom')],
    [Input('participant-dropdown', 'value')],
    [State('map', 'zoom')])  # Speichere den aktuellen Zoom-Wert

def update_map(
        selected_participant: str,
        current_zoom: int) -> tuple[list[CircleMarker], list[Any], int | Any]:
    # Sicherstellen, dass Längen- und Breitengrade numerisch sind
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0)
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0)

    # Marker für alle Teilnehmer
    selected_marker = None
    all_markers = []
    for _, row in df.iterrows():
        unique_id = str(uuid.uuid4())
        is_selected = selected_participant == row['participants']
        marker_radius = 10 if is_selected else 6
        border_color = '#000000' if is_selected else "#999"  # z.B. grau für nicht-ausgewählte
        fill_color = "purple" if is_selected else get_color(row['total_flies'])

        # Berechne die species_totals für den Teilnehmer, falls ausgewählt
        if is_selected:
            filtered_df = df[df['participants'] == row['participants']].copy()
            species_totals = filtered_df[species_list].sum().to_frame().T
            species_totals['sampleId'] = 'Total per Participant'
            species_totals['Total per Sample'] = species_totals[species_list].sum(axis=1)

            all_markers.append(
                dl.CircleMarker(
                    id=unique_id,
                    center=[row['latitude'], row['longitude']],
                    radius=marker_radius,
                    color=border_color,
                    fillColor=fill_color,
                    fillOpacity=0.8 if is_selected else 0.2,
                    children=make_popup(row['participants'], species_totals)  # Übergabe von species_totals
                )
            )
        else:
            all_markers.append(
                dl.CircleMarker(
                    id=unique_id,
                    center=[row['latitude'], row['longitude']],
                    radius=marker_radius,
                    color=border_color,
                    fillColor=fill_color,
                    fillOpacity=0.8 if is_selected else 0.2,
                    children=dl.Tooltip(f"{row['participants']} - {row['total_flies']} flies")
                )
            )

    if selected_participant:
        filtered_df = df[df['participants'] == selected_participant].copy()
        if not filtered_df.empty:
            participant_lat = filtered_df['latitude'].mean()
            participant_lon = filtered_df['longitude'].mean()
            participant_center = [participant_lat, participant_lon]
            return all_markers, participant_center, 13

    # Kein Participant ausgewählt → auf alle Punkte zoomen
    min_lat = df['latitude'].min()
    max_lat = df['latitude'].max()
    min_lon = df['longitude'].min()
    max_lon = df['longitude'].max()

    map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]

    # Grober Zoom-Level, der die gesamte Streuung halbwegs abdeckt
    auto_zoom = 8 if max_lat - min_lat < 1.5 and max_lon - min_lon < 1.5 else 6

    return all_markers, map_center, auto_zoom


@app.callback(
    Output('species-info', 'children'),
    Input('common-species-dropdown', 'value'))
def update_species_info(species: str) -> Div:
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/drosophila_"
           f"{species}")
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return html.Div([
                html.H3(data.get('title', 'No Title'), style={'padding': '10px'}),
                html.Img(
                    src=data.get('thumbnail', {}).get('source', ''),
                    style={'max-width': '100%', 'padding': '10px'}),
                html.P(
                    html.I(data.get('extract', 'No information available'), style={'paddingLeft': '10px'}))])
    except Exception as e:
        return html.Div(f"Error fetching data: {str(e)}")
    return html.Div("No data available.")

# Callback für den Download


@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State("download-option", "value"),
    State("participant-dropdown", "value"),  # Annahme: dieser Wert ist per dcc.Store o. Ä. gespeichert
    prevent_initial_call=True
)
def download_table(n_clicks, download_option, selected_participant):
    if download_option == 'selected':
        df_to_download = df[df['participants'] == selected_participant]
        filename = f"{selected_participant}-species_data.csv"
    else:
        columns_to_exclude = ['latitude', 'longitude', 'bait']
        columns_to_include = [col for col in df.columns if col not in columns_to_exclude]
        df_to_download = df[columns_to_include]
        filename = "all_species_data.csv"

    # Gebe den DataFrame als CSV-String zum Download zurück
    return dcc.send_data_frame(df_to_download.to_csv, filename, index=False)


@app.callback(
    Output('sample-dropdown', 'options'),
    Input('participant-dropdown', 'value'))
def update_sample_dropdown(selected_participant: str) -> list[Any]:
    """Updates the sample dropdown based on selected participant"""
    if selected_participant:
        sample_ids = df[
            df["participants"] == selected_participant]["sampleId"].unique()
        return [{"label": s, "value": s} for s in sample_ids]
    return []  # Return empty if no participant is selected


@app.callback(
    Output('species-table', 'data'),
    Input('participant-dropdown', 'value'))
def update_species_table(selected_participant: str) -> list[Any]:
    print("Callback für Tabelle aufgerufen!")

    if selected_participant:
        filtered_df = df[df['participants'] == selected_participant].copy()

        # Gruppiere nach Sample ID und summiere die Arten (für die einzelnen
        # Sample-Zeilen)
        species_by_sample = (
            filtered_df.groupby('sampleId')[species_list].sum().reset_index())
        species_by_sample['Total per Sample'] = (
            species_by_sample[species_list].sum(axis=1))

        # Berechne die Summe jeder Species über alle Samples des Participants
        species_totals = filtered_df[species_list].sum().to_frame().T
        # Füge eine "Sample ID" für die Summenzeile hinzu
        species_totals['sampleId'] = 'Total per Participant'
        # Berechne die Gesamtsumme für den Participant
        species_totals['Total per Sample'] = (
            species_totals[species_list].sum(axis=1))
        print(f"Inhalt von species_totals nach Berechnung der Summe:\n"
              f"{species_totals}")

        # Kombiniere die Sample-Daten mit der Summenzeile
        final_data = pd.concat(
            [species_by_sample, species_totals], ignore_index=True)
        print(f"Daten für die Tabelle (final_data.to_dict('records')):\n"
              f"{final_data.to_dict('records')}")
        return final_data.to_dict('records')
    return []


@app.callback(
    Output('participant-species-pie-chart', 'figure'),
    Input('participant-dropdown', 'value'))
def update_participant_pie_chart(selected_participant: str) -> Figure:
    if selected_participant:
        participant_data = (
            df[df['participants'] == selected_participant][species_list].sum())
        # Filtere Arten mit Werten größer als 0
        filtered_data = participant_data[participant_data > 0]
        labels = filtered_data.index
        values = filtered_data.values
        colors = [get_species_color(species) for species in labels]
        showlegend = False
        fig = go.Figure(data=[
            go.Pie(labels=labels, values=values, marker=dict(colors=colors), showlegend = False)])
        fig.update_layout(title=f"Artenverteilung Teilnehmer { selected_participant}")
        return fig
    return go.Figure()


@app.callback(
    Output('sample-species-pie-chart', 'figure'),
    Input('sample-dropdown', 'value'))
def update_sample_pie_chart(selected_sample: str) -> Figure:
    if selected_sample:
        sample_data = df[df['sampleId'] == selected_sample][species_list].sum()
        # Filtere Arten mit Werten größer als 0
        filtered_data = sample_data[sample_data > 0]
        labels = filtered_data.index
        values = filtered_data.values
        colors = [get_species_color(species) for species in labels]
        fig = go.Figure(data=[
            go.Pie(labels=labels, values=values, marker=dict(colors=colors), showlegend = False)])
        fig.update_layout(title=f"Artenverteilung Falle {selected_sample}")
        return fig
    return go.Figure()


@app.callback(
    Output("species-time-series", "figure"),
    Input("common-species-dropdown", "value"))
def update_time_series(selected_species: str) -> Figure:
    if selected_species:
        # Stelle sicher, dass die collectionEnd-Spalte
        # im DataFrame ein datetime-Objekt ist
        df_copy = df.copy()
        df_copy['collectionEnd'] = pd.to_datetime(df_copy['collectionEnd'])

        # Nur Einträge mit Vorkommen der Spezies
        filtered_df = df[df[selected_species] > 0].copy()
        if not filtered_df.empty:
            # Verwende go.Bar für ein Säulendiagramm
            fig = go.Figure(
                data=[go.Bar(
                    x=filtered_df['collectionEnd'],
                    y=filtered_df[selected_species],
                    marker_color=get_species_color(selected_species))])
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title=f"Number of {selected_species}")
            return fig
        return go.Figure(
            data=[go.Bar(x=[], y=[])],  # Leere Balken
            layout=go.Layout(title=f"No data found for {selected_species}")
        )
    return go.Figure()  # Leerer Graph, wenn keine Spezies ausgewählt ist


@app.callback(
    [Output("species-markers", "children"),
     Output("species-collection-map", "bounds")],
    Input("common-species-dropdown", "value"))
def update_species_map(selected_species: str) -> tuple[list[Any], list[Any]]:
    if selected_species:
        # Nur Einträge mit Vorkommen der Spezies
        filtered_df = df[df[selected_species] > 0].copy()
        if not filtered_df.empty:
            markers = []
            for _, row in filtered_df.iterrows():
                unique_id = str(uuid.uuid4())
                markers.append(dl.CircleMarker(
                    id=unique_id,
                    center=[row['latitude'], row['longitude']],
                    radius=8,
                    color='black',
                    fillColor=get_species_color(selected_species),
                    fillOpacity=0.6,
                    children=dl.Tooltip(f"{selected_species}")))



            # Berechne die Bounds der Marker
            lats = filtered_df['latitude'].tolist()
            longs = filtered_df['longitude'].tolist()
            if lats and longs:
                min_lat = min(lats)
                max_lat = max(lats)
                min_lon = min(longs)
                max_lon = max(longs)
                bounds = [[min_lat, min_lon], [max_lat, max_lon]]
                return markers, bounds
    return [], []  # Keine Marker, keine Bounds


# Run the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
