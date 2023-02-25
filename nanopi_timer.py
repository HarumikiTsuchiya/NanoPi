import os
import time
import datetime
from smbus2 import SMBus
import serial
import json
from dotenv import load_dotenv


class Nanopi_control:
    def __init__(self):
        self.led_port = {
            "G": "0",
            "Y": "2",
            "R": "3",
        }
        self.shutdown_port = "1"
        # 環境変数読込
        load_dotenv()
        self.env_ping_target = os.getenv("ping_target")

    def led_clear(self):
        self.led_output("G", 0)
        self.led_output("Y", 0)
        self.led_output("R", 0)

    def led_output(self, color, onoff):
        self.color = color
        self.onoff = onoff
        port = ""
        onoff = ""

        if self.color == "G" or self.color == "GREEN":
            port = self.led_port["G"]
        if self.color == "Y" or self.color == "YELLOW":
            port = self.led_port["Y"]
        if self.color == "R" or self.color == "RED":
            port = self.led_port["R"]

        if self.onoff == "ON" or self.onoff == 1:
            onoff = "1"
        if self.onoff == "OFF" or self.onoff == 0:
            onoff = "0"

        command1 = "gpio mode " + port + " out"
        command2 = "gpio write " + port + " " + onoff

        if port != "" and onoff != "":
            print(command1)
            os.system(command1)
            print(command2)
            os.system(command2)
        else:
            print("Error LED Output!!")

    def check_ping(self):
        command = "ping -c1 -w1 " + self.env_ping_target
        print(command)
        ret = os.system(command)
        print(ret)
        return ret

    def check_network(self):
        ret = self.check_ping()
        if ret == 0:
            self.led_clear()
            self.led_output("G", 1)
        else:
            self.led_clear()
            self.led_output("R", 1)

    def shutdown(self):

        command1 = "gpio mode " + self.shutdown_port + " out"
        command2 = "gpio write " + self.shutdown_port + " 1"
        command3 = "gpio write " + self.shutdown_port + " 0"
        command4 = "shutdown -h now "

        print(command1)
        os.system(command1)
        print(command2)
        os.system(command2)
        time.sleep(1)
        print(command3)
        os.system(command3)
        print(command4)
        os.system(command4)


class serial_control:
    def __init__(self):
        self.port = "/dev/ttyS1"
        self.rate = 9600

        self.ser = serial.Serial(self.port, self.rate, timeout=5)
        self.ser.close()
        self.ser.open()

    def send_command(self, command):
        print(command)
        buf = ""
        data = ""

        self.ser.write(command + "\r\n".encode("utf-8"))

        while 1:

            # print(frm)
            buf = self.ser.readline()
            try:
                buf.decode()
            except:
                # TC-35Nのバッファエラー対策(スリープ時に制御文字が入る))
                data = data + buf[1:].decode()
            else:
                data = data + buf.decode()

            if data.count("END") > 0 or data.count("ERR") > 0:
                print(data)
                self.ser.reset_input_buffer()
                rcv_OK = True
                break

        return data

    def send_ESCOF(self):
        print("Send ESC+OFF")
        senddata = [0x1B, 0x4F, 0x46, 0x0D, 0x0A]
        send_binary = bytes(senddata)

        self.ser.write(send_binary)


class alarm_set:
    def __init__(self):
        self.alarm_file = "./Alarm_Time.json"
        self.rx8900a = RX8900A()

    def next_alaem_time(self, now_hour, now_min):

        f = open(self.alarm_file, "r")
        data = json.load(f)

        print("Check Time {}:{}".format(now_hour, now_min))
        now_time = now_hour * 100 + now_min

        alarm_hour = 0
        alarm_min = 0

        for i in data["Alarm_Time"]:
            if int(i) > now_time:
                # print(i)
                alarm_hour = int(int(i) / 100)
                alarm_min = int(i) % 100
                break
        print("Next Alarm Time {}:{}".format(alarm_hour, alarm_min))

        return alarm_hour, alarm_min

    def alarm_set(self, alarm_set_hour, alarm_set_min):

        self.rx8900a.clr_flag_reg()

        self.rx8900a.read_flag_reg()

        self.rx8900a.write_alarm_time(alarm_set_hour, alarm_set_min)

        ret = self.rx8900a.read_alarm_time()
        print(ret)

    def alarm_start(self):

        self.rx8900a.set_AIE()

        self.rx8900a.read_control_reg()

    def alarm_stop(self):

        self.rx8900a.reset_AIE()

        self.rx8900a.read_control_reg()


class RX8900A:
    def __init__(self):

        busNum = 0
        self.smbus2 = SMBus(busNum)
        self.addr = 0x32

    def hex2dec(self, num):
        # print(num)
        num_1 = num & 0x0F
        num_10 = (num & 0xF0) >> 4
        # print(num_10,num_1)
        return num_10 * 10 + num_1

    def dec2hex(self, num):
        num_1 = num % 10
        num_10 = int(num / 10)
        # print(num_10,num_1)
        return num_10 * 16 + num_1

    def read_time(self):
        data = []
        data = self.smbus2.read_i2c_block_data(self.addr, 0, 7)
        # print(data)
        time_data = []

        for i in data:
            time_data.append(self.hex2dec(i))
            # print(hex2dec(i))

        print(time_data)
        return time_data

    def clr_flag_reg(self):
        self.smbus2.write_byte_data(self.addr, 0x0E, 0)

    def write_time(self, SEC=0, MIN=0, HOUR=0, WEEK=1, DAY=1, MONTH=1, YEAR=0):
        data = [SEC, MIN, HOUR, WEEK, DAY, MONTH, YEAR]
        # print(data)

        self.smbus2.write_i2c_block_data(self.addr, 0, data)

    def read_alarm_time(self):
        ret = []

        # print("Read Alarm Time")

        data = self.smbus2.read_i2c_block_data(self.addr, 0x08, 3)
        # print(data)
        MIN = self.hex2dec(data[0])
        HOUR = self.hex2dec(data[1])
        DAY = data[2]
        ret = [HOUR, MIN]
        print("Read Alarm Time {}:{}".format(HOUR, MIN))
        return ret

    def write_alarm_time(self, HOUR=0, MIN=0):
        HOUR_h = self.dec2hex(HOUR)
        MIN_h = self.dec2hex(MIN)
        # print("Write Alarm Time HEX {}:{}".format(HOUR_h,MIN_h))

        self.reset_AIE()
        print("Write Alarm Time {}:{}".format(HOUR, MIN))
        self.smbus2.write_byte_data(self.addr, 0x08, MIN_h)
        self.smbus2.write_byte_data(self.addr, 0x09, HOUR_h)
        self.smbus2.write_byte_data(self.addr, 0x0A, 0x80)

    def set_AIE(self):
        print("Set Alarm")
        ret = self.read_control_reg()
        write_data = ret | 0b00001000
        # print(bin(write_data))
        self.smbus2.write_byte_data(self.addr, 0x0F, write_data)

    def reset_AIE(self):
        print("Reset Alarm")
        ret = self.read_control_reg()
        write_data = ret & 0b11110111
        # print(bin(write_data))
        self.smbus2.write_byte_data(self.addr, 0x0F, write_data)

    def read_control_reg(self):
        reg = []
        data = self.smbus2.read_byte_data(self.addr, 0x0F)
        print("Control reg")
        # print(bin(data))
        if data & 0b00001000:
            reg.append("AIE")
        if data & 0b00010000:
            reg.append("TIE")
        if data & 0b00100000:
            reg.append("UIE")
        if data & 0b01000000:
            reg.append("CSEL0")
        if data & 0b10000000:
            reg.append("CSEL1")
        print(reg)
        return data

    def read_extension_reg(self):
        reg = []
        data = self.smbus2.read_byte_data(self.addr, 0x0D)
        print("Extension reg")
        # print(bin(data))
        if data & 0b00000001:
            reg.append("TSEL0")
        if data & 0b00000010:
            reg.append("TSEL1")
        if data & 0b00000100:
            reg.append("FSEL0")
        if data & 0b00001000:
            reg.append("FSEL1")
        if data & 0b00010000:
            reg.append("TE")
        if data & 0b00100000:
            reg.append("USEL")
        if data & 0b01000000:
            reg.append("WADA")
        print(reg)
        return data

    def read_flag_reg(self):
        reg = []

        data = self.smbus2.read_byte_data(self.addr, 0x0E)
        print("Flag reg")
        # print(bin(data))
        if data & 0b00000001:
            reg.append("VDET")
        if data & 0b00000010:
            reg.append("VLF")
        if data & 0b00001000:
            reg.append("AF")
        if data & 0b00010000:
            reg.append("TF")
        if data & 0b00100000:
            reg.append("UF")
        print(reg)
        return data

    def init(self):
        flg = self.read_flag_reg()

        if flg & 0x02:
            print("RX8900 Buckup Error!!")
            print("RX8900 Reset!!")
            self.smbus2.write_byte_data(
                self.addr, 0x0D, 0x48
            )  # Extension set Day Alarm ,FOUT 1Hz
            self.clr_flag_reg()
            self.smbus2.write_byte_data(self.addr, 0x0F, 0x01)  # Control RESET
            self.write_rtc_time()
            self.write_alarm_time(0, 0)

    def write_rtc_time(self):
        print("Write RTC Time")
        now = datetime.datetime.now()
        print(now)

        SEC = self.dec2hex(now.second)
        MIN = self.dec2hex(now.minute)
        HOUR = self.dec2hex(now.hour)
        WEEK = 0x01
        DAY = self.dec2hex(now.day)
        MONTH = self.dec2hex(now.month)
        YEAR = self.dec2hex(now.year - 2000)

        # SUN=0x01,MON=0x02,TUE=0x04,WED=0x08,THU=0x10,FRI=0x20,SAT=0x40
        # print(now.weekday())

        if now.weekday() == 0:
            WEEK = 0x02
        if now.weekday() == 1:
            WEEK = 0x04
        if now.weekday() == 2:
            WEEK = 0x08
        if now.weekday() == 3:
            WEEK = 0x10
        if now.weekday() == 4:
            WEEK = 0x20
        if now.weekday() == 5:
            WEEK = 0x40
        if now.weekday() == 6:
            WEEK = 0x01

        self.write_time(SEC, MIN, HOUR, WEEK, DAY, MONTH, YEAR)


if __name__ == "__main__":

    nanopi = Nanopi_control()
    # nanopi.led_output("RED", 1)
    # nanopi.shutdown()
    nanopi.check_ping()

    # rx8900a = RX8900A()
    # rx8900a.read_time()
    # rx8900a.read_alarm_time()
    # rx8900a.read_control_reg
    # alarm = alarm_set()
    # alarm.next_alaem_time(12, 58)
