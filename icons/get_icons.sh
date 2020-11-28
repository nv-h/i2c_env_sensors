#!/bin/bash

icon_names="01d 01n 02d 02n 03d 03n 04d 04n 09d 09n 10d 10n 11d 11n 13d 13n 50d 50n"
base_url="http://openweathermap.org/img/wn/"

for icon_name in ${icon_names}; do
    if [ ! -e "./icons/${icon_name}@2x.png" ]; then
        wget "${base_url}${icon_name}@2x.png" -O "./icons/${icon_name}@2x.png"
    fi
done