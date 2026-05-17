# Instancia de la aplicación Dash
from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, title='Análisis de mortalidad en Colombia',
           external_stylesheets=[dbc.themes.BOOTSTRAP])

# Ícono y fuente de la pestaña del navegador
app.index_string = '''<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>'''
