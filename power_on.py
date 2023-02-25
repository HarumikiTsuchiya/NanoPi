#!/usr/bin/env python3

import nanopi_timer
import os


def get_sw():

    try:

        os.system("gpio mode 7 in")

        while True:
            stream = os.popen("gpio read 7")
            output = stream.read()

            if "0" in output:
                nanopi = nanopi_timer.Nanopi_control()
                nanopi.shutdown()

    except KeyboardInterrupt:
        print("interrupted!")


if __name__ == "__main__":

    nanopi = nanopi_timer.Nanopi_control()
    nanopi.check_network()

    get_sw()
