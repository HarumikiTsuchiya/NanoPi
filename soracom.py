import json
from datetime import datetime
import msgpack
import socket

def tds2json(tds_text):

    tds_text_split=tds_text.split('\n')

    #print(tds_text_split)

    scan_data={}

    for ch_text in tds_text_split:
        ch_text=ch_text.strip()
        #print(ch_text)
        try:
            scan_time=datetime.strptime(ch_text, "%Y/%m/%d %H:%M:%S")
            scan_data["TDS_TIME"]=int(scan_time.timestamp())
        except ValueError:
            #print("Not DateTime")
            if "END" in ch_text or "ERR" in ch_text:
                break
            else:
                try:
                    ch_data=ch_text.split()
                    ch=int(ch_data[0][1:])
                    data=ch_data[1]
                    print("ch:{} data:{}".format(ch,data))
                    try:
                        float(data)
                        if "." in data:
                            scan_data[ch]=float(data)
                        else:
                            scan_data[ch]=int(data)

                    except ValueError:
                        print("Not Num")

                except ValueError:
                    print("err")
    #print(scan_data)
    return scan_data

def json2msgpack(json_data):
    #print(json_text)
    json_data=json.loads(json_data)
    #print(json_data)
    ret=msgpack.packb(json_data,use_bin_type=True)
    #print(ret)
    return ret

def send_soracom_msgpack(json_data):

    #json_data=json.loads(json_text)

    #print(json_text)
    #print(len(json_text))

    send_msg=msgpack.packb(json_data, use_bin_type=True)

    print(send_msg)
    #print(len(send_msg))

    payload = send_msg
    try:
        serv_address = ('harvest.soracom.io',8514)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        send_len = sock.sendto(payload, serv_address)

        sock.close()
        return "OK"
    except:
        print("Send Error")
        return "NG"


if __name__ == "__main__":

    tds_text="2023/3/3 1:2:3\r\n" 
    tds_text+="D000 +12345\r\n"
    tds_text+="D001 -123.45\r\n"
    tds_text+="D002 +00000\r\n"
    tds_text+="D003 ******\r\n"
    tds_text+="D004 +*****\r\n"
    tds_text+="D005 -*****\r\n"
    tds_text+="END\r\n"

    print(tds_text)
    json_data=tds2json(tds_text)
    json_text=json.dumps(json_data)

    send_soracom_msgpack(json_data)


    #msg_data=json2msgpack(json_text)
    #print(msg_data)
    #print(len(msg_data))
