
import os
import sys
from datetime import datetime, timedelta as td
import requests
import numpy as np

mPING_token = os.environ['mPINGToken']
mPING_url_head = os.environ['URL_HEAD']
VERIF_CASE = os.environ['VERIF_CASE']
OBSNAME = os.environ['OBSNAME']
VDATE = os.environ['VDATE']
VHOUR_GROUP = os.environ['VHOUR_GROUP']

if VHOUR_GROUP == 'LT1200':
    VHOURS = [str(vh).zfill(2) for vh in np.arange(0,12,1)]
elif VHOUR_GROUP == 'GE1200':
    VHOURS = [str(vh).zfill(2) for vh in np.arange(12,24,1)]
else:
    print(f"VHOUR_GROUP, \"{VHOUR_GROUP}\", is not valid.")
    sys.exit(1)

for VHOUR in VHOURS:
    vdate_dt = datetime.strptime(VDATE+VHOUR, '%Y%m%d%H')
    vdate_dt_shift1H = vdate_dt - td(hours=1)

    DATA = os.environ['DATA']
    outdir1 = os.path.join(DATA,VERIF_CASE,'data',vdate_dt.strftime(f'{OBSNAME}.%Y%m%d'))
    outdir2 = os.path.join(DATA,VERIF_CASE,'data',vdate_dt_shift1H.strftime(f'{OBSNAME}.%Y%m%d'))
    outfile1 = vdate_dt.strftime("mPING_%Y%m%d%H.csv")
    outfile2 = vdate_dt_shift1H.strftime("mPING_%Y%m%d%H.csv")

    headers = {
        "Content-Type": "application/json",
        "Vary": "Accept",
        "Allow": "GET, POST, HEAD, OPTIONS",
        "Authorization": f"Token {mPING_token}"
    }

    get_file1 = not os.path.exists(os.path.join(outdir1, outfile1))
    get_file2 = not os.path.exists(os.path.join(outdir2, outfile2))

    if get_file1:
        download_link1 = (
            mPING_url_head
            + "?format=csv&year="
            + vdate_dt.strftime("%Y")
            + "&month="
            + vdate_dt.strftime("%m")
            + "&day="
            + vdate_dt.strftime("%d")
            + "&hour="
            + vdate_dt.strftime("%H")
        )
        r1 = requests.get(download_link1, headers=headers)
        if r1.raise_for_status():
            print("Bad response.  Quitting")
        else:
            with open(os.path.join(outdir1, outfile1), 'w') as f:
                f.write(r1.text)
            print(f"Wrote data to {os.path.join(outdir1, outfile1)}")
    if get_file2:
        download_link2 = (
            mPING_url_head
            + "?format=csv&year="
            + vdate_dt_shift1H.strftime("%Y")
            + "&month="
            + vdate_dt_shift1H.strftime("%m")
            + "&day="
            + vdate_dt_shift1H.strftime("%d")
            + "&hour="
            + vdate_dt_shift1H.strftime("%H")
        )
        r2 = requests.get(download_link2, headers=headers)
        if r2.raise_for_status():
            print("Bad response.  Quitting")
        else:
            with open(os.path.join(outdir2, outfile2), 'w') as f:
                f.write(r2.text)
            print(f"Wrote data to {os.path.join(outdir2, outfile2)}")
