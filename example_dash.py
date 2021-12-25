#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np

from bme280 import BME280
from ccs811 import CCS811
from datetime import datetime
import os

ccs811 = CCS811()
bme280 = BME280()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# 初回データ取得
p, t, h = bme280.get()
ccs811.compensate(h, t)
voc, co2 = ccs811.get()
df = pd.DataFrame(
    [[co2, t, h, p]],
    columns=['CO2 ppm', 'Celsius', 'Humidity %', 'Pressure hPa'],
    index=[datetime.now()],
)
fig = px.line(df)

app.layout = html.Div(children=[
    html.H1(
        children='I2C Sensor on Dash',
        style={
            'textAlign': 'center',
        }
    ),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='graph',
        figure=fig,
        responsive='auto',
    ),

    dcc.Interval(
        id="interval-component",
        interval=1*1000,
        n_intervals=1
    ),
])

@app.callback(dash.dependencies.Output("graph", "figure"),
              [dash.dependencies.Input("interval-component", "n_intervals")])
def update(n_intervals):
    global df
    try:
        p, t, h = bme280.get()
        voc, co2 = ccs811.get()
        df.loc[datetime.now()] = [co2, t, h, p] # Add row
    except OSError:
        # No update
        pass

    fig = px.line(df)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host=os.uname()[1], port='5001')