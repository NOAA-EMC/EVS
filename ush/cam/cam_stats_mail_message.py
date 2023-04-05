import os
import numpy as np
from glob import glob
import re
import cam_util as cutil

maillist = os.environ['maillist']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
MODELNAME = os.environ['MODELNAME']
VDATE = os.environ['VDATE']
DATA = os.environ['DATA']
MET_PLUS_OUT = os.path.join(DATA, VERIF_CASE, 'METplus_output')
met_process_names = [
    'point_stat', 'genvxmask', 'pcp_combine', 'grid_stat', 'pb2nc', 'ascii2nc'
]
error_search_strs1 = ["ERROR", "Could not find", "file", "using template"]
error_search_strs2 = ["FileNotFoundError", "No such file or directory"]
idx1_str1 = "file"
idx1_str2 = "using"
idx2_str1 = "directory: '"
idx2_str2 = "'"
max_num_files=10

# Get list of directories
log_dirs = []
log_dirs.append(os.path.join(MET_PLUS_OUT, 'gather_small', 'stat_analysis', 'logs'))
log_dirs.append(os.path.join(MET_PLUS_OUT, 'stat_analysis', 'logs'))
log_dirs = np.hstack((
    log_dirs,
    list(cutil.flatten([
        glob(os.path.join(MET_PLUS_OUT,'*',process,'logs'))
        for process in met_process_names
    ]))
))
log_dirs = np.hstack((
    log_dirs,
    list(cutil.flatten([
        glob(os.path.join(MET_PLUS_OUT,'*','*',process,'logs'))
        for process in met_process_names
    ]))
))
# Get list of log files that include line, error_search_str
log_fnames = list(cutil.flatten(glob(os.path.join(log_dir, '*')) for log_dir in log_dirs))
error_lines = []
for fname in log_fnames:
    if os.path.isfile(fname):
        with open(fname) as f:
            read_file = f.read()
            look_in1 = 1
            look_in2 = 1
            for search_str in error_search_strs1:
                if search_str not in read_file:
                    look_in1 = 0
                    break
            for search_str in error_search_strs2:
                if search_str not in read_file:
                    look_in2 = 0
                    break
        if look_in1 or look_in2:
            with open(fname) as f:
                for line in f:
                    if look_in1:
                        print(2)
                        if all(search_str in line for search_str in error_search_strs1):
                            error_lines.append(
                                re.search(
                                    f"^.*{idx1_str1}(.*?){idx1_str2}.*$", 
                                    line    
                                ).group(1).replace(' ','')
                            )
                    if look_in2:
                        if all(search_str in line for search_str in error_search_strs2):
                            error_lines.append(
                                re.search(
                                    f"^.*{idx2_str1}(.*?){idx2_str2}.*$", 
                                    line    
                                ).group(1).replace(' ','')
                            )
quit_msg = ("A search of METplus output log files discovered no missing"
            + f" data.")
if not error_lines or not any(error_lines):
    print(quit_msg)
else:
    error_lines = list(set(error_lines))
    filtered_error_lines = []
    for error_line in error_lines:
        keep = 1
        # Ensure lowest- and next-lowest-level directories exist
        if not os.access(os.path.dirname(error_line), os.W_OK):
            if not os.access(os.path.dirname(
                    os.path.dirname(error_line)), os.W_OK):
                keep = 0
        if keep:
            filtered_error_lines.append(os.path.split(error_line)[-1])
    if len(filtered_error_lines) == 0:
        print(quit_msg)
    else:
        data_names = [
            cutil.get_data_type(fname) 
            for fname in filtered_error_lines
        ]
        unknown_filenames = [
            fname for f, fname in enumerate(filtered_error_lines) 
            if data_names[f] == "Unknown Data Type"
        ]
        data_names = np.unique(data_names)
        JOB=f"EVS {COMPONENT}/{MODELNAME}/{VERIF_CASE}"
        if len(data_names) == 1:
            if data_names[0] == "Unknown Data Type":
                DATAsubj = "Unrecognized data"
            else:
                DATAsubj = f"{data_names[0]} data"
            DATAmsg_body = '.'
        else:
            DATAsubj = f"Several datasets"
            DATAmsg_body = ':\n'+'\n'.join(data_names)
        subject = f"EVS/{COMPONENT}: {DATAsubj} missing for {VDATE}"
        DATAmsg_head = (f"Warning: {DATAsubj} are missing for"
                        + f" the {JOB} verification job valid on"
                        + f" {VDATE}")
        DATAmsg = DATAmsg_head + DATAmsg_body

        if "Unknown Data Type" in data_names:
            if len(unknown_filenames) > max_num_files:
                DATAmsg += (f"\nThe following missing files were associated"
                            + f" with the unrecognized data set (showing"
                            + f" {max_num_files} of"
                            + f" {len(unknown_filenames)} total files):\n")
                for fname in unknown_filenames[:max_num_files]:
                    DATAmsg+=f"{fname}\n"
            else:
                DATAmsg += (f"\nThe following missing files were associated"
                            + f" with the unrecognized data set:\n")
                for fname in unknown_filenames:
                    DATAmsg+=f"{fname}\n"
        cutil.run_shell_command([
            'echo', f'\"{DATAmsg}\"', '>>mailmsg'
        ])
        cutil.run_shell_command([
            'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
            f'\"{maillist}\"'
        ])
