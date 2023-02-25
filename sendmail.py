#!/usr/bin/env python3

from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
from dotenv import load_dotenv
import os


def sendmail(mail_to="", mail_cc="", mail_bcc="", mail_data="", subject=""):

    # 環境変数読込
    load_dotenv()
    env_send_mail_user = os.getenv("send_mail_user")
    env_send_mail_password = os.getenv("send_mail_password")
    env_send_mail_server = os.getenv("send_mail_server")
    env_from_email = os.getenv("from_email")

    to_email = mail_to
    cc_email = mail_cc
    bcc_email = mail_bcc
    # to_email = "tsuchiya@tml.jp"
    from_email = env_from_email

    data = mail_data

    # subject = "FPT-Em"
    msg = MIMEText(data)
    msg["Subject"] = subject
    msg["To"] = to_email
    msg["Cc"] = cc_email
    msg["Bcc"] = bcc_email
    msg["From"] = from_email
    msg["Date"] = formatdate(None, True)

    print(msg)
    try:
        server = smtplib.SMTP_SSL(env_send_mail_server, 465)
        # server.set_debuglevel(True)
        # server.starttls()
        server.login(env_send_mail_user, env_send_mail_password)
        server.send_message(msg)
        server.quit()
    except:
        data = ""
        buf = ""
        print("Mail Send ERR!")
        return 0
    else:
        data = ""
        buf = ""
        print("Mail Send OK!")
        return 1


if __name__ == "__main__":

    ret = sendmail(
        mail_to="harumiki.tsuchiya@gmail.com",
        mail_data="Nano Pi Wake Up!!",
        subject="Nano Pi Wake up",
    )
    if ret:
        print("True")
