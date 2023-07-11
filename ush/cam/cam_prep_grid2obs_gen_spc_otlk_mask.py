#!/usr/bin/env python3
from datetime import datetime, timedelta as td
import os
import sys
import requests
import cam_util as cutil

VDATE = os.environ['VDATE']
VHOUR_GROUP = os.environ['VHOUR_GROUP']
DAY = os.environ['DAY']
URL_HEAD = os.environ['URL_HEAD']
TEMP_DIR = os.environ['TEMP_DIR']
#metplus_launcher = os.environ['metplus_launcher']

vdate_dt = datetime.strptime(VDATE,'%Y%m%d')
VDATEp1 = (vdate_dt + td(days=1)).strftime('%Y%m%d')
VDATEm1 = (vdate_dt - td(days=1)).strftime('%Y%m%d')
VDATEm2 = (vdate_dt - td(days=2)).strftime('%Y%m%d')
VDATEm3 = (vdate_dt - td(days=3)).strftime('%Y%m%d')

if int(DAY) == 1:
    OTLKs = ['0100', '1200', '1300', '1630', '2000']
elif int(DAY) == 2:
    OTLKs = ['0600', '0700', '1730']
elif int(DAY) == 3:
    OTLKs = ['0730', '0830']
else:
    sys.exit(1)

for OTLK in OTLKs:
    if int(DAY) == 1:
        if VHOUR_GROUP == 'LT1200': 
            V2DATE = VDATE
            V1HOUR = OTLK
            if OTLK < '1200':
                V1DATE = VDATE
                IDATE = VDATE
            else:
                V1DATE = VDATEm1
                IDATE = VDATEm1
        elif VHOUR_GROUP == 'GE1200':
            V1DATE = VDATE
            V1HOUR = OTLK
            IDATE = VDATE
            if OTLK < '1200':
                V2DATE = VDATE
            else:
                V2DATE = VDATEp1
        else:
            sys.exit(1)
    elif int(DAY) == 2:
        if VHOUR_GROUP == 'LT1200':
            V1DATE = VDATEm1
            V2DATE = VDATE
            V1HOUR = '1200'
            IDATE = VDATEm2
        elif VHOUR_GROUP == 'GE1200':
            V1DATE = VDATE
            V2DATE = VDATEp1
            V1HOUR = '1200'
            IDATE = VDATEm1
        else:
            sys.exit(1)
    elif int(DAY) == 3:
        if VHOUR_GROUP == 'LT1200':
            V1DATE = VDATEm1
            V2DATE = VDATE
            V1HOUR = '1200'
            IDATE = VDATEm3
        elif VHOUR_GROUP == 'GE1200':
            V1DATE = VDATE
            V2DATE = VDATEp1
            V1HOUR = '1200'
            IDATE = VDATEm2
        else:
            sys.exit(1)
    V2HOUR = '1200'
    YYYY = IDATE[0:4]
    ZIP_FILE = f'day{DAY}otlk_{IDATE}_{OTLK}-shp.zip'
    URL = f'{URL_HEAD}/{YYYY}/{ZIP_FILE}'
    response = requests.get(URL)
    if response.status_code == 200:
        cutil.run_shell_command(['wget',URL,'-P',TEMP_DIR])
        cutil.run_shell_command(['unzip',os.path.join(TEMP_DIR,ZIP_FILE),'*_cat*','-d',TEMP_DIR])
        cutil.run_shell_command(['rm','-f',os.path.join(TEMP_DIR,ZIP_FILE)])
    else:
        print("No day DAY outlook areas were issued at OTLKZ on IDATE")
        continue
