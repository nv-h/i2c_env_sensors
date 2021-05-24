#!/bin/env python

'''
require: pip install lxml

Various Code list
https://www.jma.go.jp/jma/kishou/know/amedas/ame_master.pdf
'''

import pandas as pd
import urllib
import urllib.request
from datetime import date, datetime, timezone, timedelta

import os
import glob

PLACE_CODE = 44132 # Tokyo


def unlist_df_data(df, column):
    """特定列のリストの先頭の値で上書きする
    """
    return df[column].apply(pd.Series)[0]


def get_json_data(json_url):
    '''get 3 hours history data from `www.jma.go.jp`.

    If url is not found, return None.
    '''
    amedas_data_url_base = f"https://www.jma.go.jp/bosai/amedas/data/point/{PLACE_CODE}/"
    try:
        json_data = None
        json_path = f"{os.path.dirname(__file__)}{os.sep}{json_url}"
        if os.path.exists(json_path):
            with open(json_path, 'rb') as i:
                json_data = i.read()
        else:
            with urllib.request.urlopen(f"{amedas_data_url_base}{json_url}") as u:
                json_data = u.read()
                with open(json_path, 'bw') as o:
                    o.write(json_data)

        return pd.read_json(json_data.decode('utf-8'), orient='index')[::6]
    except urllib.error.HTTPError:
        # 未来のデータは存在しないので404が返る
        return None


def get_1day_history(json_urls):
    '''Get 1 day history from `www.jma.go.jp`.

    return pandas dataframe like bellow
    ----
                           prefNumber  observationNumber     pressure normalPressure  ...    minTemp                    gustTime gustDirection       gust
2021-05-23 00:00:00+09:00          44                132  [1001.5, 0]    [1004.3, 0]  ...  [17.5, 0]  {'hour': 18, 'minute': 12}        [8, 0]  [14.5, 0]
2021-05-23 18:00:00+09:00          44                132  [1004.2, 0]    [1007.0, 0]  ...  [15.0, 0]  {'hour': 16, 'minute': 19}        [1, 0]   [9.5, 0]
...                               ...                ...          ...            ...  ...        ...                         ...           ...        ...

    '''
    # 3時間分ごとにjsonデータになっているのでそれぞれ取得してくっつける
    amedas_data_url_base = f"https://www.jma.go.jp/bosai/amedas/data/point/{PLACE_CODE}/"
    dfs = []
    for i, json_url in enumerate(json_urls):
        df_temp = get_json_data(json_url)
        if df_temp is None:
            break
        dfs.append(df_temp)

    df = pd.concat(dfs)

    # indexがおかしくなるので調整する
    df.index = [datetime.strptime(str(v), '%Y%m%d%H%M%S%f') for v in df.index.values.tolist()]

    df.index = df.index.tz_localize('Asia/Tokyo')

    return df


def get_historical_dataframe():
    '''Get data and save data to csv if csv is old.

    return: pandas dataframe
    ''' 
    # 昨日の分と今日の分を取得してくっつける
    # JMAが日本なので強制的に日本時間に修正
    now_jst = datetime.now(timezone.utc) + timedelta(hours=+9)
    yesterday_str = (now_jst + timedelta(days=-1)).strftime("%Y%m%d")
    yesterday_urls = [f"{yesterday_str}_{i:02d}.json" for i in range(0, 24, 3)]
    df_yesterday = get_1day_history(yesterday_urls)

    today_str = now_jst.strftime("%Y%m%d")
    today_urls = [f"{today_str}_{i:02d}.json" for i in range(0, int(now_jst.strftime('%H')), 3)]
    df_today = get_1day_history(today_urls)

    df = pd.concat([df_yesterday, df_today])

    # 2日以上前のものは消去
    old_day_str = (now_jst + timedelta(days=-2)).strftime("%Y%m%d")
    for filename in  glob.glob(f'{os.path.dirname(__file__)}{os.sep}{old_day_str}*'):
        os.remove(filename)

    """有効な列は以下の通りだが、値はリスト形式になっている。
    ['prefNumber', 'observationNumber', 'pressure', 'normalPressure', 'temp',
    'humidity', 'snow', 'snow1h', 'snow6h', 'snow12h', 'snow24h', 'sun10m',
    'sun1h', 'precipitation10m', 'precipitation1h', 'precipitation3h',
    'precipitation24h', 'windDirection', 'wind', 'maxTempTime', 'maxTemp',
    'minTempTime', 'minTemp', 'gustTime', 'gustDirection', 'gust']
    """
    wanted_columns = ['normalPressure', 'temp', 'humidity']

    # リストになっているので、先頭の値だけ抜き出す。
    # 2つ目の値は測定値の確からしさなので、ひとまず無視する。
    for column in wanted_columns:
        df[column] = unlist_df_data(df, column)

    return df.loc[:, wanted_columns]


if __name__ == '__main__':
    import time
    start = time.time()
    df = get_historical_dataframe()
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")

    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.index, y=df['normalPressure'], name='Pressure hPa', yaxis="y1",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['humidity'], name='Humidity %', yaxis="y2",),
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['temp'], name='Celsius', yaxis="y3",),
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
