#!/usr/bin/env python3

import nanopi_timer
import sendmail
import os


def run_command():
    print("Just Time")

    nanopi = nanopi_timer.Nanopi_control()
    nanopi.led_output("Y", 1)

    ret = sendmail.sendmail(
        mail_to="harumiki.tsuchiya@gmail.com",
        mail_data="Nano Pi Wake Up!!",
        subject="Nano Pi Wake up",
    )
    if ret == True:
        nanopi.led_output("Y", 0)
        nanopi.led_output("G", 1)
    else:
        nanopi.led_output("Y", 0)
        nanopi.led_output("R", 1)


if __name__ == "__main__":
    run_command()
