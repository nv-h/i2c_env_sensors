#!/bin/env python

'''
require: pip install lxml

Various Code list
https://www.jma.go.jp/jma/kishou/know/amedas/ame_master.pdf
'''

import pandas as pd
from datetime import datetime, timedelta

PLACE_CODE = 44132 # Tokyo
AREA_CODE = 000
GROUPE_CODE = 30
TODAY_URL = f"https://www.jma.go.jp/jp/amedas_h/today-{PLACE_CODE}.html?areaCode={AREA_CODE}&groupCode={GROUPE_CODE}"
YESTERDAY_URL = f"https://www.jma.go.jp/jp/amedas_h/yesterday-{PLACE_CODE}.html?areaCode={AREA_CODE}&groupCode={GROUPE_CODE}"


def get_dataframe(url=TODAY_URL):
    '''
                         時刻    気温  降水量   風向   風速 日照時間  積雪深    湿度      気圧
                          時     ℃   mm 16方位  m/s    h   cm     %     hPa
    2020-11-29 01:00:00   1   8.7  0.0    北  3.5  NaN  0.0  51.0  1019.5
    2020-11-29 02:00:00   2   9.1  0.0  北北西  3.3  NaN  0.0  49.0  1020.0
    2020-11-29 03:00:00   3   9.1  0.0  北北西  3.0  NaN  0.0  50.0  1020.6
    ......
    2020-11-29 21:00:00  21   9.8  0.0  北北東  1.4  NaN  0.0  70.0  1023.1
    2020-11-29 22:00:00  22   NaN  NaN  NaN  NaN  NaN  NaN   NaN     NaN
    2020-11-29 23:00:00  23   NaN  NaN  NaN  NaN  NaN  NaN   NaN     NaN
    2020-11-30 00:00:00  24   NaN  NaN  NaN  NaN  NaN  NaN   NaN     NaN
    '''
    dfs = pd.read_html(url, header=[0, 1]) # header is 2 rows
    df = dfs[4] # main table

    day_start = datetime.now().replace(hour=1, minute=0, second=0, microsecond=0)
    if "yesterday" in url:
        day_start -= timedelta(days=1)

    datetime_index = []
    for i in range(len(df)):
        datetime_index.append(day_start + timedelta(hours=i))

    df.index = datetime_index

    return df


if __name__ == '__main__':
    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    import plotly.graph_objects as go

    import os

    today_df = get_dataframe(TODAY_URL)
    yesterday_df = get_dataframe(YESTERDAY_URL)
    df = pd.concat([yesterday_df, today_df])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.index, y=df['気圧', 'hPa'], name='Pressure hPa', yaxis="y1",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['湿度', '%'], name='Humidity %', yaxis="y2",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['気温', '℃'], name='Celsius', yaxis="y3",),
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
