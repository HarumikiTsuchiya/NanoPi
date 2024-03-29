#!/usr/bin/env python3

import nanopi_timer
import sendmail
import os
import recv_DM
import datetime
import requests
import send_command
from dotenv import load_dotenv


def run_command():
    print("Just Time")
    # 環境変数読込
    load_dotenv()
    env_host_url = os.getenv("host_url")
    env_local_folder = os.getenv("local_folder")

    log_text = ""

    nanopi = nanopi_timer.Nanopi_control()
    nanopi.led_output("Y", 1)

    print("DM get")
    data, log_text = recv_DM.recv_dm()

    ret = send_command.download_command_list()
    print(ret)
    if ret == "OK":
        ret, logtext = send_command.send_command_list()
        print(ret)
        print(logtext)
        log_text += "Send Command List\n"
        log_text += logtext

    print("Alarm Table Download")

    url = "https://" + env_host_url + "/Alarm_Time.json"
    filename = env_local_folder + "/Alarm_Time.json"

    urlData = requests.get(url)
    print("URL:" + url)
    print("Respons:" + str(urlData.status_code))
    if urlData.status_code == 200:
        print(urlData.content)

        with open(filename, mode="wb") as f:
            f.write(urlData.content)

    print("ADC DC Volt")
    adc = nanopi_timer.MCP3425()
    adc.init()
    dc_volt = adc.read_data()
    print("DC Volt : {} V".format(dc_volt))

    nanopi_alarm = nanopi_timer.alarm_set()

    now = datetime.datetime.now()
    print(now)

    alarm_hour, alarm_minute = nanopi_alarm.next_alarm_time(now.hour, now.minute)

    ret = sendmail.sendmail(
        mail_to="harumiki.tsuchiya@gmail.com",
        mail_data="Nano Pi Wake Up!!\nDC Volt : {} V\nData recv: ".format(dc_volt)
        + data
        + "\n------\n"
        + log_text
        + "\n------\nAlarm Table Recv:{}\nNext WakeUp Time : {}:{} \n".format(
            urlData.status_code, alarm_hour, alarm_minute
        ),
        subject="Nano Pi Wake up",
    )
    if ret == True:
        nanopi.led_output("Y", 0)
        nanopi.led_output("G", 1)
    else:
        nanopi.led_output("Y", 0)
        nanopi.led_output("R", 1)

    rtc = nanopi_timer.RX8900A()
    rtc.init()
    ret = rtc.write_ntp_time()
    if ret == "NG":
        ret = rtc.write_rtc_time()
    ret = rtc.read_time()

    # nanopi_alarm=nanopi_timer.alarm_set()

    now = datetime.datetime.now()
    print(now)

    alarm_hour, alarm_minute = nanopi_alarm.next_alarm_time(now.hour, now.minute)
    nanopi_alarm.alarm_set(alarm_hour, alarm_minute)
    nanopi_alarm.alarm_start()

    nanopi.shutdown()


if __name__ == "__main__":
    run_command()
