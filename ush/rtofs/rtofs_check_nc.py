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
        try:
            result = subprocess.run(
                 ['ncdump', '-h', filepath],
                 check=True,
                 stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL
                 )
            if result.returncode == 0:
                status = 0  # file is not corrupted.
                print (status)
        except subprocess.CalledProcessError:
            status = 1      # file is corrupted. 
            print (status)
        return status

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    filename = sys.argv[1]
    status = rtofs_check_nc(filename)

