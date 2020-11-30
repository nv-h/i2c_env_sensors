#!/bin/env python

'''
require: pip install lxml

Various Code list
https://www.jma.go.jp/jma/kishou/know/amedas/ame_master.pdf
'''

import pandas as pd
from datetime import datetime, timezone, timedelta

import os

PLACE_CODE = 44132 # Tokyo
AREA_CODE = 000
GROUPE_CODE = 30
TODAY_URL = f"https://www.jma.go.jp/jp/amedas_h/today-{PLACE_CODE}.html?areaCode={AREA_CODE}&groupCode={GROUPE_CODE}"
YESTERDAY_URL = f"https://www.jma.go.jp/jp/amedas_h/yesterday-{PLACE_CODE}.html?areaCode={AREA_CODE}&groupCode={GROUPE_CODE}"
CSV_PATH = 'jma_historical_data.csv'

def get_1day_history(url=TODAY_URL):
    '''Get 1 day history from `www.jma.go.jp`.

    parameter is choice from TODAY_URL or YESTERDAY_URL
    return pandas dataframe like bellow
    ----
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

    day_start = datetime.now(timezone.utc) + timedelta(hours=9-1) # mesurment time is before 1 hour
    day_start = day_start.replace(hour=1, minute=0, second=0, microsecond=0)
    if "yesterday" in url:
        day_start -= timedelta(days=1)

    datetime_index = []
    for i in range(len(df)):
        datetime_index.append(day_start + timedelta(hours=i-9))

    df.index = datetime_index
    df.index = df.index.tz_convert('Asia/Tokyo')

    return df


def get_historical_dataframe(csv_path=CSV_PATH):
    '''Get data and save data to csv if csv is old.

    return: pandas dataframe
    '''
    if os.path.exists(csv_path):
        if not is_old_csv(csv_path):
            return pd.read_csv(csv_path, index_col=0, header=[0, 1])

    today_df = get_1day_history(TODAY_URL)
    yesterday_df = get_1day_history(YESTERDAY_URL)
    df = pd.concat([yesterday_df, today_df])

    df.to_csv(csv_path)

    return df


def is_old_csv(path=CSV_PATH):
    df = pd.read_csv(path, index_col=0, header=[0, 1])
    del df['日照時間', 'h'] # '日照時間' include NaN

    # saved time is JST(+9)
    NaN_index = df.isnull().any(axis=1) # future hours index
    if not NaN_index.any():
        # Select last row when the table is full 
        saved_time_str = df.index[-1]
    else:
        saved_time_str = df[NaN_index].index[0]
    saved_time = pd.to_datetime(saved_time_str).tz_convert('UTC')
    # datetime.now() return system timezone, so force to JST(+9)
    now = datetime.now(timezone.utc)

    return saved_time < now


if __name__ == '__main__':
    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    import plotly.graph_objects as go

    df = get_historical_dataframe()

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
