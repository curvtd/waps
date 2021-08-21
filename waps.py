#!/usr/bin/env python3
from time import sleep
import argparse
import os
import re

def information_parser():
    global interface
    parser = argparse.ArgumentParser(description='Gathers necessary information')
    parser.add_argument('-n', '--name',
                        metavar='NAME', required=True,
                        help='enter a name for the device')
    parser.add_argument('-i', '--interface',
                        metavar='INT', type=str, required=True,
                        help='enter network interface for scan')
    parser.add_argument('-s', '--seconds',
                        metavar='SEC', type=int, required=True,
                        help='enter user ID')
    parser.add_argument('-t', '--token',
                        metavar='API', type=str, required=True,
                        help='enter api token (bot)')
    parser.add_argument('-u', '--user',
                        metavar='ID', type=int, required=True,
                        help='enter user ID')
    args = parser.parse_args()

    name = args.name
    seconds = args.seconds
    interface = args.interface
    interface_state = os.popen(
        f'ifconfig').read()
    token = args.token
    token_state = os.popen(
        f"curl -s https://api.telegram.org/bot{token}/getUpdates").read()
    user = args.user
    user_state = os.popen(
        f"curl -s https://api.telegram.org/bot{token}/getChat -d chat_id={user}").read()

    if interface in interface_state:
        print(f'Interface {interface} is up')
    else:
        print(f'Interface {interface} is down. Exiting...')
        exit()

    if "true" in token_state:
        print('API token is valid')
    else:
        print('API token is invalid. Exiting...')
        exit()

    if 'true' in user_state:
        print('User ID is valid')
    else:
        print('User ID is invalid. Exiting...')
        exit()

    return name, seconds, token, user


def get_access_points():
    '''Detecting and storing access points'''
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
    '''Pulls MACs from the whitelist.txt'''
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
    name, seconds, token, user = information_parser()

    while True:
        access_points = delete_allowed()

        if access_points:
            print("Creating a report")
            message = f"{name} - Detected unknown access points\n(MAC, SIGNAL, SSID)"
            for mac, ap_info in access_points.items():
                message += f"\n{mac}    {ap_info['SIGNAL']}    {ap_info['SSID']}"

            print("Sending the report to Telegram")
            command = f"curl -s https://api.telegram.org/bot{token}/sendMessage -d chat_id={user} -d text='{message}'"
            os.system(f"{command} > /dev/null")
        else:
            print('No unknown access points detected')

        sleep(seconds)


create_report()
