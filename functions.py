"""
 -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Herramientas para el análisis del desempeño de la actividad de trading                     -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: ramirezdiana, israelcastilloh, CristinaCruzD                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_equipo6_lab3                                       -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import data as dat
import datetime as dt
import numpy as np
import math


def f_leer_archivos(param_archivo):
    """
    :param param_archivo: ruta de la ubicacion del archivo
    :return: DataFrame con la informacion base, con los nombres de divisas arreglado
    """
    global data
    param_archivo = r"./files/" + param_archivo
    if param_archivo[-3:] == "lsx" or param_archivo[-3:] == "xls":
        data = pd.read_excel(param_archivo)
    elif param_archivo[-3:] == "csv":
        data = pd.read_csv(param_archivo)
    data["Item"] = data["Item"].replace("-e", "", regex=True)
    data = data.sort_values('Close Time', ascending=True)
    return data


def f_pip_size(param_ins):
    """
    :param param_ins: string del instrumento
    :return: integer multiplicador para obtener pips
    """
    data = dat.instruments  # información de los instrumentos
    pip = pd.DataFrame(columns=['name', 'piploc'])
    pip['name'] = [data.iloc[i]['name'] for i in range(len(data))]
    pip['piploc'] = [data.iloc[i]['pipLocation'] for i in range(len(data))]
    pip['name'] = [pip['name'][i].replace('_', '').lower() for i in range(len(data))]
    x = pip[pip['name'] == param_ins]['piploc'].values[0]
    multiplicador = 10 ** (-x)
    return multiplicador


def f_columnas_tiempo(param_data):
    """
    :param param_data: DataFrame base
    :return: Dataframe con inicio, final y segundos de duracion de cada compra o venta
    """
    col_tiempo = pd.concat([pd.to_datetime(param_data["Open Time"]), pd.to_datetime(param_data["Close Time"])], axis=1)
    col_tiempo["tiempo"] = (col_tiempo["Close Time"] - col_tiempo["Open Time"]).dt.total_seconds()
    return col_tiempo


def f_columnas_pip(param_data):
    """
    :param param_data: DataFrame base
    :return: DataFrame con pips, pips_acm y profit_acm
    """
    col_pip = param_data
    col_pip['pips'] = 0
    for i in range(len(col_pip)):
        if col_pip.loc[i, 'Type'] == 'buy':  # Compra
            col_pip.loc[i, 'pips'] = (col_pip.loc[i, 'Price.1'] - col_pip.loc[i, 'Price']) * f_pip_size(col_pip.loc[i,
                                                                                                                    'Item'])
        else:  # Venta
            col_pip.loc[i, 'pips'] = (col_pip.loc[i, 'Price'] - col_pip.loc[i, 'Price.1']) * f_pip_size(col_pip.loc[i,
                                                                                                                    'Item'])
    col_pip['pips_acm'] = col_pip['pips'].cumsum()
    col_pip['profit_acm'] = col_pip['Profit'].cumsum()
    return col_pip


def f_estadisticas_ba(param_data):
    """
    :param param_data: Dataframe base
    :return: diccionario con dos dataframes: df_1_tabla (que contiene descripcion de la cuenta)
                                            y fd_2_ranking (ratio de efectividad de cada instrumento)
    """
    param_data = f_columnas_pip(param_data)
    explicacion = ["Operaciones totales", "Operaciones ganadoras", "Operaciones ganadoras de compra",
                   "Operaciones ganadoras de venta", "Operaciones perdedoras", "Operaciones perdedoras de compra",
                   "Operaciones perdedoras de venta", "Mediana de profit de operaciones",
                   "Mediana de pips de operaciones", "Ganadoras Totales/Operaciones Totales",
                   "Ganadoras Totales/Perdedoras Totales", "Ganadoras Compras/Operaciones Totales",
                   "Ganadoras Ventas/ Operaciones Totales"]
    df_1_tabla = pd.DataFrame(columns=['valor', 'descripcion'],
                              index=['Ops totales', 'Ganadoras', 'Ganadoras_c', 'Ganadoras_v', 'Perdedoras',
                                     'Perdedoras_c',
                                     'Perdedoras_v', 'Mediana (Profit)', 'Mediana (Pips)', 'r_efectividad',
                                     'r_proporcion',
                                     'r_efectividad_c', 'r_efectividad_v'])
    # DATAFRAME 1
    df_1_tabla['valor']['Ops totales'] = len(param_data)

    df_1_tabla['valor']['Ganadoras'] = sum(1 for x in param_data.Profit if x > 0)
    df_1_tabla['valor']['Ganadoras_c'] = len(param_data[(param_data.Profit > 0) & (param_data.Type == 'buy')])
    df_1_tabla['valor']['Ganadoras_v'] = len(param_data[(param_data.Profit > 0) & (param_data.Type == 'sell')])

    df_1_tabla['valor']['Perdedoras'] = sum(1 for x in param_data.Profit if x < 0)
    df_1_tabla['valor']['Perdedoras_c'] = len(param_data[(param_data.Profit < 0) & (param_data.Type == 'buy')])
    df_1_tabla['valor']['Perdedoras_v'] = len(param_data[(param_data.Profit < 0) & (param_data.Type == 'sell')])

    df_1_tabla['valor']['Mediana (Profit)'] = param_data.Profit.median()
    df_1_tabla['valor']['Mediana (Pips)'] = param_data.pips.median()

    df_1_tabla['valor']['r_efectividad'] = round(df_1_tabla['valor']['Ganadoras'] / df_1_tabla['valor']['Ops totales'],
                                                 2)
    df_1_tabla['valor']['r_proporcion'] = round(df_1_tabla['valor']['Ganadoras'] / df_1_tabla['valor']['Perdedoras'], 2)
    df_1_tabla['valor']['r_efectividad_c'] = round(
        df_1_tabla['valor']['Ganadoras_c'] / df_1_tabla['valor']['Ops totales'], 2)
    df_1_tabla['valor']['r_efectividad_v'] = round(
        df_1_tabla['valor']['Ganadoras_v'] / df_1_tabla['valor']['Ops totales'], 2)
    df_1_tabla["descripcion"] = explicacion
    # DATAFRAME 2
    df_2_tabla = pd.DataFrame(columns=['rank'], index=param_data.Item.unique())
    for item in param_data.Item.unique():
        df_2_tabla['rank'][item] = round(len(param_data[(param_data.Profit > 0) & (param_data.Item == item)]) / len(
            param_data[(param_data.Item == item)]), 4)
    df_2_ranking = df_2_tabla.sort_values('rank', ascending=False)
    df_2_ranking['rank'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_2_ranking['rank']],
                                     index=df_2_ranking.index)
    # DICCIONARIO DE AMBAS TABLAS
    dict_estadisticas = {'df_1_tabla': df_1_tabla, 'df_2_ranking': df_2_ranking}
    return dict_estadisticas


def f_profit_acm_d(param_data):
    """
    :param param_data: DataFrame base
    :return: Dataframe de 1 columna con evolucion de capital
    """
    columnas = f_columnas_pip(param_data)
    column = pd.DataFrame(columnas, columns=["Close Time", 'profit_acm'])
    column = column.set_index("Close Time", drop=True)
    column["profit_acm_d"] = 100000 + column["profit_acm"]
    column = column.drop("profit_acm", axis=1)
    return column


def f_evolucion_capital(param_data):
    """
    :param param_data: Dataframe base
    :return: DataFrame con valor de capital diario
    """
    param_data["Close Time"] = pd.to_datetime(param_data["Close Time"])
    param_data["Open Time"] = pd.to_datetime(param_data["Open Time"])
    df = pd.DataFrame(param_data, columns=['Close Time', 'Profit'])
    dates = pd.DataFrame(param_data, columns=['Open Time'])
    dates["Profit2"] = 0
    dates.columns = ["Close Time", "Profit2"]
    dates = dates.groupby([dates['Close Time'].dt.date])['Profit2'].sum()
    dates = pd.Series.to_frame(dates)
    df = df.groupby([df['Close Time'].dt.date])['Profit'].sum()
    df = pd.Series.to_frame(df)
    join = pd.merge(dates, df, how="outer", left_index=True, right_index=True)
    join['Profit'] = join['Profit'].fillna(0)
    del join["Profit2"]
    join["profit_acm_d"] = 100000 + join["Profit"].cumsum()
    join = join.reset_index()
    join.columns = ["timestamp", "profit_d", "profit_acm_d"]
    return join


def f_estadisticas_mad(param_data):
    """
     :param param_data: Dataframe base
     :return: Métricas de atribucion al desempeño
     """
    values = f_evolucion_capital(param_data)
    if len(values.columns) == 3:
        values = values.set_index("timestamp", drop=True)
        values = values.drop("profit_d", axis=1)
    df = pd.DataFrame(columns=['metrica', 'valor', 'descripcion'])
    df['metrica'] = ['sharpe', 'drawdown_capi', 'drawup_capi']
    df['descripcion'] = ['Sharpe Ratio', 'DrawDown de Capital', 'DrawUp de Capital']
    rp = np.mean(np.log(values) - np.log(values.shift(1)))[0]
    sdp = np.std(np.log(values) - np.log(values.shift(1)))[0]
    df['valor'][0] = (rp - 0.05 / 300) / sdp
    d1, d2, d3 = draw(values, "down")
    u1, u2, u3 = draw(values, "up")
    df['valor'][1] = [d2, d3, d1]
    df['valor'][2] = [u2, u3, u1]
    return df


def draw(values, method):
    nuevo, init, fin = [], [], []
    value_list = values["profit_acm_d"].tolist()
    for cont in range(0, len(value_list)):
        param = value_list[cont]
        rest_list = value_list[cont + 1:]
        for elemento in rest_list:
            if method == "down":
                nuevo.append(param - elemento)
                init.append(param)
                fin.append(elemento)
            if method == "up":
                nuevo.append(elemento - param)
                init.append(param)
                fin.append(elemento)
    x1 = max(nuevo)
    ind = nuevo.index(x1)
    x2 = values.index[values['profit_acm_d'] == init[ind]].tolist()[0]
    x3 = values.index[values['profit_acm_d'] == fin[ind]].tolist()[0]
    return x1, x2, x3


from masivos import *


def f_be_de(param_data):
    """

    :param param_data: dataframe con profit acumulado
    :return: diccionario con ocurrencias del disposicional effect
    """
    param_data['profit_acm'] = param_data['profit_acm']+100000
    param_data = param_data.reset_index(drop=True)
    ganadoras = param_data[param_data.Profit > 0]
    ganadoras = ganadoras.reset_index(drop=True)
    other = param_data
    status_q = []
    av_perdida = []
    sens1 = []
    dict_c = {}
    l = 0
    for x in ganadoras.index:
        perdedoras = pd.DataFrame(columns=other.columns)
        profits = []
        for y in other.index:
            if other.loc[y, 'Open Time'] < ganadoras.loc[x, 'Close Time'] < other.loc[y, 'Close Time']:
                oa_token = '4d5aad4aa2939a132fe264df7592d9ab-6a99aceb020a93917af53376dbb1a8d5'
                oa_in = str(other.loc[y, 'Item']).upper()  # Instrumento
                oa_in = oa_in[:3] + '_' + oa_in[3:]
                oa_gn = "M1"  # Granularidad de velas (M1: Minuto, M5: 5 Minutos, M15: 15 Minutos)
                ffin = pd.to_datetime(ganadoras.loc[x, 'Close Time']).tz_localize('GMT').floor('60S')  # Fecha final
                # fini = pd.to_datetime(other.loc[y, 'Open Time']).tz_localize('GMT')  # Fecha inicial
                fini = ffin - dt.timedelta(minutes=800)
                precios = f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=oa_gn, p3_inst=oa_in, p4_oatk=oa_token,
                                            p5_ginc=4900)
                float_price = precios.iloc[-1, -1]
                if other.loc[y, 'Type'] == "buy" and float_price < other.loc[y, 'Price']:
                    perdedoras = perdedoras.append(other.loc[y], ignore_index=True)
                    profits.append((other.loc[y, 'Price'] - float_price)*f_pip_size(other.loc[y, 'Item']) *
                                   other.loc[y, 'Size'])
                elif other.loc[y, 'Type'] == "sell" and float_price > other.loc[y, 'Price']:
                    perdedoras = perdedoras.append(other.loc[y], ignore_index=True)
                    profits.append((float_price - other.loc[y, 'Price'])*f_pip_size(other.loc[y, 'Item']) *
                                   other.loc[y, 'Size'])
        if len(perdedoras) != 0:
            l += 1
            perdedoras["profit_capital"] = profits
            selected = perdedoras[perdedoras["profit_capital"] == max(perdedoras["profit_capital"])]
            selected = selected.reset_index(drop=True)
            dict_c['ocurrencia_' + str(l)] = {'timestamp': ganadoras.loc[x, 'Close Time'],
                                              'operaciones': {
                                                  'ganadora':
                                                      {'instrumento': ganadoras.loc[x, 'Item'],
                                                       'volumen': ganadoras.loc[x, 'Size'],
                                                       'sentido': ganadoras.loc[x, 'Type'],
                                                       'profit_ganadora': ganadoras.loc[x, 'Profit']},
                                                  'perdedora':
                                                      {'instrumento': selected.loc[0, 'Item'],
                                                       'volumen': selected.loc[0, 'Size'],
                                                       'sentido': selected.loc[0, 'Type'],
                                                       'profit_perdedora': -selected.loc[0, 'profit_capital']}},
                                              'ratio_cp_profit_acm': -selected.loc[0, 'profit_capital']/ganadoras.loc[x, 'profit_acm'],
                                              'ratio_cg_profit_acm': ganadoras.loc[x, 'Profit']/ganadoras.loc[x, 'profit_acm'],
                                              'ratio_cp_cg': -selected.loc[0, 'profit_capital']/ganadoras.loc[x, 'Profit']}
            if selected.loc[0, 'profit_capital']/ganadoras.loc[x, 'profit_acm'] < ganadoras.loc[x, 'Profit']/ganadoras.loc[x, 'profit_acm']:
                status_q.append(1)
            else:
                status_q.append(0)
            if selected.loc[0, 'profit_capital']/ganadoras.loc[x, 'Profit'] > 2:
                av_perdida.append(1)
            else:
                av_perdida.append(0)
            if l == 1:
                profit_gen_init = ganadoras.loc[x, 'profit_acm']
                profit_ganadora_init = ganadoras.loc[x, 'Profit']
                profit_perdedora_init = selected.loc[0, 'profit_capital']
            if l != 1:
                temp = 0
                profit_gen_med = ganadoras.loc[x, 'profit_acm']
                profit_ganadora_med = ganadoras.loc[x, 'Profit']
                profit_perdedora_med = selected.loc[0, 'profit_capital']
                if profit_gen_med > profit_gen_init:
                    temp = temp+1
                if profit_ganadora_med > profit_ganadora_init and profit_perdedora_med > profit_perdedora_init:
                    temp = temp+1
                if profit_perdedora_med / profit_ganadora_med > 2:
                    temp = temp+1
                if temp >= 2:
                    sens1.append(1)
                else:
                    sens1.append(0)
    if not (not bool(dict_c)):
        profit_gen_fin = ganadoras.loc[x, 'profit_acm']
        profit_ganadora_fin = ganadoras.loc[x, 'Profit']
        profit_perdedora_fin = selected.loc[0, 'profit_capital']
        sensibilidad = []
        if profit_gen_fin > profit_gen_init:
            sensibilidad.append(1)
        if profit_ganadora_fin > profit_ganadora_init and profit_perdedora_fin > profit_perdedora_init:
            sensibilidad.append(1)
        if profit_perdedora_fin/profit_ganadora_fin > 2:
            sensibilidad.append(1)
        resultados = pd.DataFrame(columns=["ocurrencias", "status_quo", "aversion_perdida",
                                           "sensibilidad_decreciente"], index=[" "])
        resultados["ocurrencias"][" "] = l
        resultados["status_quo"][" "] = status_q.count(1) / len(status_q) * 100
        resultados["aversion_perdida"][" "] = av_perdida.count(1) / len(av_perdida) * 100
        if sum(sensibilidad) >= 2:
            resultados["sensibilidad_decreciente"] = "Sí"
            sens1.append(1)
        else:
            resultados["sensibilidad_decreciente"] = "No"
            sens1.append(0)
        final = {"ocurrencias": {"cantidad": l}, "resultados": resultados}
        final["ocurrencias"].update(dict_c)
    else:
        final = {"ocurrencias": "no hay presencia del Disposition Effect",
                 "resultados": "no hay presencia del Disposition Effect"}
    return final, status_q, sens1, av_perdida

