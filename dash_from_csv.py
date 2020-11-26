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
from datetime import datetime, timedelta

import os

CSV_FILENAME = './dump_data.csv'
TIMEZONE = 'Asia/Tokyo'
CELSIUS_OFFSET = 2 # generated heat by the board

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
def create_fig(csv_file):
    df = pd.read_csv(csv_file)
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(TIMEZONE)

    df = df[(df.index > df.index[-1]-timedelta(days=7))]
    df = df[::len(df)//2000]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.index, y=df[' Pressure hPa'], name='Pressure hPa', yaxis="y1",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df[' CO2 ppm'], name='CO2 ppm', yaxis="y2",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df[' Humidity %'], name='Humidity %', yaxis="y3",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df[' Celsius']-CELSIUS_OFFSET, name='Celsius', yaxis="y4",),
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom", xanchor="left",
            x=0, y=1.06,
        ),
        xaxis=dict(
            range = [df.index[-1]-timedelta(days=2), df.index[-1]],
            rangeslider=dict(
                autorange=True,
            ),
            type = "date",
            side = 'top',
            rangeselector=dict(
                yanchor="bottom", xanchor="right",
                x=1, y=1.06,
                buttons=list([
                    dict(count=1, label="1日", step="day", stepmode="backward"),
                    dict(count=2, label="2日", step="day", stepmode="backward"),
                    dict(count=3, label="3日", step="day", stepmode="backward"),
                    dict(count=6, label="週", step="day", stepmode="backward"),
                    # dict(count=1, label="月", step="month", stepmode="backward"),
                    # dict(step="all")
                ])
            )
        ),
        yaxis1=dict(domain=[0.76, 1.00], side="right", title="hPa"),
        yaxis2=dict(domain=[0.51, 0.75], side="right", title="ppm"),
        yaxis3=dict(domain=[0.26, 0.50], side="right", title="%"),
        yaxis4=dict(domain=[0.00, 0.25], side="right", title="C"),
    )
    fig.update_layout(
        dragmode="zoom",
        hovermode="x",
        height=800,
    )

    return fig

fig = create_fig(CSV_FILENAME)

app.layout = html.Div(children=[
    html.Div(
        children=[
            'I2C Sensor on Dash   \n',
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
