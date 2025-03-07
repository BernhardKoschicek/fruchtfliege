import pandas as pd
from flask import g, render_template
import plotly.express as px
from fruchtfliege import app


@app.route('/')
def index() -> str:
  # Aggregate the counts for the bar chart by summing the values of each column
    aggregated_counts = g.data[g.species].sum()

    # Create a Plotly bar chart for species counts
    bar_fig = px.bar(
        x=aggregated_counts.index,  # Categories (species)
        y=aggregated_counts.values,  # Corresponding counts
        labels={'x': 'Species', 'y': 'Total Count'},  # Label axes
        title='Total Count of Each Species',  # Title of the chart
    )

    # Convert the Plotly figure to HTML
    bar_chart_html = bar_fig.to_html(full_html=False)


    return render_template('index.html', bar_chart_html=bar_chart_html)
