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

#
## Check first 3 line for number of column or use the default column 'DAILY_NCOL' defined in ~/job
#
count=0
flag_data=False
for line in rfile:
    if not flag_data:
        if count == 0:
            line1=line
        elif count == 1:
            line2=line
        elif count == 2:
            line3=line
        line=line.rstrip("\n")
        hdr=line.split("|")
        if count == 0:
            num_hdr1=len(hdr)
        elif count == 1:
            num_hdr2=len(hdr)
            if num_hdr1 == num_hdr2:
                num_hdr = num_hdr1
                wfile.write(line1)
                wfile.write(line2)
                flag_data=True
        elif count == 2:
            num_hdr3=len(hdr)
            if num_hdr3 == num_hdr1:
                num_hdr = num_hdr1
                wfile.write(line1)
                wfile.write(line3)
                print(f"DEBUG :: Line 2 has different columns number {num_hdr2} vs standard {num_hdr}")
                flag_data=True
            elif num_hdr3 == num_hdr2:
                num_hdr = num_hdr2
                wfile.write(line2)
                wfile.write(line3)
                print(f"DEBUG :: Line 1 has different columns number {num_hdr1} vs standard {num_hdr}")
                flag_data=True
            else:   ## USE DEFAULT Column number
                print(f"DEBUG :: First 3 lines of {input_file} have different column number")
                try:
                    str_num_hdr=os.environ['DAILY_NCOL']
                    num_hdr=int(str_num_hdr)
                    print(f"DEBUG :: Use default {num_hdr} as reference column number")
                    if num_hdr1 == num_hdr:
                        wfile.write(line1)
                    else:
                        print(f"DEBUG :: Line 1 has different columns number {num_hdr1} vs standard {num_hdr}")
                    if num_hdr2 == num_hdr:
                        wfile.write(line2)
                    else:
                        print(f"DEBUG :: Line 2 has different columns number {num_hdr2} vs standard {num_hdr}")
                    if num_hdr3 == num_hdr:
                        wfile.write(line3)
                    else:
                        print(f"DEBUG :: Line 3 has different columns number {num_hdr3} vs standard {num_hdr}")
                    flag_data=True
                except KeyError:
                    print(f"WARNING ::  no reference DAILY_NCOL daily column number has been defined")
                    sys.exit()
        count += 1
    else:
        count += 1
        line=line.rstrip("\n")
        var=[]
        var=line.split("|")
        num_var=len(var)
        if num_var == num_hdr:
            wfile.write(line+"\n")
        else:
            print(f"DEBUG :: Line {count} has different columns number {num_var} vs standard {num_hdr}")
wfile.close()
