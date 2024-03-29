#!/usr/bin/env python3

import dash
from dash import dcc
from dash import html
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from PIL import Image

import os

try:
    from openweathermap.weather_data import weather_data
except ImportError:
    openweathermap_available = False
else:
    openweathermap_available = True

from japan_meteological_agency import jma_data

CSV_FILENAME = "./dump_data.csv"
TIMEZONE = "Asia/Tokyo"
CITY = "Tokyo.JP"
CELSIUS_OFFSET = 2  # generated heat by the board
DISPLAY_DAYS = 31

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
hour_width_in_msec = 1000 * 3600


def thin_out_data(df, days=7, rows=2000):
    """Get smaller Dataframe
    Display is slow when data is big.

    param:
        df (pandas.DataFrame): include time data
        days (int): wanted data width
        rows (int): wanted data rows
    return: (pandas.DataFrame)
    """
    if days != 0:
        df = df[(df.index > df.index[-1] - timedelta(days=days))]
    if rows != 0:
        df = df[:: len(df) // rows]

    return df


def set_timezoned_time_to_index(df, label="Date", tz_from="UTC", tz_to=TIMEZONE):
    """Set timezone and move index
    Need to set index because display cann't better.

    param:
        df (pandas.DataFrame): include time data
        label (str): text label of time date
        tz_from (str): timezone strings before changing
        tz_to (str): timezone strings after changing
    return: (pandas.DataFrame)
    """
    df = df.set_index(label)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(tz_from)
    df.index = df.index.tz_convert(tz_to)

    return df


def add_image_to_xaxis_datetime(fig, image, text, x, y, width=hour_width_in_msec * 3, opacity=1.0, layer="above"):
    """Add forecast icons

    The icons are place along the x axis.
    The x axis of datetime is msec-based.
    """
    # print(f"x={x}, y={y}, width={width}")
    fig.add_layout_image(
        dict(
            source=image,
            xref="x",  # yref="y",
            x=x,  # Image position x is datetime
            y=y,
            # Sizes are selected smaller one if hold aspect ratio
            sizex=width,  # sizex is must be integer or float format
            # the format is msec based
            sizey=1000,
            opacity=opacity,
            # sizing="stretch", # Comment out if want to hold aspect ratio
            layer=layer,  # above or below
        )
    )
    fig.add_annotation(
        text=text,
        xref="x",
        yref="paper",
        x=x + timedelta(hours=1.5),
        y=y - 0.16,
        showarrow=False,
    )
    return fig


def add_forecast_fig(fig, latest=datetime.now(timezone.utc)):
    """Add the forecast weather data to received fig

    The forecast data from openweathermap has 5 days.
    But heavy to display all data. So display only 2 days.
    """
    weather = weather_data(city=CITY)
    df = weather.get_forecast_dataframe(latest)
    df = set_timezoned_time_to_index(df, "dt_txt")

    # truncate data to 2 days
    df = df[(df.index < df.index[0] + timedelta(days=2))]

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["main.pressure"],
            name="forecast hPa",
            yaxis="y1",
            line=dict(color=px.colors.qualitative.Plotly[1 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["main.humidity"],
            name="forecast %",
            yaxis="y3",
            line=dict(color=px.colors.qualitative.Plotly[3 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["main.temp"],
            name="forecast C",
            yaxis="y4",
            line=dict(color=px.colors.qualitative.Plotly[4 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )

    # Add forecast weather icons
    for i, weather in enumerate(df["weather"]):
        fig = add_image_to_xaxis_datetime(
            fig,
            Image.open(f"./icons/{weather[0]['icon']}@2x.png"),
            weather[0]["main"],
            df.index[i],
            0.75,
        )
    return fig


def add_historical_fig(fig):
    """Add historical weather data to received fig

    The data get from japan meteorological associate (JMA).
    JMA has only data in japan.
    """
    df = jma_data.get_historical_dataframe()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["normalPressure"],
            name="historical hPa",
            yaxis="y1",
            line=dict(color=px.colors.qualitative.Plotly[1 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["humidity"],
            name="historical %",
            yaxis="y3",
            line=dict(color=px.colors.qualitative.Plotly[3 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["temp"],
            name="historical C",
            yaxis="y4",
            line=dict(color=px.colors.qualitative.Plotly[4 - 1], dash="dash"),
            mode="lines",
            showlegend=False,
        )
    )

    return fig


def add_sensor_csv_fig(fig, csv_file):
    df = pd.read_csv(csv_file)
    df = set_timezoned_time_to_index(df)
    df = thin_out_data(df, days=DISPLAY_DAYS, rows=0)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[" Pressure hPa"],
            name="Pressure hPa",
            yaxis="y1",
            line=dict(color=px.colors.qualitative.Plotly[1 - 1]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[" CO2 ppm"],
            name="CO2 ppm",
            yaxis="y2",
            line=dict(color=px.colors.qualitative.Plotly[2 - 1]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[" Humidity %"],
            name="Humidity %",
            yaxis="y3",
            line=dict(color=px.colors.qualitative.Plotly[3 - 1]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[" Celsius"] - CELSIUS_OFFSET,
            name="Celsius",
            yaxis="y4",
            line=dict(color=px.colors.qualitative.Plotly[4 - 1]),
        )
    )

    return df


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
def create_fig(csv_file):
    fig = go.Figure()
    df = None

    if os.path.exists(csv_file):
        df = add_sensor_csv_fig(fig, csv_file)
        latest = pd.to_datetime(df.index[-1], utc=True)
    else:
        print(f"Warning! {csv_file} is not found.")
        latest = datetime.now(timezone.utc)

    if openweathermap_available:
        fig = add_forecast_fig(fig)
        offset = timedelta(days=1)
    else:
        offset = timedelta(days=0)

    if TIMEZONE == "Asia/Tokyo":
        fig = add_historical_fig(fig)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="left",
            x=0,
            y=1.06,
        ),
        xaxis=dict(
            # range=[df.index[-1] - timedelta(days=1), df.index[-1] + offset],
            rangeslider=dict(
                autorange=True,
            ),
            type="date",
            side="top",
            rangeselector=dict(
                yanchor="bottom",
                xanchor="right",
                x=1,
                y=1.06,
                buttons=list(
                    [
                        dict(count=1, label="1日", step="day", stepmode="backward"),
                        dict(count=2, label="2日", step="day", stepmode="backward"),
                        dict(count=3, label="3日", step="day", stepmode="backward"),
                        dict(count=7, label="週", step="day", stepmode="backward"),
                        dict(count=1, label="月", step="month", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
            ),
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
    # "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    fig.update_layout(template="plotly_white")
    return fig


fig = create_fig(CSV_FILENAME)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    children=[
        html.Div(
            "Display I2C Sensors value on Dash.",
        ),
        html.Button(
            "Update data",
            id="update-button",
            n_clicks=0,
        ),
        dcc.Graph(
            id="graph",
            figure=fig,
            responsive="auto",
        ),
    ],
    style={
        "textAlign": "center",
    },
)


@app.callback(
    dash.dependencies.Output("graph", "figure"),
    [dash.dependencies.Input("update-button", "n_clicks")],
)
def update_csv(n_clicks):
    global fig
    fig = create_fig(CSV_FILENAME)
    return fig


if __name__ == "__main__":
    if os.name == "nt":
        import socket

        hostname = socket.gethostname()
    else:
        hostname = os.uname()[1]

    app.run_server(debug=True, host=hostname, port="5001")
