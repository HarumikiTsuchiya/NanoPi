#!/usr/bin/env python3

import nanopi_timer
import sendmail
import os


def run_command():
    print("Just Time")

    sendmail.sendmail(
        mail_to="harumiki.tsuchiya@gmail.com",
        mail_data="Nano Pi Wake Up!!",
        subject="Nano Pi Wake up",
    )


if __name__ == "__main__":
    run_command()
