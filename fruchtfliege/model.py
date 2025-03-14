import dash
from dash import dash_table, html
from flask import g

from fruchtfliege import app, dash_

dash_.layout = html.Div("Hello, Dash!")
dash_.layout = dash.html.Div([
    dash_table.DataTable(
        id='sample-table',
        columns=[{"name": col, "id": col} for col in g.df_samples.columns],
        data=g.df_samples.to_dict('records'),
        # Convert DataFrame to dict for Dash
    )
])
