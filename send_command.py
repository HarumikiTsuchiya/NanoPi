import nanopi_timer
import soracom
import json
import time


log_txt=""

with open('command_list.txt', 'r') as file:
    command_list = file.readlines()

nanopi = nanopi_timer.serial_control()

log_txt += "ESC+ON"

ret = nanopi.send_ESCON()


for command in command_list:
    #print(command.strip())

    log_txt += command

    ret = nanopi.send_command(command.strip())

    log_txt += ret

#log_txt += "ESC+OFF"
#ret = nanopi.send_ESCOF()

