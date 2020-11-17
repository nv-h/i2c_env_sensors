#!/usr/bin/env python

from smbus2 import SMBus


CCS811_STATUS = 0x00
CCS811_MEAS_MODE = 0x01
CCS811_ALG_RESULT_DATA = 0x02

CCS811_DRIVE_MODE_IDLE = 0x00
CCS811_DRIVE_MODE_1SEC = 0x01
CCS811_DRIVE_MODE_10SEC = 0x02
CCS811_DRIVE_MODE_60SEC = 0x03
CCS811_DRIVE_MODE_250MS = 0x04

CCS811_BOOTLOADER_APP_START = 0xF4


class CCS811:
    def __init__(self, bus_num=1, i2c_address=0x5b):
        self.i2c = SMBus(bus_num)
        self.i2c_address = i2c_address

        self.status = 0
        self.TVOC = 0
        self.eCO2 = 0

        # 0バイト書き込み
        self.i2c.write_i2c_block_data(self.i2c_address, CCS811_BOOTLOADER_APP_START, [])
        # モード設定(割り込み無効、1秒間隔)
        meas_mode = (1 << 3) | CCS811_DRIVE_MODE_1SEC
        self.i2c.write_byte_data(self.i2c_address, CCS811_MEAS_MODE, meas_mode)


    def available(self):
        self.status = self.i2c.read_byte_data(self.i2c_address, CCS811_STATUS)
        if self.status == 0:
            return False
        else:
            return True


    def update(self):
        if self.available():
            buf = self.i2c.read_i2c_block_data(self.i2c_address, CCS811_ALG_RESULT_DATA, 8)
            self.eCO2 = (buf[0] << 8) | (buf[1])
            self.TVOC = (buf[2] << 8) | (buf[3])
        else:
            return False


    def get(self):
        self.update()
        return self.TVOC, self.eCO2


if __name__ == '__main__':
    ccs811 = CCS811()
    voc, co2 = ccs811.get()
    print(f"TVOC = {tvoc} ppm, eCO2 = {co2} ppm")
