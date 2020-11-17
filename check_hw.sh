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
