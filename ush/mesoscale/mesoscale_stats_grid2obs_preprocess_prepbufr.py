#!/usr/bin/env python3
'''
Name: mesoscale_stats_grid2obs_preprocess_prepbufr.py
Contact(s): Marcel Caron (marcel.caron@noaa.gov)
Abstract: Preprocess input prepbufr files and store the preprocessed file in 
          DATA. Preprocessing currently includes splitting each file into
          multiple files by subset (i.e. message type, e.g., ADPUPA), and
          concatenating the desired subsets to a new smaller file.
Run By: scripts/stats/mesoscale/exevs_nam_grid2obs_stats.sh
        scripts/stats/mesoscale/exevs_rap_grid2obs_stats.sh
'''
import os
from datetime import datetime
import mesoscale_util as cutil

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
