#!/usr/bin/env python3
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
jobid = os.environ['jobid']
CYC = os.environ['cyc']
MET_PLUS_OUT = os.path.join(DATA, VERIF_CASE, 'METplus_output')
met_process_names = [
    'point_stat', 'genvxmask', 'pcp_combine', 'grid_stat', 'pb2nc', 'ascii2nc'
] # used for defining list of paths to read from

# Filter log files and then lines based on whether or not they contain the ... 
# ... following list of strings, used to find lines with a specific error ...  
# ... that relates to missing files.  You may define two such lines.
error_search_strs1 = ["ERROR", "Could not find", "file", "using template"]
error_search_strs2 = ["FileNotFoundError", "No such file or directory"]

# For "E" specific error related to a missing file, the string that ...
# ... precedes the name of the file is idxE_str1 and the string that ...
# ... follows the name of the file is idxE_str2. 
idx1_str1 = "file"
idx1_str2 = "using"
idx2_str1 = "directory: '"
idx2_str2 = "'"
max_num_files=10

# Define the list of paths to log directories that contain METplus log files 
# ... to be searched for missing data files
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
                        if all(search_str in line for search_str in error_search_strs1):
                            error_lines.append(
                                re.search(
                                    f"^.*{idx1_str1}(.*?){idx1_str2}.*$", 
                                    line    
                                ).group(1).replace(' ','')
                                .replace("'","").replace('"','')
                            )
                    if look_in2:
                        if all(search_str in line for search_str in error_search_strs2):
                            error_lines.append(
                                re.search(
                                    f"^.*{idx2_str1}(.*?){idx2_str2}.*$", 
                                    line    
                                ).group(1).replace(' ','')
                                .replace("'","").replace('"','')
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
        if not os.access(os.path.dirname(error_line), os.F_OK):
            if not os.access(os.path.dirname(
                    os.path.dirname(error_line)), os.F_OK):
                keep = 0
        if keep:
            filtered_error_lines.append(os.path.split(error_line)[-1])
    if len(filtered_error_lines) == 0:
        print(quit_msg)
    else:
        data_info = [
            cutil.get_data_type(fname) 
            for fname in filtered_error_lines
        ]
        gen_names = []
        anl_names = []
        fcst_names = []
        unk_names = []
        gen_fnames = []
        anl_fnames = []
        fcst_fnames = []
        unk_fnames = []
        for i, info in enumerate(data_info):
            if info[1] == "gen":
                gen_names.append(info[0])
                gen_fnames.append(filtered_error_lines[i])
                gen_names = np.unique(gen_names)
            elif info[1] == "anl":
                anl_names.append(info[0])
                anl_fnames.append(filtered_error_lines[i])
                anl_names = np.unique(anl_names)
            elif info[1] == "fcst":
                fcst_names.append(info[0])
                fcst_fnames.append(filtered_error_lines[i])
                fcst_names = np.unique(fcst_names)
            elif info[1] == "unk":
                unk_names.append(info[0])
                unk_fnames.append(filtered_error_lines[i])
                unk_names = np.unique(unk_names)
            else:
                print(f"ERROR: Undefined data type for missing data file: {info[1]}"
                      + f"\nPlease edit the get_data_type() function in"
                      + f" USHevs/cam/cam_util.py")
                sys.exit(1)
        if unk_names:
            if len(unk_names) == 1:
                DATAsubj = "Unrecognized"
            else:
                DATAsubj = ', '.join(unk_names)
            subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
            DATAmsg_head = (f"Warning: Some unrecognized data were unavailable"
                            + f" for valid date {VDATE} and cycle {CYC}Z.")
            if len(unk_fnames) > max_num_files:
                DATAmsg_body1 = (f"\nMissing files are: (showing"
                            + f" {max_num_files} of"
                            + f" {len(unk_fnames)} total files)\n")
                for fname in unk_fnames[:max_num_files]:
                    DATAmsg_body1+=f"{fname}\n"
            else:
                DATAmsg_body1 = (f"Missing files are:\n")
                for fname in unk_fnames:
                    DATAmsg_body1+=f"{fname}\n"
            DATAmsg_body2 = f"Job ID: {jobid}"
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_head}\"', '>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body1}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body2}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
                f'\"{maillist}\"'
            ])
        if gen_names:
            if len(gen_names) == 1:
                DATAsubj = gen_names[0]
            else:
                DATAsubj = ', '.join(gen_names)
            subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
            DATAmsg_head = (f"Warning: No {DATAsubj} data were available"
                            + f" for valid date {VDATE} and cycle {CYC}Z.")
            if len(gen_fnames) > max_num_files:
                DATAmsg_body1 = (f"\nMissing files are: (showing"
                            + f" {max_num_files} of"
                            + f" {len(gen_fnames)} total files)\n")
                for fname in gen_fnames[:max_num_files]:
                    DATAmsg_body1+=f"{fname}\n"
            else:
                DATAmsg_body1 = (f"Missing files are:\n")
                for fname in gen_fnames:
                    DATAmsg_body1+=f"{fname}\n"
            DATAmsg_body2 = f"Job ID: {jobid}"
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_head}\"', '>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body1}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body2}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
                f'\"{maillist}\"'
            ])
        if anl_names:
            if len(anl_names) == 1:
                DATAsubj = anl_names[0]
            else:
                DATAsubj = ', '.join(anl_names)
            subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
            DATAmsg_head = (f"Warning: No {DATAsubj} data were available"
                            + f" for valid date {VDATE} and cycle {CYC}Z.")
            if len(anl_fnames) > max_num_files:
                DATAmsg_body1 = (f"\nMissing files are: (showing"
                            + f" {max_num_files} of"
                            + f" {len(anl_fnames)} total files)\n")
                for fname in anl_fnames[:max_num_files]:
                    DATAmsg_body1+=f"{fname}\n"
            else:
                DATAmsg_body1 = (f"Missing files are:\n")
                for fname in anl_fnames:
                    DATAmsg_body1+=f"{fname}\n"
            DATAmsg_body2 = f"Job ID: {jobid}"
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_head}\"', '>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body1}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body2}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
                f'\"{maillist}\"'
            ])
        if fcst_names:
            if len(fcst_names) == 1:
                DATAsubj = fcst_names[0]
            else:
                DATAsubj = ', '.join(fcst_names)
            lead_hour_matches = [
                re.search('f(\d+)', fcst_fname) for fcst_fname in fcst_fnames
            ]
            lead_hours = [
                str(int(match.group(1))).zfill(3) 
                for match in lead_hour_matches if match
            ]
            lead_hours = np.unique(lead_hours)
            if lead_hours:
                if len(lead_hours) == 1:
                    subject = (f"F{lead_hours[0]} {DATAsubj} Data Missing for"
                               + f" EVS {COMPONENT}")
                    DATAmsg_head = (f"Warning: No {DATAsubj} data were"
                                    + f" available for valid date {VDATE},"
                                    + f" cycle {CYC}Z, and f{lead_hours[0]}.")
                else:
                    lead_string = ', '.join(
                        [f'f{lead}' for lead in lead_hours]
                    )
                    subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                    DATAmsg_head = (f"Warning: No {DATAsubj} data were"
                                    + f" available for valid date {VDATE},"
                                    + f" cycle {CYC}Z, and {lead_string}.")
            if len(fcst_fnames) > max_num_files:
                DATAmsg_body1 = (f"\nMissing files are: (showing"
                            + f" {max_num_files} of"
                            + f" {len(fcst_fnames)} total files)\n")
                for fname in fcst_fnames[:max_num_files]:
                    DATAmsg_body1+=f"{fname}\n"
            else:
                DATAmsg_body1 = (f"Missing files are:\n")
                for fname in fcst_fnames:
                    DATAmsg_body1+=f"{fname}\n"
            DATAmsg_body2 = f"Job ID: {jobid}"
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_head}\"', '>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body1}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'echo', f'\"{DATAmsg_body2}\"', '>>mailmsg'
            ])
            cutil.run_shell_command([
                'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
                f'\"{maillist}\"'
            ])
