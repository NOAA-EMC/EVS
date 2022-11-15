from datetime import datetime, timedelta as td
import os
import sys
import requests
import cam_util as cutil

VDATE = os.environ['VDATE']
VHOUR = os.environ['VHOUR']
DAY = os.environ['DAY']
TEMP_DIR = os.environ['TEMP_DIR']
metplus_launcher = os.environ['metplus_launcher']
#SHP_FILE_DIR = some COMOUT directory string

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
        if int(VHOUR) < 12: 
            V2DATE = VDATE
            V1HOUR = OTLK
            if OTLK < '1200':
                V1DATE = VDATE
                IDATE = VDATE
            else:
                V1DATE = VDATEm1
                IDATE = VDATEm1
        elif int(VHOUR) >= 12:
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
        if int(VHOUR) < 12:
            V1DATE = VDATEm1
            V2DATE = VDATE
            V1HOUR = '1200'
            IDATE = VDATEm2
        elif int(VHOUR) >= 12:
            V1DATE = VDATE
            V2DATE = VDATEp1
            V1HOUR = '1200'
            IDATE = VDATEm1
        else:
            sys.exit(1)
    elif int(DAY) == 3:
        if int(VHOUR) < 12:
            V1DATE = VDATEm1
            V2DATE = VDATE
            V1HOUR = '1200'
            IDATE = VDATEm3
        elif int(VHOUR) >= 12:
            V1DATE = VDATE
            V2DATE = VDATEp1
            V1HOUR = '1200'
            IDATE = VDATEm2
        else:
            sys.exit(1)
    V2HOUR = '1200'
    YYYY = IDATE[0:4]
    SHP_FILE = f'day{DAY}otlk_{IDATE}_{OTLK}_cat'
    # if SHP_FILE exists in SHP_FILE_DIR, then:
        N_REC = cutil.run_shell_command([
            'gis_dump_dbf', os.path.join([SHP_FILE_DIR,SHP_FILE+'.dbf']), '|', 
            'grep', 'n_records', '|', 'cut', '-d\'=\'', '-f2', '|', 'tr', '-d',
            '\' \''
        ], capture_output=True)
        print(f"Processing {N_REC} records.")

        if N_REC > 0:
            for REC in np.arange(N_REC-1):
                NAME = cutil.run_shell_command([
                    'gis_dump_dbf', os.path.join([SHP_FILE_DIR,SHP_FILE+'.dbf']), 
                    '|', 'egrep', '-A', '5', f'"^Record {REC}"', '|', 'tail',
                    '-1', '|', 'cut', '-d\'"\'', '-f2'
                ], capture_output=True)
                print(f"Processing Record #{REC}: {NAME}")
                MASK_FNAME = "spc_otlk_d{DAY}_{OTLK}_v{V1DATE}{V1HOUR}-{V2DATE}{V2HOUR}"
                if int(DAY) == 3:
                    MASK_NAME = "DAY{DAY}_{NAME}"
                else:
                    MASK_NAME = "DAY{DAY}_{OTLK}_{NAME}"
                os.environ['SHP_FILE'] = SHP_FILE
                os.environ['REC'] = REC
                os.environ['MASK_FNAME'] = MASK_FNAME
                os.environ['MASK_NAME'] = MASK_NAME

                cutil.run_shell_command([
                    metplus_launcher, '-c', 
                    os.path.join([MET_PLUS_CONF, 'GenVxMask_SPC_OTLK.conf'])
                ])
        else:
            print("No day DAY outlook areas were issued at OTLKZ on IDATE")
            continue
    else:
        print("No day DAY outlook areas were issued at OTLKZ on IDATE")
        continue
