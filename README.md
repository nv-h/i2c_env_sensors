# CCS811/BME280 on Raspberry PI 4

This document is to read sensor value of CCS811 and BME280 connected by I2C.

* CCS811: ultra-low power digital gas sensor  
     outputs: The equivalent CO2 (eCO2) and The Total Volatile Organic Compound (TVOC)
* BME280: Combined humidity and pressure sensor  
     outputs: humidity and pressure and temprature

## Check I2C connection

Install `i2c-tools`, and check the connection.  
CCS811 is address 0x5B (default), BME280 is address 0x77 (default).

```sh
$ sudo apt install i2c-tools
$ ls /dev/i2c*
/dev/i2c-1
$ sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- 5b -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77
```

You can check hardware ID by script bellow.  
The connection is OK, if hardware ID is correct.

```bash
#!/bin/bash

CCS811="0x5b"
BME280="0x77"
I2C_BUS="1"

# CCS811
# https://cdn.sparkfun.com/assets/learn_tutorials/1/4/3/CCS811_Datasheet-DS000459.pdf

ccs811_hw_id=$(i2cget -y ${I2C_BUS} ${CCS811} 0x20)
ccs811_hw_version=$(i2cget -y ${I2C_BUS} ${CCS811} 0x21)
# ccs811_fw_boot_version=$(i2cget -y ${I2C_BUS} ${CCS811} 0x23 w)
# ccs811_fw_app_version=$(i2cget -y ${I2C_BUS} ${CCS811} 0x24 w)

echo "CCS811 HW_ID: ${ccs811_hw_id} HW Version ${ccs811_hw_version}"
# echo "FW Boot Version ${ccs811_fw_boot_version}"
# echo "FW app  Version ${ccs811_fw_app_version}"

# BME280
# https://cdn.sparkfun.com/assets/learn_tutorials/4/1/9/BST-BME280_DS001-10.pdf

bme280_hw_id=$(i2cget -y ${I2C_BUS} ${BME280} 0xd0)
echo "BME280 HW_ID: ${bme280_hw_id}"
```

## Read the sensor values

I2C devices such as `/dev/i2c-1` do not need permission if you belong in i2c groupe. So add yourself to the i2c groupe. (Because I don't want to sudo every time.)

```sh
sudo usermod -aG i2c $USER
```

And Install `smbus2` package that is required by python program to communicate by i2c.

```sh
pip install smbus2
```

Use this repository's code and read the values.

```python
from bme280 import BME280

bme280 = BME280()
p, t, h = bme280.get()
print(f"{p:7.2f} hPa, {t:6.2f} C, {h:5.2f} %")

from ccs811 import CCS811

ccs811 = CCS811()
ccs811.compensate(h, t) # if needed
voc, co2 = ccs811.get() # May need to exec several times to get correct values
print(f"TVOC:{voc:4d} ppb, eCO2:{co2:4d} ppm")
```
