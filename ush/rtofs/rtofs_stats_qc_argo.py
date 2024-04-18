#!/usr/bin/env python3
'''
Name: rtofs_prep_rej_argo.py
Contact(s): Samira Ardani(samira.ardani@noaa.gov)
Abstract: This Python code reads the .txt files from Argo float profiles, 
          identifies the call sign and type of rejected observation data with QC Std >4, 
          lists the call signs for further use in METplus configuration file.
'''          

import os
import pandas as pd
import datetime
import glob
import shutil
import numpy as np


# Read in environment variables to use
VDATE = os.environ['VDATE']
PDATE = os.environ['PDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
COMROOT = os.environ ['COMROOT']
SENDCOM = os.environ['SENDCOM']
COMOUTsmall = os.environ['COMOUTsmall']
RUN = os.environ['RUN']


# Set up date/time
VDATE_YMD = datetime.datetime.strptime(VDATE, '%Y%m%d')
PDATE_YMD = datetime.datetime.strptime(PDATE, '%Y%m%d')

rtofs_qc = os.path.join(COMROOT,
                        'rtofs/v2.3/',f"rtofs.{VDATE_YMD:%Y%m%d}",
                        'ncoda/logs/profile_qc',
                        f"prof_argo_rpt.{PDATE_YMD:%Y%m%d}00.txt")

#########################################################################################
# Identify and filter the call sign of profiles with rejected flag from QC ARTOFS outputs:
########################################################################################
num_profile = []
line_with_sign = []
rejected_temp = []
rejected_psal = []
call_signs = []
Rcpt_temp = []
Rcpt_psal = []
DTG_temp = []
DTG_psal = []
lookup = 'QC Std'
with open(rtofs_qc) as myFile:
    myFile = list(myFile)
    for num, line in enumerate(myFile, 0):
        if lookup in line:
            std_num=line.rpartition(' ')[2]
            if std_num > str(4):
                if "Salinity" in line:
                    num_profile.append(num-3)
                    call_sign= myFile[num-3].rpartition('= "')[2].rpartition('"')[0]
                    #print(call_sign)
                    call_signs.append(call_sign)
                    line_with_sign.append(myFile[num-3].strip())
                    rejected_psal.append(myFile[num-3].rpartition('= "')[2].rpartition('"')[0])
                    Rcpt_psal.append(myFile[num-3].rpartition('Rcpt= ')[2].rpartition('  Sign')[0])
                    DTG_psal.append(myFile[num-3].rpartition('DTG= ')[2].rpartition('  Rcpt')[0])
                if "Temperature" in line:
                    num_profile.append(num-2)
                    call_sign= myFile[num-2].rpartition('= "')[2].rpartition('"')[0]
                    #print(call_sign)
                    call_signs.append(call_sign)
                    line_with_sign.append(myFile[num-2].strip())
                    rejected_temp.append(myFile[num-2].rpartition('= "')[2].rpartition('"')[0])
                    Rcpt_temp.append(myFile[num-2].rpartition('Rcpt= ')[2].rpartition('  Sign')[0])
                    DTG_temp.append(myFile[num-2].rpartition('DTG= ')[2].rpartition('  Rcpt')[0])

rejected_temp_file = os.path.join (COMOUTsmall,f"rejected_temp_{VDATE_YMD:%Y%m%d}.txt")
file1 = open(rejected_temp_file,'w')
for temp_ID in rejected_temp:
    file1.write(temp_ID+" ")
file1.close()

rejected_psal_file = os.path.join (COMOUTsmall,f"rejected_psal_{VDATE_YMD:%Y%m%d}.txt")    
file2 = open(rejected_psal_file,'w')
for psal_ID in rejected_psal:
#    file2.write(psal_ID+"\n")
    file2.write(psal_ID+" ")
file2.close()

print(rejected_psal)
print(rejected_temp)
print(Rcpt_psal)
print(DTG_psal)
print(Rcpt_temp)
print(DTG_temp)
###################################################################


