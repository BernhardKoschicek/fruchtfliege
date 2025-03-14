import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("My First Dash App"),
    dcc.Input(id="input-text", type="text", placeholder="Enter text..."),
    html.Button("Submit", id="submit-btn", n_clicks=0),
    html.Div(id="output-div")])


@app.callback(
    Output("output-div", "children"),
    Input("submit-btn", "n_clicks"),
    prevent_initial_call=True)


def update_output(n_clicks):
    return f"Button clicked {n_clicks} times!"


if __name__ == "__main__":
    app.run(debug=True)
