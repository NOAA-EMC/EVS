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
##############################################################################
import sys
import subprocess

def rtofs_check_nc(filepath):
    # Specific variables to check first, followed by universal fallback dimensions
    test_vars = [
        'temperature', 'salinity', 'sss', 'sst', 
        'ice_coverage', 'ice_temperature', 'ice_thickness', 'ssh','sla','analysed_sst','TEMP','PSAL','ice_conc','raw_ice_conc_values'
    ]

    for var in test_vars:
        try:
            # Attempt to read data for the target variable
            subprocess.run(
                ['ncdump', '-v', var, filepath],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # If ncdump succeeds, the data block is healthy
            status = 0
            return status

        except subprocess.CalledProcessError:
            # Variable not present in this file OR corrupted; check next
            continue

    # If NONE of the variables or fallback coordinates could be read, mark as corrupt
    status = 1
    return status

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    filename = sys.argv[1]
    status = rtofs_check_nc(filename)

