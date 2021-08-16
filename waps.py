import os
import re

def get_access_points():
    '''Discover access points and collect information in dictionaries'''
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

    print('\nDiscovered some acess points')
    return access_points


def get_allowed_mac():
    '''Getting the allowed MAC addresses'''
    try:
        with open('./whitelist.txt') as file:
            whitelist = file.read().splitlines()
        if whitelist == '':
            raise NoAllowedAP
    except:
        print('Please, write the allowed MAC address of access points '+\
              'in whitelist.txt \nOne MAC address per line')
    else:
        return whitelist


def delete_allowed():
    '''Deleting allowed MAC addresses from discovered APs'''
    access_points = get_access_points()
    whitelist = get_allowed_mac()

    for address in whitelist:
        if address in access_points:
            del access_points[address]

    print('Allowed MAC addresses deleted from discovered APs')
    return access_points

