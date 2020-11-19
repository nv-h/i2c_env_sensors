#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np

import os

CSV_FILENAME = './dump_data.csv'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv(CSV_FILENAME)
fig = px.line(df, x='Date', y=[' CO2 ppm', ' Celsius', ' Humidity %', ' Pressure hPa'])
fig.update_xaxes(
    rangeslider_visible=True,
)

app.layout = html.Div(children=[
    html.H1(
        children='I2C Sensor on Dash',
        style={
            'textAlign': 'center',
        }
    ),
    html.Div(
        children=[
            'Dash: A web application framework for Python.\n',
            html.Button(
                'Update', id='update-button', n_clicks=0,
                style={
                    'textAlign': 'center',
                }
            ),
        ],
        style={
            'textAlign': 'center',
        }
    ),
    dcc.Graph(
        id='graph', figure=fig,
    ),
])

@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('update-button', 'n_clicks')],
)
def update_csv(n_clicks):
    df = pd.read_csv(CSV_FILENAME)
    fig = px.line(df, x='Date', y=[' CO2 ppm', ' Celsius', ' Humidity %', ' Pressure hPa'])
    fig.update_xaxes(
        rangeslider_visible=True,
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host=os.uname()[1], port='5001')