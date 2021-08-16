import os
import re

def get_access_points():
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

get_access_points()
