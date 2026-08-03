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

def rtofs_check_nc(filepath, target=None, file_type='fcst'):
    """
    Checks binary data integrity of a single variable in a NetCDF file.
    Forces ncdump to stream the full variable data block to /dev/null.
    """

    # 1. Exact variable mapping for single-variable checks
    FCST_VAR_MAP = {
        'argo_temp': ['temperature'],
        'argo_psal': ['salinity'],
        'ghrsst': ['sst'],
        'aviso': ['ssh'],
        'smos': ['sss'],
        'smap': ['sss'],
        'ndbc': ['sst'],
        'osisaf': ['ice_coverage', 'ice_temperature','ice_thickness'],
    }

    OBS_VAR_MAP = {
        'argo': ['TEMP', 'PSAL'],
        'ghrsst': ['analysed_sst'],
        'aviso': ['sla'],
        'smap': ['sss'],
        'smos': ['sss'],
        'osisaf': ['ice_conc', 'raw_ice_conc_values'],
    }
    primary_vars = []

    # 3. Resolve required primary target variables
    if target:
        target_lower = target.lower()
        if file_type.lower() == 'fcst':
            if target_lower in FCST_VAR_MAP:
                primary_vars = FCST_VAR_MAP[target_lower]
            else:
                primary_vars = [target]
        elif file_type.lower() == 'obs':
            if target_lower in OBS_VAR_MAP:
                primary_vars = OBS_VAR_MAP[target_lower]
            else:
                primary_vars = [target]

    # 4. Strict Check: ALL primary variables must pass ncdump -v
    for var in primary_vars:
        try:
            subprocess.run(
                ['ncdump', '-v', var, filepath],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            # If ANY primary variable is missing or corrupted -> FAIL
            status = 1
            print(status)
            return status

    # 5. All required variables passed successfully -> PASS
    status = 0
    print(status)
    return status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None       # e.g., 'temp', 'argo', 'salinity'
    file_type = sys.argv[3] if len(sys.argv) > 3 else 'fcst'   # 'fcst' or 'obs'

    status = rtofs_check_nc(filepath, target, file_type)
