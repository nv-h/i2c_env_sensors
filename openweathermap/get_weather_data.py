#!/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

import os

from api_key import API_KEY
import urllib.request
import json


CSV_FILENAME = './dump_data.csv'
CITY = "Tokyo,JP"
CURRENT_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&units=metric&appid={API_KEY}"
FORECAST_URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&units=metric&appid={API_KEY}"


def get_response_body(url):
    request = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(request) as response:
        response_body = json.loads(response.read().decode("utf-8"))
    
    return response_body

# response_body = get_response_body(CURRENT_URL)
# print(json.dumps(response_body, indent=4))

# wanted_attributes = ["temp", "pressure", "humidity"]
# for attr in wanted_attributes:
#     print(f"{attr}: {response_body['main'][attr]}")


response_body = get_response_body(FORECAST_URL)
# print(json.dumps(response_body, indent=4))

df = pd.json_normalize(response_body['list'])
df = df.set_index('dt_txt')
df.index = pd.to_datetime(df.index)
df.index = df.index.tz_localize('UTC')
df.index = df.index.tz_convert('Asia/Tokyo')

fig = go.Figure()
fig.add_trace(
    go.Scatter(x=df.index, y=df['main.pressure'], name='Pressure hPa', yaxis="y1",),
)
fig.add_trace(
    go.Scatter(x=df.index, y=df['main.humidity'], name='Humidity %', yaxis="y2",),
)
fig.add_trace(
    go.Scatter(x=df.index, y=df['main.temp'], name='Celsius', yaxis="y3",),
)

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom", xanchor="left",
        x=0, y=1.06,
    ),
    xaxis=dict(
        rangeslider=dict(
            autorange=True,
        ),
        type = "date",
        side = 'top',
    ),
    yaxis1=dict(domain=[0.67, 1.00], side="right", title="hPa"),
    yaxis2=dict(domain=[0.34, 0.66], side="right", title="%"),
    yaxis3=dict(domain=[0.00, 0.33], side="right", title="C"),
)
fig.update_layout(
    dragmode="zoom",
    hovermode="x",
    height=800,
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        dcc.Graph(
            id='graph', figure=fig,
            responsive='auto',
        ),
    ], 
)

if __name__ == '__main__':
    app.run_server(debug=True, host=os.uname()[1], port='5001')
