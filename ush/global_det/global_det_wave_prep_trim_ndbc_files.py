import os
import pandas as pd
import datetime
import glob 
import shutil

INITDATE = os.environ['INITDATE']
DATA = os.environ['DATA']
COMINndbc = os.environ['COMINndbc']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']

INITDATE_dt = datetime.datetime.strptime(INITDATE, '%Y%m%d')
INITDATEp1_dt = INITDATE_dt + datetime.timedelta(days=1)

ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                +"PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                +"hPa  degC  degC  degC  nmi  hPa    ft\n")

for COMINndbc_file in glob.glob(os.path.join(COMINndbc,
                                             f"{INITDATEp1_dt:%Y%m%d}",
                                             'validation_data', 'marine',
                                             'buoy', '*.txt')):
    DATAndbc_file = os.path.join(DATA,
                                 f"ndbc_trimmed_{INITDATE_dt:%Y%m%d}_"
                                 +f"{COMINndbc_file.rpartition('/')[2]}")
    COMOUTndbc_file = os.path.join(f"{COMOUT}.{INITDATE_dt:%Y%m%d}",
                                   'ndbc',
                                   f"{COMINndbc_file.rpartition('/')[2]}")
    if not os.path.exists(COMOUTndbc_file):
        print(f"Trimming {COMINndbc_file} for {INITDATE_dt:%Y%m%d}")
        COMINndbc_file_df = pd.read_csv(
            COMINndbc_file, sep=" ", skiprows=2, skipinitialspace=True,
            keep_default_na=False, dtype='str', header=None,
            names=ndbc_header1[1:].split()
        )
        trimmed_COMINndbc_file_df = COMINndbc_file_df[
            (COMINndbc_file_df['YY'] == f"{INITDATE_dt:%Y}") \
             & (COMINndbc_file_df['MM'] == f"{INITDATE_dt:%m}") \
             & (COMINndbc_file_df['DD'] == f"{INITDATE_dt:%d}")
        ]
        DATAndbc_file_data = open(DATAndbc_file, 'w')
        DATAndbc_file_data.write(ndbc_header1)
        DATAndbc_file_data.write(ndbc_header2)
        DATAndbc_file_data.close()
        trimmed_COMINndbc_file_df.to_csv(
            DATAndbc_file, header=None, index=None, sep=' ', mode='a'
        )
        if SENDCOM == 'YES':
            if os.path.getsize(DATAndbc_file) > 0:
                print(f"Copying {DATAndbc_file} to {COMOUTndbc_file}")
                shutil.copy2(DATAndbc_file, COMOUTndbc_file)
            else:
                print("WARNING: {DATAndbc_file} empty, 0 sized")
