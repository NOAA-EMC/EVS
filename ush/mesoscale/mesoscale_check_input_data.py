#!/usr/bin/env python3
# =============================================================================
#
# NAME: mesoscale_check_input_data.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Check Availability of Input Data
# DEPENDENCIES: os.path.join([
#                   SCRIPTSevs,COMPONENT,STEP,
#                   "_".join(["exevs",MODELNAME,VERIF_CASE,STEP+".sh"]
#               )]
#
# =============================================================================

import sys
import os
from datetime import datetime, timedelta as td
import numpy as np
import mesoscale_util as cutil
import re

print(f"BEGIN: {os.path.basename(__file__)}")

# Construct a file name given a template
def fname_constructor(template_str, IDATE="YYYYmmdd", IHOUR="HH", 
                      VDATE="YYYYmmdd", VHOUR="HH", VDATEHOUR="YYYYmmddHH",
                      VDATEm1H="YYYYmmdd", VDATEHOURm1H="YYYYmmddHH", 
                      FHR="HH", LVL="0"):
    template_str = template_str.replace('{IDATE}', IDATE)
    template_str = template_str.replace('{IHOUR}', IHOUR)
    template_str = template_str.replace('{VDATE}', VDATE)
    template_str = template_str.replace('{VHOUR}', VHOUR)
    template_str = template_str.replace('{VDATEHOUR}', VDATEHOUR)
    template_str = template_str.replace('{VDATEm1H}', VDATEm1H)
    template_str = template_str.replace('{VDATEHOURm1H}', VDATEHOURm1H)
    template_str = template_str.replace('{FHR}', FHR)
    template_str = template_str.replace('{LVL}', LVL)
    return template_str


# Determine whether or not to proceed
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
proceed = 0
if STEP == 'stats':
    proceed = 1


if proceed:
    # Load environment variables
    send_mail = 0
    mdf=0
    max_num_files = 10
    SENDMAIL = os.environ['SENDMAIL']
    COMPONENT = os.environ['COMPONENT']
    MAILTO = os.environ['MAILTO']
    VHR = os.environ['vhr']
    jobid = os.environ['jobid']
    FIXevs = os.environ['FIXevs']
    VDATE = os.environ['VDATE']
    VHOUR = os.environ['VHOUR']
    vdate = datetime.strptime(VDATE+VHOUR, '%Y%m%d%H')
    FHR_END_FULL = os.environ['FHR_END_FULL']
    FHR_END_SHORT = os.environ['FHR_END_SHORT']
    NEST = os.environ['NEST']
    if STEP == 'stats':
        if  SENDMAIL == "YES":
            send_mail = 1
        MODELNAME = os.environ['MODELNAME']
        FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
        FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
        FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
        MIN_IHOUR = os.environ['MIN_IHOUR']
        if VERIF_CASE == 'grid2obs':
            COMINobsproc = os.environ['COMINobsproc']
            COMINnam = os.environ['COMINnam']
            COMINrap = os.environ['COMINrap']
        if MODELNAME == 'nam':
            COMINfcst = os.environ['COMINnam']
        elif MODELNAME == 'rap':
            COMINfcst = os.environ['COMINrap']
        else:
            print(f"The provided MODELNAME ({MODELNAME}) is not recognized. Quitting ...")
            sys.exit(1)

    vdates = [vdate]

    leads_list = []
    if STEP == 'stats':
            for v in vdates:
                leads = []
                for group in FHR_GROUP_LIST.split(' '):
                    if group == 'SHORT':
                        fhr_incr = int(FHR_INCR_SHORT)
                        fhr_end = int(FHR_END_SHORT)
                        if MODELNAME == 'nam':
                            MIN_IHOUR = "00"
                        elif MODELNAME == 'rap':
                            MIN_IHOUR = "00"
                    elif group == 'FULL':
                        fhr_incr = int(FHR_INCR_FULL)
                        fhr_end = int(FHR_END_FULL)
                        if MODELNAME == 'nam':
                            MIN_IHOUR = "00"
                        elif MODELNAME == 'rap':
                            MIN_IHOUR = "03"
                    else:
                        print(f"Unrecognized FHR_GROUP ({group}) ... Quitting.")
                        sys.exit(1)
                    fhr_start = cutil.get_fhr_start(v.hour, 0, fhr_incr, int(MIN_IHOUR))
                    leads = np.hstack((leads,np.arange(fhr_start, fhr_end+1, fhr_incr)))
                leads_list.append(leads)
    else:
            for v in vdates:
                leads_list.append(np.arange(0, int(FHR_END_FULL)))


    # Calculate all init hours
    inits_list = []
    for vi, v in enumerate(vdates):
        inits = [v - td(hours=int(h)) for h in leads_list[vi]]
        inits_list.append(inits)


    # Check for missing masks
    # Make list of paths
    mask_files = []
    conus_mask_files = [
        'Bukovsky_G221_CONUS.nc',
        'Bukovsky_G221_CONUS_East.nc',
        'Bukovsky_G221_CONUS_West.nc',
        'Bukovsky_G221_CONUS_Central.nc',
        'Bukovsky_G221_CONUS_South.nc',
    ]
    subreg_mask_files = [
        'Bukovsky_G221_Appalachia.nc',
        'Bukovsky_G221_CPlains.nc',
        'Bukovsky_G221_DeepSouth.nc',
        'Bukovsky_G221_GreatBasin.nc',
        'Bukovsky_G221_GreatLakes.nc',
        'Bukovsky_G221_Mezquital.nc',
        'Bukovsky_G221_MidAtlantic.nc',
        'Bukovsky_G221_NorthAtlantic.nc',
        'Bukovsky_G221_NPlains.nc',
        'Bukovsky_G221_NRockies.nc',
        'Bukovsky_G221_PacificNW.nc',
        'Bukovsky_G221_PacificSW.nc',
        'Bukovsky_G221_Prairie.nc',
        'Bukovsky_G221_Southeast.nc',
        'Bukovsky_G221_SPlains.nc',
        'Bukovsky_G221_SRockies.nc',
    ]
    ak_mask_files = [
        'Alaska_G091.nc',
    ]
    namer_mask_files = [
        'G221_NAMER.nc',
    ]
    conusc_mask_files = [
        'Bukovsky_G221_CONUS.nc',
        'Bukovsky_G221_CONUS_East.nc',
        'Bukovsky_G221_CONUS_West.nc',
        'Bukovsky_G221_CONUS_Central.nc',
        'Bukovsky_G221_CONUS_South.nc',
    ]
    akc_mask_files = [
        'Alaska_G091.nc',
    ]
    conusp_mask_files = [
        'Bukovsky_G218_CONUS.nc',
        'Bukovsky_G218_CONUS_East.nc',
        'Bukovsky_G218_CONUS_West.nc',
        'Bukovsky_G218_CONUS_Central.nc',
        'Bukovsky_G218_CONUS_South.nc',
    ]
    if NEST == 'conus':
        mask_files = np.hstack((mask_files, conus_mask_files))
    elif NEST == 'subreg':
        mask_files = np.hstack((mask_files, subreg_mask_files))
    elif NEST == 'ak':
        mask_files = np.hstack((mask_files, ak_mask_files))
    elif NEST == 'namer':
        mask_files = np.hstack((mask_files, namer_mask_files))
    elif NEST == 'conusc':
        mask_files = np.hstack((mask_files, conusc_mask_files))
    elif NEST == 'akc':
        mask_files = np.hstack((mask_files, akc_mask_files))
    elif NEST == 'conusp':
        mask_files = np.hstack((mask_files, conusp_mask_files))
    mask_paths = [
        os.path.join(FIXevs, 'masks', mask_file) for mask_file in mask_files
    ]
    
    # Record paths that don't exist
    missing_mask_files = []
    for mask_path in mask_paths:
        if not os.path.exists(mask_path):
            missing_mask_files.append(mask_path)
    
    # Print warning for missing masks
    if missing_mask_files:
        print(f"WARNING: The following masks were not found in the fix directory"
              + f" ({FIXevs}):")
        for missing_mask_file in missing_mask_files:
            print(missing_mask_file)


    # Check for missing forecasts
    # Make list of paths
    if STEP == 'stats':
        fcst_templates = []
        if MODELNAME == 'nam':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst, 
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip32{FHR}.tm00.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip32{FHR}.tm00.grib2'
                ))
            elif NEST == 'akc':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip32{FHR}.tm00.grib2'
                ))
            elif NEST == 'conusc':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip32{FHR}.tm00.grib2'
                ))
            elif NEST == 'conusp':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip12{FHR}.tm00.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.awip32{FHR}.tm00.grib2'
                ))
        elif MODELNAME == 'rap':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'rap.{IDATE}',
                    'rap.t{IHOUR}z.awip32f{FHR}.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'rap.{IDATE}',
                    'rap.t{IHOUR}z.awip32f{FHR}.grib2'
                ))
            elif NEST == 'akc':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'rap.{IDATE}',
                    'rap.t{IHOUR}z.awp242f{FHR}.grib2'
                ))
            elif NEST == 'conusc':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'rap.{IDATE}',
                    'rap.t{IHOUR}z.awp130pgrbf{FHR}.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'rap.{IDATE}',
                    'rap.t{IHOUR}z.awip32f{FHR}.grib2'
                ))
        else:
            print(f"The provided MODELNAME ({MODELNAME}) is not recognized."
                  + f" Quitting ...")
            sys.exit(1)
    else:
        fcst_templates = []
    fcst_paths = []
    for v, leads in enumerate(leads_list):
        for i, FHR in enumerate(leads):
            IDATE = inits_list[v][i].strftime('%Y%m%d')
            IHOUR = inits_list[v][i].strftime('%H')
            for template in fcst_templates:
                fcst_paths.append(fname_constructor(
                        template, IDATE=IDATE, IHOUR=IHOUR, 
                        FHR=str(int(FHR)).zfill(2)
                ))
    fcst_paths = np.unique(fcst_paths)
    
    # Record paths that don't exist
    missing_fcst_paths = []
    missing_fcst_files = []
    for fcst_path in fcst_paths:
        if not os.path.exists(fcst_path):
            missing_fcst_files.append(os.path.split(fcst_path)[-1])
            missing_fcst_paths.append(fcst_path)
    
    # Print warning (mdf) and send an email for missing data
    if missing_fcst_paths:
        print(f"WARNING: The following forecasts were not found:")
        for missing_fcst_path in missing_fcst_paths:
            print(missing_fcst_path)
        if send_mail:
            mdf+=1
            data_info = [
                cutil.get_data_type(fname) 
                for fname in missing_fcst_files
            ]
            fcst_names = []
            unk_names = []
            fcst_fnames = []
            unk_fnames = []
            for i, info in enumerate(data_info):
                if info[1] == "fcst":
                    fcst_names.append(info[0])
                    fcst_fnames.append(missing_fcst_files[i])
                elif info[1] == "unk":
                    unk_names.append(info[0])
                    unk_fnames.append(missing_fcst_files[i])
                else:
                    print(f"ERROR: Undefined data type for missing data file: {info[1]}"
                          + f"\nPlease edit the get_data_type() function in"
                          + f" USHevs/mesoscale/mesoscale_util.py")
                    sys.exit(1)
            fcst_names = np.unique(fcst_names)
            unk_names = np.unique(unk_names)
            if unk_names.size > 0:
                if len(unk_names) == 1:
                    DATAsubj = "Unrecognized"
                else:
                    DATAsubj = ', '.join(unk_names)
                subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                DATAmsg_head = (f"Warning: Some unrecognized data were unavailable"
                                + f" for valid date {VDATE} and cycle {VHR}Z.")
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
                    # 'cat', 'mailmsg', '|' , 'mail.py', '-s', f'\"{subject}\"', 
                    # f'\"{MAILTO}\"', '-v'
                    'cat', 'mailmsg', '|' , 'mail', '-s', f'\"{subject}\"', 
                    f'\"{MAILTO}\"'
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
                if lead_hours.size > 0:
                    if len(lead_hours) == 1:
                        subject = (f"F{lead_hours[0]} {DATAsubj} Data Missing for"
                                   + f" EVS {COMPONENT}")
                        DATAmsg_head = (f"Warning: No {DATAsubj} data were"
                                        + f" available for valid date {VDATE},"
                                        + f" cycle {VHR}Z, and f{lead_hours[0]}.")
                    else:
                        lead_string = ', '.join(
                            [f'f{lead}' for lead in lead_hours]
                        )
                        subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                        DATAmsg_head = (f"Warning: No {DATAsubj} data were"
                                        + f" available for valid date {VDATE},"
                                        + f" cycle {VHR}Z, and {lead_string}.")
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
                    f'\"{MAILTO}\"'
                ])


    # Check for missing obs data (analyses or da)
    # Make list of paths
    anl_templates = []
    if STEP == 'stats':
        if VERIF_CASE == 'grid2obs':
            # Expect PrepBufr to at least be available at these times
            if VHOUR in ['00', '06', '12', '18']:
                anl_templates.append(os.path.join(
                    COMINobsproc, 
                    'nam.{VDATE}',
                    'nam.t{VHOUR}z.prepbufr.tm00'
                ))
                anl_templates.append(os.path.join(
                    COMINobsproc, 
                    'gdas.{VDATE}',
                    '{VHOUR}',
                    'atmos',
                    'gdas.t{VHOUR}z.prepbufr'
                ))
    anl_paths = []
    for v, vdate in enumerate(vdates):
        for template in anl_templates:
            anl_paths.append(fname_constructor(
                    template, VDATE=vdate.strftime('%Y%m%d'), VHOUR=vdate.strftime('%H')
            ))
    anl_paths = np.unique(anl_paths)

    # Record paths that don't exist
    missing_anl_paths = []
    missing_anl_files = []
    for anl_path in anl_paths:
        if not os.path.exists(anl_path):
            missing_anl_files.append(os.path.split(anl_path)[-1])
            missing_anl_paths.append(anl_path)

    # Print warning (mdf) and send an email for missing data
    if missing_anl_paths:
        print(f"WARNING: The following analyses were not found:")
        for missing_anl_path in missing_anl_paths:
            print(missing_anl_path)
        if send_mail:
            mdf+=1
            data_info = [
                cutil.get_data_type(fname) 
                for fname in missing_anl_files
            ]
            anl_names = []
            unk_names = []
            anl_fnames = []
            unk_fnames = []
            for i, info in enumerate(data_info):
                if info[1] == "anl":
                    anl_names.append(info[0])
                    anl_fnames.append(missing_anl_files[i])
                elif info[1] == "unk":
                    unk_names.append(info[0])
                    unk_fnames.append(missing_anl_files[i])
                else:
                    print(f"ERROR: Undefined data type for missing data file: {info[1]}"
                          + f"\nPlease edit the get_data_type() function in"
                          + f" USHevs/mesoscale/mesoscale_util.py")
                    sys.exit(1)
            anl_names = np.unique(anl_names)
            unk_names = np.unique(unk_names)
            if unk_names.size > 0:
                if len(unk_names) == 1:
                    DATAsubj = "Unrecognized"
                else:
                    DATAsubj = ', '.join(unk_names)
                subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                DATAmsg_head = (f"Warning: Some unrecognized data were unavailable"
                                + f" for valid date {VDATE} at {VHOUR}Z.")
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
                    f'\"{MAILTO}\"'
                ])
            if anl_names.size > 0:
                if len(anl_names) == 1:
                    DATAsubj = anl_names[0]
                else:
                    DATAsubj = ', '.join(anl_names)
                subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                DATAmsg_head = (f"Warning: No {DATAsubj} data were available"
                                + f" for valid date {VDATE} at {VHOUR}Z.")
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
                    f'\"{MAILTO}\"'
                ])



    # exit with warning (mdf)
    if mdf:
        sys.exit(mdf)

print(f"END: {os.path.basename(__file__)}")
