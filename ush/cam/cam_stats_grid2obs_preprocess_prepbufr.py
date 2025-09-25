#!/usr/bin/env python3
"""
cam_stats_grid2obs_preprocess_prepbufr.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Preprocesses input prepbufr files and stores the preprocessed files in DATA
for the cam component. Preprocessing includes splitting each file by subset
(e.g., message type such as ADPUPA) and concatenating the desired subsets to a
new smaller file.

Environment Variables (Inputs):
    DATA, COMINobsproc, MODELNAME, VERIF_CASE, VERIF_TYPE, VDATE, VHOUR

Outputs:
    - Preprocessed prepbufr files in the appropriate output directory.
    - Prints errors and exits if required environment variables or settings are
      missing or invalid.

This script is intended to be run as part of the cam component to automate
preprocessing of prepbufr files for Grid2Obs verification.
"""

import os
from datetime import datetime

import cam_util as cutil

print("BEGIN: "+os.path.basename(__file__))

# Run split_by_subset on all INPUT_FILES, saving SUBSETS we want to OUTPUT_DIT
DATA = os.environ['DATA']
COMINobsproc = os.environ['COMINobsproc']
MODELNAME = os.environ['MODELNAME']
VERIF_CASE = os.environ['VERIF_CASE']
VERIF_TYPE = os.environ['VERIF_TYPE']
VDATE = os.environ['VDATE']
VHOUR = os.environ['VHOUR']

workdir = os.path.join(DATA, VERIF_CASE, 'data', MODELNAME, 'tmp')
outdir = os.path.join(DATA, VERIF_CASE, 'data', VERIF_TYPE, 'prepbufr')
if VERIF_TYPE == 'raob':
    subsets = ['ADPUPA']
elif VERIF_TYPE == 'metar':
    subsets = ['ADPSFC']
else:
    raise ValueError(
        f'\"{VERIF_TYPE}\" is not a valid VERIF_TYPE for ' 
        + '{os.path.basename(__file__)}'
    )
vdate = datetime.strptime(VDATE+VHOUR, '%Y%m%d%H')
infiles = cutil.get_prepbufr_templates(COMINobsproc, [vdate])

for infile in infiles:
    indir, fname = os.path.split(infile)
    cutil.preprocess_prepbufr(
        indir, fname, workdir, outdir, subsets
    )

print("END: "+os.path.basename(__file__))
