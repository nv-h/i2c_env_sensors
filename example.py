#!/usr/bin/env python

from time import sleep
from bme280 import BME280
from ccs811 import CCS811

ccs811 = CCS811()
bme280 = BME280()
p, t, h = bme280.get()
ccs811.compensate(h, t)

while(True):
    try:
        p, t, h = bme280.get()
        voc, co2 = ccs811.get()
        print(f"{p:7.2f} hPa, {t:6.2f} C, {h:5.2f} %, TVOC:{voc:4d} ppb, eCO2:{co2:4d} ppm")
        sleep(1)
    except OSError:
        # i2c bus somtimes cannot access
        continue
    except KeyboardInterrupt:
        break
