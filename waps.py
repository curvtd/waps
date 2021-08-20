#!/usr/bin/env python3
from time import sleep
import os
import re

def get_information():
    '''Receiving and verifying information'''
    name = input("Enter a name for the device: ")

    while True:
        token = input("Enter API token: ")
        command = f"curl -s https://api.telegram.org/bot{token}/getUpdates"
        verify_token = os.popen(command).read()

        if "true" in verify_token:
            print("Token is valid")
            break
        else:
            print("API token is invalid, try again\n")


    while True:
        user = input("Enter your UserID: ")
        command = f"curl -s https://api.telegram.org/bot{token}/getChat -d chat_id={user}"
        verify_user = os.popen(command).read()

        if "true" in verify_user:
            print("UserID is valid")
            break
        else:
            print("UserID is invalid, try again\n")

    return name, token, user


def get_access_points():
    '''Detecting and storing access points'''
    interface = input("Enter the interface for scanning: ")
    raw_scan = os.popen(f"iw dev {interface} scan").read()
    mac = re.findall(r' (..:..:..:..:..:..)', raw_scan)     # Extracts 
    ssid = re.findall(r'SSID: (.*)', raw_scan)              # MAC,SSID,Signal
    signal = re.findall(r'signal: (-.+).00 dBm', raw_scan)  # from the command output
    access_points = {}

    while True:
        try:
            count = 0
            for address in mac:
                access_points.update({  # Сreates a nested dictionary with discovered 
                        address: {      # access points 
                                  'SSID': ssid[count],
                                  'SIGNAL': signal[count]
                                 }
                        })
                count += 1
        except:
            print("Something went wrong, trying again")
            continue
        else:
            print('\nMultiple access points detected')
            break
    return access_points


def get_allowed_mac():
    '''Obtaining allowed MAC addresses'''
    with open('./whitelist.txt') as file:
        whitelist = file.read().lower().splitlines()

    return whitelist


def delete_allowed():
    '''Removing allowed MAC addresses from detected'''
    whitelist = get_allowed_mac()
    access_points = get_access_points()

    for address in whitelist:
        if address in access_points:
            del access_points[address]

    print('Allowed MAC addresses are removed from detected')
    return access_points


def create_report():
    '''Creating a report and sending it to Telegram'''
    name, token, user = get_information()
    time_amount = int(input("Enter the number of seconds to sleep: "))

    while True:
        access_points = delete_allowed()

        if access_points:
            print("Creating a report")
            message = f"{name} - Detected unknown access points\n(MAC, SIGNAL, SSID)"
            for mac, ap_info in access_points.items():
                message += f"\n{mac}    {ap_info['SIGNAL']}    {ap_info['SSID']}"

            print("Sending the report to Telegram")
            command = f"curl -s https://api.telegram.org/bot{token}/sendMessage -d chat_id={user} -d text='{message}'"
            os.system(command)
        else:
            print('No unknown access points detected')

        sleep(time_amount)


create_report()
