#!/usr/bin/env python3
###############################################################################
# Name of Script: 
# Contact(s):     Ho-Chun Huang (ho-chun.huang@noaa.gov)
# Purpose of Script: Read AERONET AOD file and remove bad records with
#                    inconsistent columns number as header
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
print(f'Input Original Aeronet File:  {input_file}')

# Read the Output file as the second argument
output_file = os.path.expandvars(sys.argv[2])
print(f'Output screened Aeronet File: {output_file}')

if not os.path.exists(input_file):
    print(f"DEBUG :: Can not find input Aeronet file - {input_file}")
    print(f"DEBUG :: Check the existence of input file before calling {sys.argv[0]}")
    sys.exit()

rfile=open(input_file, 'r')
wfile=open(output_file,'w')

count=0
flag_data=False
for line in rfile:
    if not flag_data:
        if line[1:6] != "AQSID":
            wfile.write(line)
        else:
            wfile.write(line)
            line=line.rstrip("\n")
            hdr=line.split('","')
            num_hdr=len(hdr)
            print(f"header len {num_hdr}")
            flag_data=True
        count += 1
    else:
        count += 1
        line=line.rstrip("\n")
        var=[]
        var=line.split('","')
        num_var=len(var)
        if num_var == num_hdr:
            wfile.write(line+"\n")
        else:
            print(f"DEBUG :: Line {count} has different columns number {num_var} vs standard {num_hdr}")
wfile.close()
