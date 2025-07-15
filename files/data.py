# Load CSV
import pandas as pd

df = pd.read_csv("flies.csv").fillna(0)

# Ensure total_flies column is numeric
df["total_flies"] = pd.to_numeric(df["total_flies"], errors="coerce").fillna(0)

# Get min and max for normalization
min_flies = df["total_flies"].min()
max_flies = df["total_flies"].max()

# List of species to include in the table
species_list = [
    'melanogaster',
    'simulans',
    'suzukii',
    'busckii',
    'testacea',
    'hydei',
    'mercatorum',
    'repleta',
    'funebris',
    'immigrans',
    'phalerata',
    'subobscura',
    'virilis']
df[species_list] = df[species_list].astype(int)
# Häufigkeit der Arten berechnen
species_counts = {species: df[species].sum() for species in species_list}

# Arten nach Häufigkeit sortieren
sorted_species = sorted(
    species_counts.items(), key=lambda x: x[1], reverse=True)
species_rank = {
    species: rank for rank, (species, _) in enumerate(sorted_species)}

# # Get unique participant names
# participants = sorted(df["participants"].dropna().unique())

# def get_species_data():
#     # Alle Spalten mit Arten summieren pro participantid
#     df_sum = df.groupby("participants")[species_list].sum().reset_index()
#
#     # Gesamtzahl aller Fliegen pro participant berechnen
#     df_sum["total_flies"] = df_sum.iloc[:, 1:].sum(axis=1)
#
#     # Eine Zeile mit der Summe aller Fliegen über alle Teilnehmer hinzufügen
#     total_row = df_sum[species_list].sum().to_frame().T
#     total_row["participants"] = "TOTAL"
#     total_row["total_flies"] = total_row[species_list].sum(axis=1)
#
#     # Die Gesamtzeile an die Tabelle anhängen
#     df_final = pd.concat([df_sum, total_row], ignore_index=True)
#
#     # Rückgabe als Liste von Dictionaries (für Dash)
#     return df_final.to_dict("records")


