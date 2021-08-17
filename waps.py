#!/usr/bin/env python3
import os
import re

def get_information():
    '''Receiving and verifying information'''
    name = input("Enter a name for the device: ")

    while True:
        token = input("Enter API token: ")
        verify_token = os.popen(f"curl -s https://api.telegram.org/bot{token}/getUpdates").read()

        if "true" in verify_token:
            print("Token is valid")
            break
        else:
            print("API token is invalid, try again\n")


    while True:
        user = input("Enter your UserID: ")
        verify_user = os.popen(f"curl -s https://api.telegram.org/bot{token}/getChat \
                                 -d 'chat_id={user}'").read()

        if "true" in verify_user:
            print("UserID is valid")
            break
        else:
            print("UserID is invalid, try again\n")

    return name, token, user


def get_access_points():
    '''Detecting and storing access points'''
    raw_scan = os.popen('iw dev wlan0 scan').read()
    mac = re.findall(r' (..:..:..:..:..:..)', raw_scan)     # Extracts 
    ssid = re.findall(r'SSID: (.*)', raw_scan)              # MAC,SSID,Signal
    signal = re.findall(r'signal: (-.+).00 dBm', raw_scan)  # from the command output
    access_points = {}

    count = 0
    for address in mac:
        access_points.update({  # Сreates a nested dictionary with discovered 
                address: {      # access points 
                          'SSID': ssid[count],
                          'SIGNAL': signal[count]
                         }
                })

        count += 1

    print('\nMultiple acess points detected')
    return access_points


def get_allowed_mac():
    '''Obtaining allowed MAC addresses'''
    try:
        with open('./whitelist.txt') as file:
            whitelist = file.read().splitlines()
        if whitelist == '':
            raise NoAllowedAP
    except:
        print('Please, write the allowed MAC address in whitelist.txt\n'+\
              'One MAC address per line')
    else:
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


