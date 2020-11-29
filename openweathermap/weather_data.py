#!/bin/env python

import pandas as pd
from datetime import datetime, timezone

try:
    from .api_key import API_KEY
except ImportError:
    from api_key import API_KEY
import urllib.request
import json

import os


CITY = "Tokyo,JP"
FORECAST_URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&units=metric&appid={API_KEY}"
FORECAST_SAVE_PATH = 'forecast.json'


class weather_data():
    def __init__(self, city=CITY, url=FORECAST_URL):
        self.city = city
        self.url = url

    def get_forecast_json_obj(self):
        request = urllib.request.Request(self.url, method='GET')
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    
    def save_forecast_json(self, path=FORECAST_SAVE_PATH):
        json_obj = self.get_forecast_json_obj()
        with open(path, mode='w') as f:
            f.write(json.dumps(json_obj, indent=4))
        
        return json_obj

    def read_forecast_json(self, path=FORECAST_SAVE_PATH):
        if os.path.exists(FORECAST_SAVE_PATH):
            with open(path) as f:
                return json.load(f)
        else:
            return self.save_forecast_json()

    def json_to_dataframe(self, json_obj):
        return pd.json_normalize(json_obj['list'])

    def get_forecast_dataframe(self, latest=datetime.now(timezone.utc)):
        saved_df = self.json_to_dataframe(self.read_forecast_json())
        saved_head =  pd.to_datetime(saved_df['dt_txt'], utc=True)[0]
        if saved_head < latest:
            return self.json_to_dataframe(self.get_forecast_json_obj())
        else:
            return saved_df


if __name__ == '__main__':
    import dash
    import dash_core_components as dcc
    import dash_html_components as html

    import plotly.graph_objects as go
    from datetime import datetime, timedelta

    weather = weather_data()
    df = weather.get_forecast_dataframe()

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

    if os.name == 'nt':
        import socket
        hostname = socket.gethostname()
    else:
        hostname = os.uname()[1]

    app.run_server(debug=True, host=hostname, port='5001')
