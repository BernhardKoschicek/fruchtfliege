from typing import Any

import pandas as pd
import dash_leaflet as dl
import plotly.graph_objects as go

from dash import dash_table, dcc, html
from dash.html import Div, Img
from dash_leaflet import MapContainer
from files.data import df, species_list
from files.util import get_color, get_species_color, make_popup

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
                value=None  # Initialer Wert
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
                        zoom=10,
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
                        html.H3("Arten nach der Zeit", style={'padding': '10px'}),
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
                html.H3("Verbreitungskarte Arten", style={'padding': '10px'} ),
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
            html.H3("Artenverteilung nach Falle"),
            dash_table.DataTable(
                id='species-table',
                columns=[
                    {'name': 'Sample ID', 'id': 'sampleId'},
                    *[{'name': species, 'id': species} for species in species_list],
                    {'name': 'Total per Sample', 'id': 'Total per Sample'},
                ],
                style_table={'height': '400px', 'overflowY': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'minWidth': '80px',
                    'width': '80px',
                    'maxWidth': '80px'},
                style_header={
                    'backgroundColor': 'lightgray',
                    'fontWeight': 'bold'
                },
                data=df.to_dict('records')
            ),
            html.Div(style={'marginTop': '10px'}, children=[
                dcc.RadioItems(
                    id='download-option',
                    options=[
                        {'label': 'Nur gewählter Teilnehmer', 'value': 'selected'},
                        {'label': 'Gesamte Tabelle', 'value': 'all'}
                    ],
                    value='selected',
                    labelStyle={'display': 'block'}
                ),
                html.Button("Download Tabelle", id="download-button"),
                dcc.Download(id="download-data")
            ])
        ],
        style={
            'resize': 'both',
            'overflow': 'auto',
            'border': '1px solid black',
            'padding': '10px'  # Padding für besseres Layout
        }
    )




def get_sample_pie_chart() -> html.Div:
    # Berechnung der Gesamtanzahl der Fliegen pro Art (wenn nicht schon in der Datenvorbereitung erledigt)
    species_counts = {species: df[species].sum() for species in species_list}

    labels = list(species_counts.keys())  # Artennamen
    values = list(species_counts.values())  # Häufigkeit der Arten

    # Farbliste basierend auf den bereits definierten Farben (diese Farben wurden für die anderen Pie-Charts verwendet)
    colors = [get_species_color(species) for species in labels]

    # Pie-Chart erstellen
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),  # Farben aus der bestehenden Farbliste
        hoverinfo='label+percent',  # Beim Hover anzeigen
        textinfo='value', # Beschriftung mit Wert
        showlegend=True,
    )])
    fig.update_layout(
        title="Artenverteilung VCF 2024",
        showlegend=True,
        legend=dict(x=1.05,  # Position der Legende rechts
            y=1,
            traceorder='normal',
            orientation='v',  # Vertikale Legende
            xanchor='left',
            yanchor='top'
        ),
        margin=dict(l=0, r=150, b=0, t=50)
    )

    return html.Div(
        children=[
            html.H3('Die Verteilung der Arten', style={'padding': '10px'}),
            # Sample ID selection (populated dynamically)
            dcc.Dropdown(
                id="sample-dropdown",
                placeholder="Select a sample ID",
                clearable=True
            ),
            html.Div(
                style={'display': 'flex'},  # Flexbox-Container
                children=[
                    dcc.Graph(
                        id='sample-species-pie-chart',
                        style={'flex': '1', 'height': '400px', 'width': '400px'}),  # Pie-Chart für Sample
                    dcc.Graph(
                        id='participant-species-pie-chart',
                        style={'flex': '1', 'height': '400px', 'width': '400px'}),  # Pie-Chart für Participant
                    dcc.Graph(
                        id='vienna-pie-chart',  # Pie-Chart für Projekt
                        figure=fig,  # Direkt die Figure einfügen
                        style={'flex': '1', 'height': '400px', 'width': '400px'}),
                ]
            )
        ],
        style={
            'resize': 'both',
            'overflow': 'auto',
            'border': '1px solid black'
        }
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
