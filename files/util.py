import numpy as np

from files.data import max_flies, min_flies, species_list, species_rank


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
