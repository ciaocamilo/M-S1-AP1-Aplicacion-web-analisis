# Lógica: callbacks de la aplicación
from dash import Output, Input
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

from app import app
from data import df_nofetal

_AZUL       = '#00184a'
_ROJO_CLARO = '#e07b7b'
_GRIS       = '#a0a0a0'

_MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo',  6: 'Junio',   7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
}

_ORDEN_EDAD = [
    'Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia',
    'Niñez', 'Adolescencia', 'Juventud',
    'Adultez temprana', 'Adultez intermedia', 'Vejez',
]


def _filtrar(causa):
    if not causa or causa == 'ALL':
        return df_nofetal
    return df_nofetal[df_nofetal['MANERA_MUERTE'] == causa]


# Generadores de figuras (reutilizables por gui.py para la carga inicial)

def build_mapa(dff):
    muertes_dpto = (
        dff
        .dropna(subset=['COD_DEPARTAMENTO', 'DEPARTAMENTO'])
        .groupby(['COD_DEPARTAMENTO', 'DEPARTAMENTO'])
        .size()
        .reset_index(name='TOTAL_MUERTES')
    )
    fig = px.choropleth(
        muertes_dpto,
        geojson='/assets/Colombia.geo.json',
        locations='COD_DEPARTAMENTO',
        featureidkey='properties.DPTO',
        color='TOTAL_MUERTES',
        hover_name='DEPARTAMENTO',
        color_continuous_scale='Blues',
        labels={'TOTAL_MUERTES': 'Total muertes'},
    )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        template='plotly_white',
        coloraxis_colorbar_title='Muertes',
        margin=dict(l=0, r=0, t=10, b=10),
        height=480,
    )
    return fig


def build_graficos(dff):
    # Líneas
    mes_data = (
        dff.groupby('MES').size()
        .reset_index(name='TOTAL_MUERTES')
        .sort_values('MES')
    )
    mes_data['MES_NOMBRE'] = mes_data['MES'].map(_MESES)
    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(
        x=mes_data['MES_NOMBRE'],
        y=mes_data['TOTAL_MUERTES'],
        mode='lines+markers',
        line=dict(color=_AZUL, width=2.5),
        marker=dict(size=9, color=_AZUL),
        hovertemplate='<b>%{x}</b><br>Muertes: %{y:,}<extra></extra>',
    ))
    fig_lineas.update_layout(
        template='plotly_white',
        xaxis_title='<b>Mes</b>',
        yaxis_title='<b>Número de muertes</b>',
        hovermode='x unified',
        margin=dict(l=50, r=20, t=20, b=70),
        height=390,
        xaxis=dict(tickangle=-30),
    )

    # Torta
    ciudades_min = (
        dff.dropna(subset=['MUNICIPIO']).groupby('MUNICIPIO').size()
        .reset_index(name='TOTAL_MUERTES')
        .sort_values('TOTAL_MUERTES').head(10)
    )
    fig_pie = px.pie(
        ciudades_min,
        values='TOTAL_MUERTES',
        names='MUNICIPIO',
        hole=0.38,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Muertes: %{value}<extra></extra>',
    )
    fig_pie.update_layout(
        template='plotly_white',
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=20),
        height=390,
    )

    # Barras apiladas
    sexo_dpto = (
        dff.dropna(subset=['DEPARTAMENTO', 'SEXO'])
        .groupby(['DEPARTAMENTO', 'SEXO']).size()
        .reset_index(name='TOTAL_MUERTES')
    )
    sexo_dpto['DEPARTAMENTO'] = sexo_dpto['DEPARTAMENTO'].apply(
        lambda x: x[:24] + '...' if len(x) > 27 else x
    )
    fig_sexo = px.bar(
        sexo_dpto.sort_values('DEPARTAMENTO'),
        x='DEPARTAMENTO',
        y='TOTAL_MUERTES',
        color='SEXO',
        barmode='stack',
        color_discrete_map={
            'Masculino':     _AZUL,
            'Femenino':      _ROJO_CLARO,
            'Indeterminado': _GRIS,
        },
        labels={
            'TOTAL_MUERTES': 'Número de muertes',
            'DEPARTAMENTO':  'Departamento',
            'SEXO':          'Sexo',
        },
    )
    fig_sexo.update_layout(
        template='plotly_white',
        xaxis_title='<b>Departamento</b>',
        yaxis_title='<b>Número de muertes</b>',
        xaxis_tickangle=-40,
        margin=dict(l=50, r=20, t=20, b=130),
        height=500,
        legend_title_text='Sexo',
    )

    # Histograma
    conteo_edad = dff['CATEGORIA_EDAD'].value_counts()
    edad_data = pd.DataFrame({
        'CATEGORIA_EDAD': _ORDEN_EDAD,
        'TOTAL_MUERTES':  [int(conteo_edad.get(c, 0)) for c in _ORDEN_EDAD],
    })
    fig_histograma = px.bar(
        edad_data,
        x='CATEGORIA_EDAD',
        y='TOTAL_MUERTES',
        color='TOTAL_MUERTES',
        color_continuous_scale='Blues',
        labels={
            'CATEGORIA_EDAD': 'Grupo de edad',
            'TOTAL_MUERTES':  'Número de muertes',
        },
        text='TOTAL_MUERTES',
    )
    fig_histograma.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_histograma.update_layout(
        template='plotly_white',
        xaxis_title='<b>Grupo de edad</b>',
        yaxis_title='<b>Número de muertes</b>',
        coloraxis_showscale=False,
        xaxis_tickangle=-25,
        margin=dict(l=50, r=20, t=30, b=90),
        height=440,
    )

    return fig_lineas, fig_pie, fig_sexo, fig_histograma


# Callback único: todos los gráficos en una sola llamada
@app.callback(
    Output('graph-mapa',        'figure'),
    Output('graph-lineas',      'figure'),
    Output('graph-pie',         'figure'),
    Output('graph-sexo',        'figure'),
    Output('graph-histograma',  'figure'),
    Output('titulo-mapa',       'children'),
    Output('titulo-lineas',     'children'),
    Output('titulo-pie',        'children'),
    Output('titulo-sexo',       'children'),
    Output('titulo-histograma', 'children'),
    Input('dropdown-causa',     'value'),
)
# Al cambiar la causa de muerte seleccionada en el dropdown, se filtran los datos y se regeneran todas las figuras con la función build_graficos() y build_mapa()
def update_todos(causa):
    dff = _filtrar(causa)
    fig_mapa = build_mapa(dff)
    fig_lineas, fig_pie, fig_sexo, fig_histograma = build_graficos(dff)
    sufijo = f' ({causa})' if causa and causa != 'ALL' else ''
    return (
        fig_mapa, fig_lineas, fig_pie, fig_sexo, fig_histograma,
        f'Distribución total de muertes por departamento{sufijo}',
        f'Total de muertes por mes en Colombia{sufijo}',
        f'10 ciudades con menor índice de mortalidad{sufijo}',
        f'Total de muertes por género en cada departamento{sufijo}',
        f'Distribución de muertes por grupo de edad{sufijo}',
    )

