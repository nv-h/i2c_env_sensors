#!/usr/bin/env python

from time import sleep
from datetime import datetime
import os
from bme280 import BME280
from ccs811 import CCS811

CSV_FILENAME = './dump_data.csv'

ccs811 = CCS811()
bme280 = BME280()
p, t, h = bme280.get()
ccs811.compensate(h, t)

if not os.path.exists(CSV_FILENAME):
    # write header
    with open(CSV_FILENAME, 'w') as f:
        f.write('Date, CO2 ppm, Celsius, Humidity %, Pressure hPa\n')

with open(CSV_FILENAME, 'a') as f:
    while(True):
        try:
            p, t, h = bme280.get()
            voc, co2 = ccs811.get()
            ccs811.compensate(h, t)
            if co2 == 0:
                continue
            now = datetime.now()
            print(f"{now.isoformat()}, {p:7.2f} hPa, {t:6.2f} C, {h:5.2f} %, eCO2:{co2:4d} ppm")
            f.write(f"{now}, {co2}, {t}, {h}, {p}\n")
            f.flush()
            sleep(60)
        except OSError:
            # i2c bus somtimes cannot access
            continue
        except KeyboardInterrupt:
            break
