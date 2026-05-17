# Capa gráfica: definición del layout de la aplicación
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from data import df

layout = html.Div([
    # Header con título (ancho completo)
    html.Header(
        html.H1("Aplicaciones I", style={"textAlign": "center", "color": "white", "margin": "0", "padding": "20px 0"}),
        style={"backgroundColor": "#00184a"}
    ),

    # Contenido principal dentro de un Container responsive
    dbc.Container([
        # Subtítulo
        dbc.Row(
            dbc.Col(html.H2("Ejemplo de Aplicación web interactiva con Dash", style={"textAlign": "center"}), width=12),
            className="mt-4"
        ),
        html.Br(),
        # Descripción
        dbc.Row(
            dbc.Col(html.P(
                "Esta aplicación muestra la evolución de la población de diferentes países a lo largo del tiempo. "
                "Selecciona un país en el menú desplegable para ver su gráfico de población."
            ), width=12),
            className="mt-2"
        ),
        # Dropdown
        dbc.Row(
            dbc.Col([
                html.Label("Selecciona un país:"),
                dcc.Dropdown(df.country.unique(), "Colombia", id="dropdown-selection"),
            ], xs=12, sm=8, md=6, lg=4),
            className="mt-3"
        ),
        # Título del gráfico
        dbc.Row(
            dbc.Col(html.H3("Evolución de la población", style={"textAlign": "center"}), width=12),
            className="mt-4"
        ),
        # Gráfico
        dbc.Row(
            dbc.Col(
                html.Div(
                    dcc.Graph(id="graph-content", responsive=True, style={"height": "450px"}),
                    style={"border": "1px solid #c0c0c0", "borderRadius": "8px",
                           "overflow": "hidden", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}
                ),
                xs=12, lg=10, className="mx-auto"
            ),
            className="mb-3"
        ),
        html.Br(),
        # Título dinámico de la tabla
        dbc.Row(
            dbc.Col(html.H3(id="table-title", children="Datos del país seleccionado",
                            style={"textAlign": "center"}), width=12),
            className="mt-2"
        ),
        # Tabla
        dbc.Row(
            dbc.Col(
                html.Div(
                    dash_table.DataTable(
                        id="table-content",
                        columns=[
                            {"name": "Año",            "id": "year"},
                            {"name": "Población",      "id": "pop"},
                            {"name": "Esperanza de vida (años)",   "id": "lifeExp"},
                            {"name": "PIB per cápita", "id": "gdpPercap"},
                        ],
                        page_size=10,
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "#00184a",
                            "color": "white",
                            "fontWeight": "bold",
                            "textAlign": "center",
                        },
                        style_cell={
                            "textAlign": "center",
                            "padding": "8px",
                            "fontFamily": "Roboto, sans-serif",
                        },
                        style_data_conditional=[
                            {"if": {"row_index": "odd"}, "backgroundColor": "#eef0f8"}
                        ],
                    ),
                    style={"border": "1px solid #c0c0c0", "borderRadius": "8px",
                           "overflow": "hidden", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}
                ),
                xs=12, lg=10, className="mx-auto"
            ),
            className="mb-5"
        ),
    ], fluid=True),

    # Footer
    html.Footer(
        "Creado por Camilo A. Castañeda Galindo - 2026",
        style={
            "backgroundColor": "#00184a",
            "color": "white",
            "textAlign": "center",
            "padding": "16px",
            "marginTop": "auto",
            "fontSize": "0.9rem",
        }
    ),

], style={"backgroundColor": "#F2F3F8", "minHeight": "100vh", "fontFamily": "Roboto, sans-serif", "fontSize": "1.1rem", "display": "flex", "flexDirection": "column"})
