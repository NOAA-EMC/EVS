#!/usr/bin/env python3
###############################################################################
# Name of Script: 
# Contact(s):     Ho-Chun Huang (ho-chun.huang@noaa.gov)
# Purpose of Script: Read Hourly AIRNOW PM25/OZONE file and remove bad records
#                    with inconsistent columns number as header
#
# History Log:
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

num_ref_hdr=34
rcount=0
wcount=0
flag_data=False
for line in rfile:
    if not flag_data:
        rcount += 1
        if line[1:6] == "AQSID":
            line=line.rstrip("\n")
            hdr=line.split('","')
            num_hdr=len(hdr)
            print(f"header len {num_hdr}")
            if num_hdr == num_ref_hdr:
                wfile.write(line)
                wcount += 1
                flag_data=True
                print(f"DEBUG :: find header row in line {rcount}")
            else:
                print(f"DEBUG :: row {rcount} has inconsistent header column")
    else:
        rcount += 1
        line=line.rstrip("\n")
        var=[]
        var=line.split('","')
        num_var=len(var)
        if num_var == num_hdr:
            wfile.write(line+"\n")
            wcount += 1
        else:
            print(f"DEBUG :: Line {rcount} has different columns number {num_var} vs standard {num_hdr}")
if wcount == 0:
    print(f"CRITICAL - CHECK DATA FILE :: it is possible that {input_file} is not EPA AirNOW hourly observation")
wfile.close()
