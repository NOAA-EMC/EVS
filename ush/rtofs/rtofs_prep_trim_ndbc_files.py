#!/usr/bin/env python3
'''
Name: rtofs_prep_trim_ndbc_files.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This trims the NDBC individual buoy text files
          for only data for a single date
Run By: scripts/prep/rtofs/exevs_prep_rtofs.sh
'''

import os
import datetime
import glob
import shutil

print("BEGIN: " + os.path.basename(__file__))

# Read in environment variables to use
INITDATE = os.environ['INITDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
SENDCOM = os.environ['SENDCOM']
COMOUTprep = os.environ['COMOUTprep']
OBTYPE = os.environ['OBTYPE']
MET_NDBC_STATIONS = os.environ['MET_NDBC_STATIONS']
RUN = os.environ['RUN']

# Set up dates
INITDATE_dt = datetime.datetime.strptime(INITDATE, '%Y%m%d')

# Assign header columns in NDBC individual buoy files
ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                + "PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                + "hPa  degC  degC  degC  nmi  hPa    ft\n")
expected_cols = len(ndbc_header1[1:].split())  # 19 columns


def is_valid_ndbc_file(filepath):
    """Validate that an NDBC text file is non-empty, not an HTML page,
    has valid NDBC headers, and contains at least one valid 19-column data row."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"WARNING: {filepath} empty or missing, 0 sized")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"WARNING: {filepath} contains invalid/corrupted byte sequences")
        return False

    if len(lines) < 3:
        print(f"WARNING: {filepath} has fewer than 3 lines (missing header or data)")
        return False

    # Reject HTML pages (e.g., 404/503 responses saved as .txt)
    head_sample = "".join(lines[:5]).lower()
    if "<html" in head_sample or "<!doctype" in head_sample:
        print(f"WARNING: {filepath} contains a corrupted HTML page")
        return False

    # Check standard NDBC 2-line header
    if not (lines[0].startswith('#YY') and lines[1].startswith('#yr')):
        print(f"WARNING: {filepath} missing valid NDBC headers (#YY / #yr)")
        return False

    # Verify data rows have expected columns and valid timestamps
    valid_data_rows = 0
    for line_num, line in enumerate(lines[2:], start=3):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if '\x00' in stripped:
            print(f"WARNING: {filepath} contains null bytes on line {line_num}")
            return False

        parts = stripped.split()
        if len(parts) != expected_cols:
            print(f"WARNING: {filepath} malformed on line {line_num} "
                  f"(expected {expected_cols} cols, got {len(parts)})")
            return False

        try:
            yy, mm, dd, hh, mn = map(int, parts[:5])
            datetime.datetime(yy, mm, dd, hh, mn)
        except ValueError:
            print(f"WARNING: {filepath} has invalid timestamp on line {line_num}: {parts[:5]}")
            return False

        valid_data_rows += 1

    if valid_data_rows == 0:
        print(f"WARNING: {filepath} contains headers only and no valid data rows")
        return False

    return True


# Read in location data file
buoy_with_loc_list = []
with open(MET_NDBC_STATIONS, 'r') as f:
    for line in f:
        buoy_with_loc_list.append(
            line.partition('<station id="')[2].partition('"')[0]
        )

# Validate and stage files for buoys with location data
for ndbc_input_file in glob.glob(os.path.join(DCOMROOT,
                                             f"{INITDATE_dt:%Y%m%d}",
                                             'validation_data', 'marine',
                                             'buoy', '*.txt')):
    buoy_id = os.path.basename(ndbc_input_file).partition('.')[0]
    if buoy_id not in buoy_with_loc_list:
        continue

    ndbc_tmp_file = os.path.join(DATA, f"{RUN}.{INITDATE_dt:%Y%m%d}",
                                 OBTYPE, 'buoy', f"{buoy_id}.txt")
    ndbc_output_file = os.path.join(COMOUTprep, f"{RUN}.{INITDATE_dt:%Y%m%d}",
                                    OBTYPE, 'buoy', f"{buoy_id}.txt")

    # Ensure target directories exist
    os.makedirs(os.path.dirname(ndbc_tmp_file), exist_ok=True)
    os.makedirs(os.path.dirname(ndbc_output_file), exist_ok=True)

    # Restart handling: validate existing COMOUTprep file before reusing it
    if os.path.exists(ndbc_output_file):
        if is_valid_ndbc_file(ndbc_output_file):
            print(f"RESTART: {ndbc_output_file} exists and is valid; Copying to {ndbc_tmp_file}")
            shutil.copy2(ndbc_output_file, ndbc_tmp_file)
            continue
        else:
            print(f"WARNING: Existing restart file {ndbc_output_file} is corrupted; removing and re-checking DCOM input")
            os.remove(ndbc_output_file)

    # Validate DCOM input file before copying to DATA and COMOUTprep
    if is_valid_ndbc_file(ndbc_input_file):
        print(f"Copying {ndbc_input_file} to {ndbc_tmp_file}")
        shutil.copy2(ndbc_input_file, ndbc_tmp_file)
        if SENDCOM == 'YES' and os.path.exists(ndbc_tmp_file):
            print(f"Copying {ndbc_tmp_file} to {ndbc_output_file}")
            shutil.copy2(ndbc_tmp_file, ndbc_output_file)
    else:
        print(f"WARNING: Corrupted validation file: {ndbc_input_file} is corrupted for valid date {INITDATE_dt:%Y%m%d}. METplus will skip this file.")

print("END: " + os.path.basename(__file__))
