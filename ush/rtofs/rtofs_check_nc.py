#!/usr/bin/env python3
###############################################################################
#
# Name:          rtofs_check_nc.py
# Developed:     APR. 18, 2025 by Samira Ardani
# Title:         Checking the netcdf observational inputs
#                
# Abstract:      This script adds a file check before files to be used in METplus and discards the corrupted netcdf files.
#                
#
###############################################################################
import sys
import subprocess

def rtofs_check_nc(filepath):
    # Variables to check
    test_vars = ['temperature', 'salinity']
    
    for var in test_vars:
        try:
            # -v forces ncdump to attempt reading actual binary data from the variable
            result = subprocess.run(
                ['ncdump', '-v', var, filepath],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # If ncdump succeeds, the data block is healthy
            status = 0
            print(status)
            return status
            
        except subprocess.CalledProcessError:
            # If the variable isn't in this file or the data is corrupt, try the next one
            continue

    # If neither variable could be read cleanly, mark as corrupted
    status = 1
    print(status)
    return status

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    filename = sys.argv[1]
    status = rtofs_check_nc(filename)
