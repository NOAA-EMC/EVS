#!/usr/bin/env python3
# =============================================================================
#
# NAME: analyses_util.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Pery Shafran, perry.shafran@noaa.gov
# PURPOSE: Various Utilities for EVS analyses Verification
# 
# =============================================================================

import os
from pathlib import Path
from collections.abc import Iterable
import numpy as np
import subprocess
import glob
from datetime import datetime, timedelta as td

def run_shell_command(command, capture_output=False):
    """! Run shell command

        Args:
            command - list of argument entries (string)

        Returns:

    """
    print("Running "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>']):
        run_command = subprocess.run(
            ' '.join(command), shell=True, capture_output=capture_output
        )
    else:
        run_command = subprocess.run(command, capture_output=capture_output)
    if run_command.returncode != 0:
        print("FATAL ERROR: "+''.join(run_command.args)+" gave return code "
              + str(run_command.returncode))
    else:
        if capture_output:
            return run_command.stdout.decode('utf-8')

