import numpy as np
import dash_leaflet as dl
from dash import html, dcc
import dash_leaflet as dl
import dash_html_components as html
import pandas as pd

from files.data import df, max_flies, min_flies, species_list, species_rank


def get_color(value: str) -> str:
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





def make_popup(participant: str, species_totals: pd.DataFrame) -> dl.Popup:
    # Extrahiere die Summe für den Teilnehmer
    total_flies = int(species_totals['Total per Sample'].iloc[0])  # Gesamtzahl der Fliegen für den Teilnehmer
    species_data = {key: int(species_totals[key].iloc[0]) for key in species_totals.columns if key != 'sampleId' and key != 'Total per Sample'}

    # HTML-Inhalt für das Popup erstellen
    popup_content = f"""
        <strong>Participant:</strong> {participant}<br>
        <strong>Total Flies:</strong> {total_flies}<br>
        <strong>melanogaster:</strong> {species_data['melanogaster']}<br>
        <strong>simulans:</strong> {species_data['simulans']}<br>
        <strong>suzukii:</strong> {species_data['suzukii']}<br>
        <strong>busckii:</strong> {species_data['busckii']}<br>
        <strong>testacea:</strong> {species_data['testacea']}<br>
        <strong>hydei:</strong> {species_data['hydei']}<br>
        <strong>mercatorum:</strong> {species_data['mercatorum']}<br>
        <strong>repleta:</strong> {species_data['repleta']}<br>
        <strong>funebris:</strong> {species_data['funebris']}<br>
        <strong>immigrans:</strong> {species_data['immigrans']}<br>
        <strong>phalerata:</strong> {species_data['phalerata']}<br>
        <strong>subobscura:</strong> {species_data['subobscura']}<br>
        <strong>virilis:</strong> {species_data['virilis']}<br>
    """

    # Popup mit Markdown für HTML-Inhalt zurückgeben
    return dl.Popup(
        children=[dcc.Markdown(popup_content, dangerously_allow_html=True)],
        maxWidth='300px',  # Popup-Breite anpassen
        maxHeight='400px',  # Popup-Höhe anpassen
        closeButton=True,  # Schließen-Button hinzufügen
        autoClose=True,  # Popup schließt automatisch bei Klick
    )



# Funktion zur Farbkodierung
def get_species_color(species: str) -> str:
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
