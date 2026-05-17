# Capa gráfica: definición del layout y las figuras de la aplicación
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from data import (
    ciudades_violentas_top5, top10_causas, opciones_causa,
)

# Paleta de colores
_AZUL       = '#00184a'
_FONDO      = '#F2F3F8'
_AZUL_BANDA = '#eef0f8'

# Estilo
_CARD = {
    'border': '1px solid #c0c0c0',
    'borderRadius': '8px',
    'overflow': 'hidden',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
    'backgroundColor': 'white',
}


def _panel(child):
    # Envuelve un dcc.Graph o DataTable en un panel con bordes
    return html.Div(child, style=_CARD)


def _titulo(texto, id=None):
    props = {'id': id} if id is not None else {}
    return html.H5(
        texto,
        style={
            'textAlign': 'center',
            'color': _AZUL,
            'marginBottom': '10px',
            'fontWeight': '600',
        },
        **props,
    )


# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICO DE BARRAS – 5 ciudades más violentas
# ════════════════════════════════════════════════════════════════════════════════
_violentas = ciudades_violentas_top5.sort_values('HOMICIDIOS', ascending=True)

fig_barras_violentas = px.bar(
    _violentas,
    x='HOMICIDIOS',
    y='MUNICIPIO',
    orientation='h',
    color='HOMICIDIOS',
    color_continuous_scale=['#ffaaaa', '#cc0000'],
    labels={'HOMICIDIOS': 'Homicidios', 'MUNICIPIO': 'Ciudad'},
    text='HOMICIDIOS',
)
fig_barras_violentas.update_traces(textposition='outside')
fig_barras_violentas.update_layout(
    template='plotly_white',
    coloraxis_showscale=False,
    xaxis_title='<b>Número de homicidios</b>',
    yaxis_title='',
    margin=dict(l=10, r=50, t=20, b=40),
    height=340,
)

# ════════════════════════════════════════════════════════════════════════════════
# TABLA – 10 principales causas de muerte
# ════════════════════════════════════════════════════════════════════════════════
_tabla_causas = dash_table.DataTable(
    data=top10_causas.to_dict('records'),
    columns=[
        {'name': 'Código',          'id': 'COD_MUERTE'},
        {'name': 'Causa de muerte', 'id': 'DESC_CIE10_4'},
        {'name': 'Total',           'id': 'TOTAL'},
    ],
    page_size=10,
    style_table={'overflowX': 'auto'},
    style_header={
        'backgroundColor': _AZUL,
        'color': 'white',
        'fontWeight': 'bold',
        'textAlign': 'center',
    },
    style_cell={
        'textAlign': 'left',
        'padding': '8px 12px',
        'fontFamily': 'Roboto, sans-serif',
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    style_cell_conditional=[
        {'if': {'column_id': 'COD_MUERTE'}, 'textAlign': 'center', 'width': '90px'},
        {'if': {'column_id': 'TOTAL'},      'textAlign': 'center', 'width': '80px'},
    ],
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': _AZUL_BANDA},
    ],
)

# ════════════════════════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════════
layout = html.Div(
    [
        # Header
        html.Header(
            html.H1(
                'Análisis de mortalidad',
                style={'textAlign': 'center', 'color': 'white',
                       'margin': '0', 'padding': '22px 0'},
            ),
            style={'backgroundColor': _AZUL},
        ),

        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        html.H2(
                            'Colombia 2019',
                            style={'textAlign': 'center'},
                        ),
                        width=12,
                    ),
                    className='mt-4 mb-1',
                ),

                # Introducción
                dbc.Row(
                    dbc.Col(
                        html.P(
                            [
                                'Esta aplicación presenta un análisis exploratorio de la ',
                                html.Strong('mortalidad en Colombia durante el año 2019'),
                                ', con base en los registros oficiales del DANE. '
                                'Los datos incluyen información sobre causas de muerte, '
                                'distribución geográfica por departamento y municipio, '
                                'comportamiento mensual, composición por género y grupos de edad. '
                                'A través de los gráficos interactivos es posible identificar patrones '
                                'y tendencias que caracterizan la mortalidad en el país durante ese período.',
                            ],
                            style={
                                'color': '#444',
                                'fontSize': '0.97rem',
                                'lineHeight': '1.7',
                                'marginTop': '32px',
                                'marginBottom': '16px',
                            },
                        ),
                        width=12,
                    ),
                    className='mb-3',
                ),

                # Filtro por causa de muerte
                dbc.Row(
                    dbc.Col(
                        [
                            html.Label(
                                'Filtrar por manera de muerte:',
                                style={'fontWeight': '600', 'color': _AZUL, 'marginBottom': '4px'},
                            ),
                            dcc.Dropdown(
                                id='dropdown-causa',
                                options=opciones_causa,
                                value='ALL',
                                clearable=False,
                                searchable=False,
                                style={'fontSize': '0.95rem'},
                            ),
                            html.Small(
                                [
                                    html.Strong('Aplica a:'),
                                    ' Muertes por departamento, muertes por mes, ciudades con menor índice de mortalidad, '
                                    'muertes por género e histograma de edad.',
                                ],
                                style={'color': '#666', 'marginTop': '4px', 'display': 'block'},
                            ),
                        ],
                        xs=12, lg=5,
                    ),
                    className='mb-4',
                ),

                # 1. Mapa
                dbc.Row(
                    dbc.Col(
                        [
                            _titulo('Distribución total de muertes por departamento', id='titulo-mapa'),
                            _panel(
                                html.Div(
                                    dcc.Graph(id='graph-mapa', responsive=True),
                                    style={'height': '480px'},
                                )
                            ),
                        ],
                        width=12,
                    ),
                    className='mb-4',
                ),
                dbc.Row(
                    [
                        # 2. Gráfico de líneas
                        dbc.Col(
                            [
                                _titulo('Total de muertes por mes en Colombia', id='titulo-lineas'),
                                _panel(
                                    html.Div(
                                        dcc.Graph(id='graph-lineas', responsive=True),
                                        style={'height': '390px'},
                                    )
                                ),
                            ],
                            xs=12, lg=7,
                            className='mb-4',
                        ),
                        # 4. Gráfico circular
                        dbc.Col(
                            [
                                _titulo('10 ciudades con menor índice de mortalidad', id='titulo-pie'),
                                _panel(
                                    html.Div(
                                        dcc.Graph(id='graph-pie', responsive=True),
                                        style={'height': '390px'},
                                    )
                                ),
                            ],
                            xs=12, lg=5,
                            className='mb-4',
                        ),
                    ],
                ),

                # 6. Gráfico de barras apiladas
                dbc.Row(
                    dbc.Col(
                        [
                            _titulo('Total de muertes por género en cada departamento', id='titulo-sexo'),
                            _panel(
                                html.Div(
                                    dcc.Graph(id='graph-sexo', responsive=True),
                                    style={'height': '500px'},
                                )
                            ),
                        ],
                        width=12,
                    ),
                    className='mb-4',
                ),

                # 7. Histograma
                dbc.Row(
                    dbc.Col(
                        [
                            _titulo('Distribución de muertes por grupo de edad', id='titulo-histograma'),
                            _panel(
                                html.Div(
                                    dcc.Graph(id='graph-histograma', responsive=True),
                                    style={'height': '440px'},
                                )
                            ),
                        ],
                        xs=12, lg=10,
                        className='mb-4 mx-auto',
                    ),
                ),
                dbc.Row(
                    [
                        # 3. Gráfico de barras
                        dbc.Col(
                            [
                                _titulo('5 ciudades más violentas (homicidios)'),
                                _panel(dcc.Graph(figure=fig_barras_violentas, responsive=True)),
                            ],
                            xs=12, lg=5,
                            className='mb-4',
                        ),
                        # 5. Tabla
                        dbc.Col(
                            [
                                _titulo('10 principales causas de muerte en Colombia'),
                                _panel(_tabla_causas),
                            ],
                            xs=12, lg=7,
                            className='mb-5',
                        ),
                    ],
                ),
            ],
            fluid=True,
        ),

        # Footer
        html.Footer(
            'Creado por Camilo A. Castañeda Galindo – 2026',
            style={
                'backgroundColor': _AZUL,
                'color': 'white',
                'textAlign': 'center',
                'padding': '16px',
                'marginTop': 'auto',
                'fontSize': '0.9rem',
            },
        ),
    ],
    style={
        'backgroundColor': _FONDO,
        'minHeight': '100vh',
        'fontFamily': 'Roboto, sans-serif',
        'fontSize': '1rem',
        'display': 'flex',
        'flexDirection': 'column',
    },
)
