
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Herramientas para el análisis del desempeño de la actividad de trading                     -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: ramirezdiana, israelcastilloh, CristinaCruzD                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_equipo6_lab3                                       -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import functions as fn
import visualizations as vs
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
# leer archivo-----------------------------------------------------------paso 1 #
data = fn.f_leer_archivos(str(input("Nombre de archivo en 0.2 Dependencias (Ejemplo: historicos_ejemplo.csv) :")))
# estadistica descriptiva------------------------------------------------paso 2 #

pip_size = fn.f_pip_size('eurusd')  # ejemplo de pip size
tiempo = fn.f_columnas_tiempo(data)  # segundos con cada posición abierta
col_pip = fn.f_columnas_pip(data)  # valores acumulados
dict_estadisticas = fn.f_estadisticas_ba(data)  # diccionario con estadisticas y ranking

# metricas atribucion al desempeño---------------------------------------paso 3 #

profit_acm_d = fn.f_profit_acm_d(data)  # evolucion capital
profit_d = fn.f_evolucion_capital(data)  # evolución diaria
mad = fn.f_estadisticas_mad(data)

# Behavioral finance ----------------------------------------------------paso 4 #
be_de, stat, sens1, av,  = fn.f_be_de(col_pip)

# visualizaciones
pie = vs.pie_ranking(dict_estadisticas["df_2_ranking"].index, dict_estadisticas["df_2_ranking"]["rank"])
graph = vs.graph_draw(data)
bar = vs.bar_chart(stat, av, sens1)


