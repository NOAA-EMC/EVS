#!/usr/bin/env python3
###############################################################################
# Name of Script: 
# Contact(s):     Ho-Chun Huang (ho-chun.huang@noaa.gov)
# Purpose of Script: Read daily AIRNOW PM25/OZONE file and remove bad records
#                    with inconsistent columns number as header
#
# History Log:
#              
#   04/04/2025   Ho-Chun Huang  Use default number of column to handle AirNOW 
#                               daily file even it is a radom text file
#
###############################################################################

import os
import sys

print(f'Python Script: {sys.argv[0]}')
# input and output file specified on the command line

if len(sys.argv) < 2:
    script_name = os.path.basename(sys.argv[0])
    print(f"FATAL ERROR: {script_name} -> Must specify input and output files.")
    sys.exit(1)

# Read the input file as the first argument
input_file = os.path.expandvars(sys.argv[1])
print(f'Input Original AirNOW File:  {input_file}')

# Read the Output file as the second argument
output_file = os.path.expandvars(sys.argv[2])
print(f'Output screened AirNOW File: {output_file}')

if not os.path.exists(input_file):
    print(f"DEBUG :: Can not find input AirNOW file - {input_file}")
    print(f"DEBUG :: Check the existence of input file before calling {sys.argv[0]}")
    sys.exit()

rfile=open(input_file, 'r')
wfile=open(output_file,'w')

evs_component=os.environ['COMPONENT']
evs_step=os.environ['STEP']
evs_run=os.environ['RUN']
#
## Check for number of columns using the default 'DAILY_NCOL' defined in ~/job
#
num_ref_col=int(os.environ['DAILY_NCOL'])
rcount=0
wcount=0
bad_rec=0
for line in rfile:
    rcount += 1
    line=line.rstrip("\n")
    var=[]
    var=line.split("|")
    num_var=len(var)
    if num_var == num_ref_col:
        wfile.write(line+"\n")
        wcount += 1
    else:
        bad_rec += 1
if wcount == 0:
    print(f"WARNING: {input_file} is corrupt (wrong number of columns). {evs_component} {evs_step} step will skip the corrupted validation file.")
else:
    if bad_rec > 0:
        print(f"WARNING: {input_file} is corrupt, {bad_rec} line(s) with having wrong number of columns. Removing the corrupted line(s) from file and continuing")
wfile.close()
