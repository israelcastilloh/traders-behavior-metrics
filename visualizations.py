
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Herramientas para el análisis del desempeño de la actividad de trading                     -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: ramirezdiana, israelcastilloh, CristinaCruzD                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_equipo6_lab3                                       -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import plotly.graph_objects as go
import functions as fn


def pie_ranking(x, y):
    """
    :param x: serie de etiquetas para un pie chart
    :param y: serie de datos para el pie chart
    :return: la visualización de un pie chart
    """
    labels = x.tolist()
    y = y.tolist()
    values = []
    [values.append(string.replace("%", "")) for string in y]
    pull = []
    val = values[0]
    for x in values:
        if x == val:
            pull.append(.1)
        else:
            pull.append(0)
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=pull)])
    fig.update_traces(textposition='inside')
    fig.update_layout(title='Ranking')
    return fig


def graph_draw(param_data):
    """
    :param param_data: dataframe base
    :return: grafica con drawup y drawdown
    """
    values = fn.f_evolucion_capital(param_data)
    if len(values.columns) == 3:
        values = values.set_index("timestamp", drop=True)
        values = values.drop("profit_d", axis=1)
    u1, u2, u3 = fn.draw(values, "up")
    d1, d2, d3 = fn.draw(values, "down")
    down = values[(values.index >= d2) & (values.index <= d3)]
    up = values[(values.index >= u2) & (values.index <= u3)]
    down = down.iloc[[0, -1], :]
    up = up.iloc[[0, -1], :]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=values.index, y=values["profit_acm_d"], mode='lines', name='capital en cuenta'))
    fig.add_trace(go.Scatter(x=up.index, y=up["profit_acm_d"], mode='lines', name='up'))
    fig.add_trace(go.Scatter(x=down.index, y=down["profit_acm_d"], mode='lines', name='down'))
    fig.update_layout(title='Cuenta', xaxis_title='Tiempo (días)', yaxis_title='Dinero en cuenta ($)')
    return fig


def bar_chart(d1, d2, d3):
    """
    :param d1: lista con 1 si ocurrió el sesgo por status quo, 0 si no ocurrió
    :param d2: lista con 1 si ocurrió el sesgo por aversión a la perdida, 0 si no ocurrió
    :param d3: lista con 1 si ocurrió el sesgo por sensibilidad decreciente, 0 si no ocurrió
    :return: grafica de barras con la suma de la ocurrencia de estas causas del sesgo
    """
    x = ["Status Quo", "Aversión a la pérdida", "Sensibilidad decreciente"]
    y = [sum(d1), sum(d2), sum(d3)]
    fig = go.Figure([go.Bar(x=x, y=y)])
    fig.update_layout(title='Disposition Effect', xaxis_title='Sesgos', yaxis_title='Cantidad de ocurrencias')
    return fig