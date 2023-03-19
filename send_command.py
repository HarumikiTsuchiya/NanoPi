import serial
import datetime
from ftplib import FTP
from dotenv import load_dotenv
import os


def download_command_list():
    # 環境変数読込
    load_dotenv()
    env_ftp_server = os.getenv("ftp_server")
    env_ftp_user = os.getenv("ftp_user")
    env_ftp_passwd = os.getenv("ftp_passwd")
    env_ftp_folder = os.getenv("ftp_folder")

    print("Download Command List")

    try:
        ftp = FTP(env_ftp_server, env_ftp_user, env_ftp_passwd, timeout=5)
        # ftp.encoding = "utf-8"

        filename = "command_list.txt"

        with open(filename, "wb") as f:
            ftp.retrbinary("RETR " + env_ftp_folder + "/" + filename, f.write)

        ftp.rename(
            env_ftp_folder + "/" + filename, env_ftp_folder + "/" + filename + "_old"
        )

        return "OK"

    except:
        print("ftp error")
        return "NG"


def upload_command_list():
    print("Upload Command List")


def clr_dm_num_file():
    print("Delete Dm_num file")
    filename = "DM_num.txt"
    with open(filename, mode="w") as f:
        pass


def send_command_list():
    filename = "command_list.txt"
    with open(filename, mode="r", encoding="utf-8") as f:
        file_list = f.read()
        command_list = file_list.split("\n")
        command_list = list(filter(None, command_list))
        print(command_list)

    log_text = ""
    ret = "OK"

    for command in command_list:
        if command[0] != "#":
            now = datetime.datetime.now()
            now_str = now.strftime("%y/%m/%d %H:%M:%S")
            # print(command)
            log_text += "[" + now_str + "]\n"
            log_text += command + "\n"
            if "{Datetime}" in command:
                command = command.replace("{Datetime}", now_str)
                log_text += command + "\n"
            if "{CLR_DM_num}" in command:
                clr_dm_num_file()
                continue
            ret, data = send_command(command)
            # ret="OK"
            log_text += data
            if ret == "NG":
                break

    return ret, log_text


def send_command(command):
    ser = serial.Serial("COM15", 9600, timeout=5)
    ser.close()
    ser.open()

    buf = ""
    data = ""
    command = command + "\r\n"
    ser.write(command.encode("utf-8"))

    while 1:

        # print(frm)
        buf = ser.readline()
        try:
            buf.decode()
        #            print(buf)
        except:
            # TC-35Nのバッファエラー対策(スリープ時に制御文字が入る))
            data = data + buf[1:].decode()
        else:
            data = data + buf.decode()

        if "END" in data:
            print(data)
            ser.reset_input_buffer()
            rcv_OK = True
            return "OK", data
        if "ERR" in data:
            print(data)
            ser.reset_input_buffer()
            rcv_OK = True
            return "NG", data


if __name__ == "__main__":
    ret = download_command_list()
    print(ret)
    if ret == "OK":
        ret, logtext = send_command_list()
        print(ret)
        print(logtext)

        # send_command("RT23/1/1 1:2:3")
