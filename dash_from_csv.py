#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os

CSV_FILENAME = './dump_data.csv'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
def create_fig(csv_file):
    df = pd.read_csv(csv_file)
    fig = make_subplots(
        rows=2, cols=1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
        shared_xaxes=True, vertical_spacing=0.02)
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df[' Pressure hPa'], name='Pressure hPa', yaxis="y",),
        secondary_y=True, row=1, col=1)
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df[' CO2 ppm'], name='CO2 ppm', yaxis="y1",),
        secondary_y=False, row=1, col=1)
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df[' Humidity %'], name='Humidity %', yaxis="y2",),
        secondary_y=True, row=2, col=1)
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df[' Celsius'], name='Celsius', yaxis="y3",),
        secondary_y=False, row=2, col=1)

    fig.update_layout(
        yaxis=dict(side="left", title="ppm"),
        yaxis2=dict(side="right", title="hPa"),
        yaxis3=dict(side="left", title="C"),
        yaxis4=dict(side="right", title="%"),
    )
    fig.update_layout(
        dragmode="zoom",
        hovermode="x",
        height=600,
    )

    return fig

fig = create_fig(CSV_FILENAME)

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
        responsive='auto',
    ),
])

@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('update-button', 'n_clicks')],
)
def update_csv(n_clicks):
    fig = create_fig(CSV_FILENAME)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host=os.uname()[1], port='5001')