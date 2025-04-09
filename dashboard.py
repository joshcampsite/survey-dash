import dash
import dash_bootstrap_components as dbc
from dash import html

# Use the correct theme from your original code
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server # Gunicorn needs this variable

app.layout = html.Div([
    html.H1("Minimal Test App"),
    html.P("If you see this, the basic app loaded!")
])