#!/usr/bin/env python3
###############################################################################
# Name of Script: 
# Contact(s):     Ho-Chun Huang (ho-chun.huang@noaa.gov)
# Purpose of Script: Read AERONET AOD file and remove bad records with inconsistent columns

# History Log:
#   9/2024: Script copied from METplus repository
###############################################################################

import os
import sys
## import datetime

print(f'Python Script: {sys.argv[0]}')
# input file specified on the command line

if len(sys.argv) < 2:
    script_name = os.path.basename(sys.argv[0])
    print(f"FATAL ERROR: {script_name} -> Must specify exactly one input file.")
    sys.exit(1)

# Read the input file as the first argument
input_file = os.path.expandvars(sys.argv[1])
print(f'Input File: {input_file}')

if not os.path.exists(input_file):
    print(f"Can not fid input file {input_file}")
    sys.exit(2)

output_file=os.path.join(os.environ['DATA'],"post_aeronet_lev15.csv")
print(output_file)
wfile=open(output_file,'w')
rfile=open(input_file, 'r')
count=0
flag_data=False
for line in rfile:
    if not flag_data:
        if line[0:4] != "Date":
            wfile.write(line)
        else:
            wfile.write(line)
            line=line.rstrip("\n")
            hdr=line.split(",")
            num_hdr=len(hdr)
            flag_data=True
        count += 1
    else:
        count += 1
        line=line.rstrip("\n")
        var=[]
        var=line.split(",")
        num_var=len(var)
        if num_var == num_hdr:
            wfile.write(line+"\n")
wfile.close()
