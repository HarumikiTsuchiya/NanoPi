#!/usr/bin/env python3

import nanopi_timer
import soracom
import json
import time
from dotenv import load_dotenv
import os

def recv_dm():
    load_dotenv()
    env_local_folder =  os.getenv('local_folder')
    print("local={}".format(env_local_folder))

    log_text=""

    net_status=""

    for i in range(10):
        nanopi_cont=nanopi_timer.Nanopi_control()
        net_status=nanopi_cont.check_network()
        print('net_status={}'.format(net_status))

        if net_status =="OK" :
            break
        time.sleep(10)

    if net_status != "OK" :
        return "NG"

    nanopi = nanopi_timer.serial_control()

    nanopi.send_ESCON()

    log_text+="LS23\n"
    ret = nanopi.send_command("LS23")
    log_text+=ret

    if "NG" in ret:
        return "NG",log_text
    if "ERR" in ret:
        return "NG",log_text

    log_text+=ret
    ret_split=ret.split("(")
    data_num=int(ret_split[0])

    with open(env_local_folder+'/DM_num.txt', 'r') as file:
        dm_list = file.read()


    for num in range(data_num):
        #print(num)
        if str(num) not in dm_list:
            log_text+="RD0," + str(num) + "\n"

            ret = nanopi.send_command("RD0,"+str(num))
            json_data=soracom.tds2json(ret)
            ret=soracom.send_soracom_msgpack(json_data)
            print(ret)

            log_text+=ret + "\n"
            if ret=="OK":
                with open(env_local_folder+'/DM_num.txt', 'a') as file:
                    file.write("\n" + str(num))

    nanopi.send_ESCOF()
    return "OK",log_text

if __name__ == "__main__":
    ret,log_text=recv_dm()
    print("-------")
    print(ret)
    print(log_text)
