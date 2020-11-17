# Raspberry PI 4でCCS811/BME280を動かす

I2Cで接続したCCS811とBME280を動かして、センサの値を読めるようにする。

* CCS811: VOC(揮発性有機化合物)を検出するガスセンサで、等価CO2濃度(eCO2)を計算できる。
* BME280: 温度、湿度、気圧を測定できるセンサ

## I2Cでの接続確認

`i2c-tools`をインストールして、接続されているか確認する。  
デフォルトで0x5BにCCS811、0x77にBME280が見えればOK。今回は特に問題なし。

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

こんな感じのスクリプトでIDを確認できる。

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

## Pythonで値を読んでみる

I2Cデバイス(`/dev/i2c-1`とか)は、i2cグループに属していれば権限がいらないので、自分をi2cグループに追加しておく。(毎回sudoするのが面倒なので)

```sh
sudo usermod -aG i2c $USER
```

また、`smbus2`が必要なので、事前にpipでインストールしておく。

```sh
pip install smbus2
```

単純に値を読むだけであれば、動作確認のときのようにbashなどのスクリプトで済ますことができるが、BME280はキャリブレーション値の反映とかで少し煩雑だったので、[Switch Scienceさんのコード(MIT License)](https://github.com/SWITCHSCIENCE/samplecodes/blob/master/BME280/Python27/bme280_sample.py)を参考にした。


