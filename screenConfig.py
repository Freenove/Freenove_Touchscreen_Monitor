#!/usr/bin/env python3
"""
Description : Auto modify config.txt file to fit the touch screen.
auther      : www.freenove.com
modification: 2022/09/23
"""

import shutil
import sys
import os
import time
import re
import datetime

filePath = r"/boot/"
fileConfigName = filePath + r"config.txt"
newFileName = filePath + "config-" +     \
    time.strftime("%Y-%m-%d-%H%M%S", time.localtime()) + ".txt"

keywords = ["hdmi_force_edid_audio", "max_usb_current", "hdmi_force_hotplug",
            "config_hdmi_boost", "hdmi_group", "hdmi_mode", "hdmi_drive", "display_rotate", "hdmi_cvt"]

content = """
[all]
hdmi_force_edid_audio=1
max_usb_current=1
[HDMI:0]
hdmi_group=2
hdmi_mode=87
hdmi_drive=2
hdmi_cvt 1024 600 60 6 0 0 0
[HDMI:1]
hdmi_group=2
hdmi_mode=87
hdmi_drive=2
hdmi_cvt 1024 600 60 6 0 0 0
"""
key_Dtoverlay = "deoverlay"
value_Dtoverlay1 = """
[all]
dtoverlay=vc4-kms-v3d
"""
value_Dtoverlay2 = """
[all]
dtoverlay=vc4-fkms-v3d
"""

def parseDate(dateString):
    date_re_str = '\d{4}[-/]*\d{2}[-/]*\d{2}'
    date_re = re.compile(date_re_str)
    return date_re.findall(dateString)


def parseTime(timeString):
    time_re_str = '\d{2}[:]\d{2}'
    time_re = re.compile(time_re_str)
    return time_re.findall(timeString)


def parseDateAndTime(dtString):
    date_re_str = '\d{4}[-/]*\d{2}[-/]*\d{2}'
    time_re_str = '\d{2}[:]\d{2}'
    dt_re = re.compile('%s %s' % (date_re_str, time_re_str))
    return dt_re.findall(dtString)


def main():
    try:
        shutil.copyfile(fileConfigName, newFileName)
        print("config.txt has backed up: " + newFileName)
    except IOError as e:
        print("Unable to copy file. %s" % e)
        exit(1)
    except:
        print("Unexpected error:", sys.exc_info())
        exit(1)
    resultRpiIssue = os.popen('cat /etc/rpi-issue')
    contentRpiIssue = resultRpiIssue.read()
    # print(res)
    rpiOsReleaseDate = parseDate(contentRpiIssue)
    print("\nOS release date: " + rpiOsReleaseDate[0] + "\n")

    # afetr 2021-10-30, should use dtoverlay=vc4-fkms-v3d
    date1 = datetime.datetime.strptime("2021-10-29", "%Y-%m-%d")
    date2 = datetime.datetime.strptime(rpiOsReleaseDate[0], "%Y-%m-%d")
    with open(fileConfigName, "r", encoding="UTF-8") as file:
        data = file.read()
        for k in keywords:
            print("check item : " + k)
            data = data.replace(k, "##### "+k)    
        data = data + content
        print("check item : " + key_Dtoverlay)
        # print(date1.__sub__(date2).days)
        if date1.__sub__(date2).days < 0:   # date1 - date2
            # after 2021-10-30
            # print("k1")
            data = data.replace(value_Dtoverlay1, "##### " + value_Dtoverlay1)
            data = data + value_Dtoverlay2
        else:
            data = data.replace(value_Dtoverlay2, "##### " + value_Dtoverlay2)
            data = data + value_Dtoverlay1
            # print("k2")
        
        # print(data)
    try:
        with open(fileConfigName, "w", encoding="UTF-8") as file:
            file.write(data)
    except:
        print("!!! No permission !!! , Please add sudo before command !")
        
    print("\nDone! Please reboot the system!")
    isEnableReboot = input("\nDo you want to restart the system now? (Enter yes or no): ")
    print("\n")
    if isEnableReboot == "yes":
        os.popen('sudo reboot')
    else:
        print("Please restart the system manually to make the change take effect!\n")


if __name__ == '__main__':    # Program entrance
    print('\n\nBegin modifying the config.txt file to fit the screen... \n')
    try:
        main()
    except KeyboardInterrupt:   # Press ctrl-c to end the program.
        exit(0)
