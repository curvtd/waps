#!/usr/bin/env python3
from time import sleep
import argparse
import os
import re

def information_parser():
    global interface
    parser = argparse.ArgumentParser(
            description='Keep an eye out for unauthorized access points',
            usage='waps.py -n NAME -i INTERFACE -s SECONDS -t API -u ID')
    parser._optionals.title = 'Required arguments (except "help")'
    parser.add_argument('-n', '--name',
                        metavar='NAME', required=True,
                        help='Name for the device')
    parser.add_argument('-i', '--int',
                        metavar='INT', type=str, required=True,
                        help='Network interface for scan')
    parser.add_argument('-s', '--sec',
                        metavar='SEC', type=int, required=True,
                        help='Time period between report creation')
    parser.add_argument('-t', '--token',
                        metavar='API', type=str, required=True,
                        help='Telegram Bot API token')
    parser.add_argument('-u', '--user',
                        metavar='ID', type=int, required=True,
                        help='User/Chat ID')
    args = parser.parse_args()

    name = args.name
    seconds = args.sec
    interface = args.int
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

def root_check():
    if not os.geteuid() == 0:
        print('\nThis script must be run as root!')
        exit()


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
            raw_scan = os.popen(f"iw dev {interface} scan").read()
            continue
        else:
            print('\nMultiple access points detected')
            break

    return access_points


def get_allowed_mac():
    '''Pulls MACs from the whitelist.txt'''
    try:
        with open('./whitelist.txt') as file:
            whitelist = file.read().lower().splitlines()
    except:
        print("\nEven if you don't have an authorized access points - create the 'whitelist.txt' and leave it empty")
        exit()

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
    root_check()

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
