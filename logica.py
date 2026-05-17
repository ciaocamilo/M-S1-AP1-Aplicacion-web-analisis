# Lógica: callbacks de la aplicación
from dash import callback, Output, Input
import plotly.express as px
from data import df


@callback(
    # El callback actualiza tres componentes a la vez: el gráfico, la tabla y el título de la tabla 
    Output('graph-content', 'figure'),
    Output('table-content', 'data'),
    Output('table-title', 'children'),
    # El callback se activa cada vez que cambia el valor del dropdown (es decir, cada vez que el usuario selecciona un país diferente)
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # Filtramos el DataFrame para quedarnos solo con las filas del país seleccionado
    dff = df[df.country == value]
    # Creamos un gráfico de líneas con Plotly Express, usando el DataFrame filtrado (dff) y configurando el eje x como 'year' y el eje y como 'pop'
    fig = px.line(
        dff, x='year', y='pop',
        markers=True,
        template='plotly_white',
        color_discrete_sequence=['#00184a'],
        labels={'year': 'Año', 'pop': 'Población'}
    )
    fig.update_xaxes(title_font={"weight": "bold"})
    fig.update_yaxes(title_font={"weight": "bold"})
    fig.update_layout(transition_duration=500)
    return fig, dff.to_dict('records'), f'Datos de {value}'
