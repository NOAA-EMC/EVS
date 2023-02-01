# =============================================================================
#
# NAME: cam_util.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Various Utilities for EVS CAM Verification
# 
# =============================================================================

import numpy as np
import subprocess

def get_all_eval_periods(graphics):
    all_eval_periods = []
    for component in graphics:                                                               
        for verif_case in graphics[component]:                                                 
            for verif_type in graphics[component][verif_case]:                                     
                verif_type_dict = graphics[component][verif_case][verif_type]
                for models in verif_type_dict:
                    for plot_type in verif_type_dict[models]:           
                        all_eval_periods.append(
                            verif_type_dict[models][plot_type]['EVAL_PERIODS']
                        )
    return np.unique(np.hstack(all_eval_periods))

def get_fhr_start(vhour, acc, fhr_incr, min_ihour):
    fhr_start = (
        float(vhour) + float(min_ihour)
        + (
            float(fhr_incr)
            * np.ceil(
                (float(acc)-float(vhour)-float(min_ihour))
                / float(fhr_incr)
            )
        )
    )
    return int(fhr_start)

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
        print("ERROR: "+''.join(run_command.args)+" gave return code "
              + str(run_command.returncode))
    else:
        if capture_output:
            return run_command.stdout.decode('utf-8')
