#!/usr/bin/env python3

import nanopi_timer
import os
import datetime

def get_sw():

    try:

        os.system("gpio mode 7 in")

        while True:
            stream = os.popen("gpio read 7")
            output = stream.read()

            if "0" in output:
                nanopi_alarm=nanopi_timer.alarm_set()

                now=datetime.datetime.now()
                print(now)

                alarm_hour,alarm_minute = nanopi_alarm.next_alarm_time(now.hour,now.minute)

                nanopi_alarm.alarm_set(alarm_hour,alarm_minute)
                nanopi_alarm.alarm_start()

                nanopi = nanopi_timer.Nanopi_control()
                nanopi.shutdown()
                    run_command()


    except KeyboardInterrupt:
        print("interrupted!")


if __name__ == "__main__":

    nanopi = nanopi_timer.Nanopi_control()
    nanopi.check_network()

    get_sw()
