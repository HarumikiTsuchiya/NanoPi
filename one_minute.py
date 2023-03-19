#!/usr/bin/env python3

import nanopi_timer
import os

if __name__ == "__main__":

    nanopi = nanopi_timer.Nanopi_control()
    ret=nanopi.check_network()
    print(ret)
    if ret == "NG":
        print("Reset USB")
        command='/home/tsuchiya/NanoPi/reset_usb.sh'
        os.system(command)

