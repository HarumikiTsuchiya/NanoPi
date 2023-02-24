import nanopi_timer
import os

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
