from typing import Any

import dash_leaflet as dl
from dash import dash_table, dcc, html
from dash.html import Div, Img
from dash_leaflet import MapContainer

from files.data import df, species_list


def get_logo() -> Img:
    logo = (
        "https://fairicube.wp2.nilu.no/wp-content/uploads/sites/21/2024/04/"
        "Logo-cityfly.png")
    return html.Img(src=logo, style={'width': '200px'})


def get_participant_map_div() -> Div:
    return html.Div(
        style={
            'resize': 'both',
            'overflow': 'auto',
            'border': '1px solid black',
            'height': '650px',
            'width': '100%',
            'padding': '0',
            'display': 'flex',
            'flexDirection': 'column'},
        children=[
            dcc.Dropdown(
                id='participant-dropdown',
                options=[
                    {'label': p, 'value': p} for p in
                    sorted(df['participants'].unique())],
                value=df['participants'].unique()[0]  # Initialer Wert
            ),
            html.Div(
                id='map-container',
                style={
                    'flex': '1',
                    'border': '0px solid black',
                    'position': 'relative',
                    # Korrigiert die Breite um die Randlinie
                    'width': 'calc(100% - 2px)',
                    # Falls die Höhe auch betroffen ist
                    'height': 'calc(100% - 2px)',
                    # Entfernt zusätzliches Padding
                    'padding': '0',
                    # Sorgt dafür, dass Border und Padding in die 100%
                    # einberechnet werden
                    'box-sizing': 'border-box'},
                # Wichtig: position: relative
                children=[
                    dl.Map(
                        id="map",
                        children=[
                            dl.TileLayer(), dl.LayerGroup(id="markers")],
                        center=[
                            df["latitude"].mean(), df["longitude"].mean()],
                        zoom=8,
                        style={
                            "height": "100%",
                            "width": "100%",
                            "position": "absolute"
                        }), ], ),
            html.Script("""
                    const mapContainer = document.getElementById(
                    'map-container');
                    const resizeObserver = new ResizeObserver(entries => {
                        for (let entry of entries) {
                            if (entry.target === mapContainer) {
                                const size = {width: 
                                entry.contentRect.width, height: 
                                entry.contentRect.height };
                                // Hier könntest du das 'size'-Property des 
                                map-container-Divs direkt manipulieren,
                                // um den Clientside-Callback auszulösen (
                                Workaround).
                                mapContainer.setAttribute('data-size', 
                                JSON.stringify(size));
                                // Oder du verwendest ein CustomEvent (
                                sauberer):
                                mapContainer.dispatchEvent(new CustomEvent(
                                'containerResize', { detail: size }));
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
    )


def get_species_details() -> Div:
    return html.Div([
        dcc.Dropdown(
            id='common-species-dropdown',
            options=[{'label': s, 'value': s} for s in species_list],
            value=species_list[0]  # Initialwert
        ),
        html.Div(
            style={'display': 'flex'},
            children=[
                html.Div(
                    style={
                        'flex': '1',
                        'resize': 'both',
                        'overflow': 'auto',
                        'border': '1px solid black'},
                    children=[
                        html.H3("Species Collection Trend Over Time"),
                        dcc.Graph(id="species-time-series")
                    ]
                ),
                html.Div(
                    id='species-info',
                    style={
                        'flex': '1',
                        'resize': 'both',
                        'overflow': 'auto',
                        'border': '1px solid black'},
                    children=[
                        html.H3("Species Info"),
                        html.Div("Select a species to see details.")]
                )
            ]
        ),
        # Die Karte wird jetzt hier außerhalb des flex-Containers platziert
        html.Div(
            style={
                'width': '100%',
                'resize': 'both',
                'overflow': 'auto',
                'border': '1px solid black',
                'margin-top': '20px'},
            children=[
                html.H3("Species Collection Map"),
                dl.Map(
                    id="species-collection-map",
                    children=[
                        dl.TileLayer(),
                        dl.LayerGroup(id="species-markers")],
                    center=[df["latitude"].mean(), df["longitude"].mean()],
                    # Verwende den Durchschnitt aller Koordinaten als
                    # initialen Center
                    zoom=8,
                    style={"height": "600px", "width": "100%"})])])


def layout() -> Div:
    return html.Div(
        className="container",
        children=[
            get_logo(),
            html.Div(children=[html.H1("Vienna City Fly 2025")]),
            get_participant_map_div(),
            get_sample_table(),
            get_sample_pie_chart(),

            get_species_details()])


def participant_map() -> MapContainer:
    return dl.Map(
        id="map",
        children=[
            dl.TileLayer(),
            # Stelle sicher, dass dies vorhanden ist
            dl.LayerGroup(id="markers")],
        center=[df["latitude"].mean(), df["longitude"].mean()],
        zoom=10,
        style={
            "width": "100%",
            "height": "500px",  # Höhe anpassen, falls nötig
            "margin": "0",
            "padding": "0",
            # Stellt sicher, dass Padding/Margin nicht die Breite verändert
            "box-sizing": "border-box",
            "overflow": "hidden"})  # Verhindert Scrollbalken


def get_sample_table() -> Div:
    return html.Div(
        children=[
            html.H3("Species Counts by Sample ID"),
            dash_table.DataTable(
                id='species-table',
                columns=[
                    {'name': 'Sample ID', 'id': 'sampleId'},
                    *[{'name': species, 'id': species} for species in
                      species_list],
                    {'name': 'Total per Sample', 'id': 'Total per Sample'},
                    # Add species columns
                ],
                style_table={'height': '400px', 'overflowY': 'auto'},
                # Enable scrolling if needed
                style_cell={
                    'textAlign': 'center',
                    'minWidth': '80px',
                    'width': '80px',
                    'maxWidth': '80px'},
                style_header={
                    'backgroundColor':
                        'lightgray',
                    'fontWeight': 'bold'}, )],
        style={
            'resize': 'both',
            'overflow': 'auto',
            'border': '1px solid black'})


def get_sample_pie_chart() -> Div:
    return html.Div(
        children=[
            html.H3('Species Distribution'),
            # Sample ID selection (populated dynamically)
            dcc.Dropdown(
                id="sample-dropdown",
                placeholder="Select a sample ID",
                clearable=True),
            html.Div(
                style={'display': 'flex'},  # Flexbox-Container
                children=[
                    dcc.Graph(
                        id='sample-species-pie-chart',
                        style={'flex': '1'}),  # Pie-Chart für Sample
                    dcc.Graph(
                        id='participant-species-pie-chart',
                        style={'flex': '1'})])],  # Pie-Chart für Participant

        style={
            'resize': 'both',
            'overflow': 'auto',
            'border': '1px solid black'}
    )


def species_time_series() -> list[Any]:
    return [
        html.H3("Species Collection Trend Over Time"),
        dcc.Dropdown(
            id="species-dropdown",
            options=[
                {"label": species, "value": species}
                for species in species_list],
            placeholder="Select a species",
            clearable=True),
        dcc.Graph(id="species-time-series")]


def species_map() -> list[Any]:
    return [
        html.H3("Species Collection Map"),
        dcc.Dropdown(
            id="common-species-dropdown",
            options=[{"label": s, "value": s} for s in species_list],
            placeholder="Select a species",
            clearable=True),
        dl.Map(
            id="species-collection-map",
            children=[
                dl.TileLayer(),
                dl.FitBounds(children=dl.LayerGroup(id="species-markers"))],
            # Diese Standardeinstellungen werden überschrieben,
            # wenn Bounds vorhanden sind
            center=[48.2082, 16.3738],
            zoom=10,
            style={"height": "600p", "width": "600p"})]
