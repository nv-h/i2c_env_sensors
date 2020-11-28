#!/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
df.plot(x='dt_txt', y=['main.temp', 'main.humidity'])
df.plot(x='dt_txt', y=['main.pressure'])

plt.show()
