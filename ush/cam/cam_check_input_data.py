#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_check_input_data.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
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
import cam_util as cutil
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
elif STEP == 'prep':
    if VERIF_CASE == 'precip':
        proceed = 1


if proceed:
    # Load environment variables
    send_mail = 0
    missing_data_flag=0
    max_num_files = 10
    COMPONENT = os.environ['COMPONENT']
    SENDMAIL = os.environ['SENDMAIL']
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
        send_mail = 1
        MODELNAME = os.environ['MODELNAME']
        FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
        FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
        FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
        MIN_IHOUR = os.environ['MIN_IHOUR']
        if VERIF_CASE == 'grid2obs':
            COMINobsproc = os.environ['COMINobsproc']
            COMINnam = os.environ['COMINnam']
        elif VERIF_CASE == 'snowfall':
            DCOMINsnow = os.environ['DCOMINsnow']
            OBS_ACC = os.environ['OBS_ACC']
            ACC = os.environ['ACC']
        elif VERIF_CASE == 'precip':
            ACC = os.environ['ACC']
        if MODELNAME == 'namnest':
            COMINfcst = os.environ['COMINnam']
        elif MODELNAME == 'hireswarw':
            COMINfcst = os.environ['COMINhiresw']
        elif MODELNAME == 'hireswarwmem2':
            COMINfcst = os.environ['COMINhiresw']
        elif MODELNAME == 'hireswfv3':
            COMINfcst = os.environ['COMINhiresw']
        elif MODELNAME == 'hrrr':
            COMINfcst = os.environ['COMINhrrr']
        else:
            print(f"The provided MODELNAME ({MODELNAME}) is not recognized. Quitting ...")
            sys.exit(1)
    if VERIF_CASE == 'precip':
        if STEP == 'stats':
            EVSINmrms = os.environ['EVSINmrms']
            EVSINccpa = os.environ['EVSINccpa']
        elif STEP == 'prep':
            DCOMINmrms = os.environ['DCOMINmrms']
            COMINccpa = os.environ['COMINccpa']


    # Calculate all lead hours
    if VERIF_CASE == 'precip':
        vdates = [vdate-td(hours=int(hour)) for hour in np.arange(23)]
    else:
        vdates = [vdate]

    leads_list = []
    if STEP == 'stats':
        if VERIF_CASE in ['precip', 'snowfall']:
            for v in vdates:
                leads = []
                for group in FHR_GROUP_LIST.split(' '):
                    if group == 'SHORT':
                        fhr_incr = int(FHR_INCR_SHORT)
                        fhr_end = int(FHR_END_SHORT)
                    elif group == 'FULL':
                        fhr_incr = int(FHR_INCR_FULL)
                        fhr_end = int(FHR_END_FULL)
                    else:
                        print(f"Unrecognized FHR_GROUP ({group}) ... Quitting.")
                        sys.exit(1)
                    fhr_start = cutil.get_fhr_start(v.hour, int(ACC), fhr_incr, int(MIN_IHOUR))
                    leads = np.hstack((leads,np.arange(fhr_start, fhr_end+1, fhr_incr)))
                leads_list.append(leads)
        else:
            for v in vdates:
                leads = []
                for group in FHR_GROUP_LIST.split(' '):
                    if group == 'SHORT':
                        fhr_incr = int(FHR_INCR_SHORT)
                        fhr_end = int(FHR_END_SHORT)
                    elif group == 'FULL':
                        fhr_incr = int(FHR_INCR_FULL)
                        fhr_end = int(FHR_END_FULL)
                    else:
                        print(f"Unrecognized FHR_GROUP ({group}) ... Quitting.")
                        sys.exit(1)
                    fhr_start = cutil.get_fhr_start(v.hour, 0, fhr_incr, int(MIN_IHOUR))
                    leads = np.hstack((leads,np.arange(fhr_start, fhr_end+1, fhr_incr)))
                leads_list.append(leads)
    else:
        if VERIF_CASE in ['precip', 'snowfall']:
            for v in vdates:
                leads_list.append(np.arange(1, int(FHR_END_FULL)))
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
        'Bukovsky_G240_CONUS.nc',
        'Bukovsky_G240_CONUS_East.nc',
        'Bukovsky_G240_CONUS_West.nc',
        'Bukovsky_G240_CONUS_Central.nc',
        'Bukovsky_G240_CONUS_South.nc',
        'Bukovsky_G212_CONUS.nc',
        'Bukovsky_G212_CONUS_East.nc',
        'Bukovsky_G212_CONUS_West.nc',
        'Bukovsky_G212_CONUS_Central.nc',
        'Bukovsky_G212_CONUS_South.nc'
    ]
    subreg_mask_files = [
        'Bukovsky_G218_Appalachia.nc',
        'Bukovsky_G218_CPlains.nc',
        'Bukovsky_G218_DeepSouth.nc',
        'Bukovsky_G218_GreatBasin.nc',
        'Bukovsky_G218_GreatLakes.nc',
        'Bukovsky_G218_Mezquital.nc',
        'Bukovsky_G218_MidAtlantic.nc',
        'Bukovsky_G218_NorthAtlantic.nc',
        'Bukovsky_G218_NPlains.nc',
        'Bukovsky_G218_NRockies.nc',
        'Bukovsky_G218_PacificNW.nc',
        'Bukovsky_G218_PacificSW.nc',
        'Bukovsky_G218_Prairie.nc',
        'Bukovsky_G218_Southeast.nc',
        'Bukovsky_G218_SPlains.nc',
        'Bukovsky_G218_SRockies.nc',
    ]
    ak_mask_files = [
        'Alaska_G091.nc',
        'Alaska_G216.nc',
    ]
    hi_mask_files = [
        'Hawaii_G196.nc',
    ]
    pr_mask_files = [
        'Puerto_Rico_G194.nc',
    ]
    gu_mask_files = [
        'Guam_RTMA.nc',
    ]
    if NEST == 'conus':
        mask_files = np.hstack((mask_files, conus_mask_files))
    elif NEST == 'subreg':
        mask_files = np.hstack((mask_files, subreg_mask_files))
    elif NEST == 'ak':
        mask_files = np.hstack((mask_files, ak_mask_files))
    elif NEST == 'hi':
        mask_files = np.hstack((mask_files, hi_mask_files))
    elif NEST == 'pr':
        mask_files = np.hstack((mask_files, pr_mask_files))
    elif NEST == 'gu':
        mask_files = np.hstack((mask_files, gu_mask_files))
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
        if VERIF_CASE == 'grid2obs' and NEST == 'firewx':
            fcst_templates = [
                os.path.join(
                    COMINnam, 
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.firewxnest.hiresf{FHR}.tm00.grib2'
                )
            ]
        else:
            fcst_templates = []
        if MODELNAME == 'namnest':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst, 
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.conusnest.hiresf{FHR}.tm00.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.alaskanest.hiresf{FHR}.tm00.grib2'
                ))
            elif NEST == 'hi':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.hawaiinest.hiresf{FHR}.tm00.grib2'
                ))
            elif NEST == 'pr':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.priconest.hiresf{FHR}.tm00.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'nam.{IDATE}',
                    'nam.t{IHOUR}z.conusnest.hiresf{FHR}.tm00.grib2'
                ))
        elif MODELNAME == 'hireswarw':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.conus.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.ak.grib2'
                ))
            elif NEST == 'hi':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.hi.grib2'
                ))
            elif NEST == 'pr':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.pr.grib2'
                ))
            elif NEST == 'gu':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.guam.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.conus.grib2'
                ))
        elif MODELNAME == 'hireswarwmem2':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.conusmem2.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.akmem2.grib2'
                ))
            elif NEST == 'hi':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.himem2.grib2'
                ))
            elif NEST == 'pr':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.prmem2.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.arw_5km.f{FHR}.conusmem2.grib2'
                ))
        elif MODELNAME == 'hireswfv3':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.conus.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.ak.grib2'
                ))
            elif NEST == 'hi':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.hi.grib2'
                ))
            elif NEST == 'pr':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.pr.grib2'
                ))
            elif NEST == 'gu':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.guam.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hiresw.{IDATE}',
                    'hiresw.t{IHOUR}z.fv3_5km.f{FHR}.conus.grib2'
                ))
        elif MODELNAME == 'hrrr':
            if NEST == 'conus':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'conus',
                    'hrrr.t{IHOUR}z.wrfprsf{FHR}.grib2'
                ))
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'conus',
                    'hrrr.t{IHOUR}z.wrfsfcf{FHR}.grib2'
                ))
            elif NEST == 'ak':
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'alaska',
                    'hrrr.t{IHOUR}z.wrfprsf{FHR}.ak.grib2'
                ))
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'alaska',
                    'hrrr.t{IHOUR}z.wrfsfcf{FHR}.ak.grib2'
                ))
            else:
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'conus',
                    'hrrr.t{IHOUR}z.wrfprsf{FHR}.grib2'
                ))
                fcst_templates.append(os.path.join(
                    COMINfcst,
                    'hrrr.{IDATE}',
                    'conus',
                    'hrrr.t{IHOUR}z.wrfsfcf{FHR}.grib2'
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
    
    # Print error and send an email for missing data
    if missing_fcst_paths:
        print(f"WARNING: The following forecasts were not found:")
        for missing_fcst_path in missing_fcst_paths:
            print(missing_fcst_path)
        if send_mail and str(SENDMAIL) == "YES":
            if 'MAILTO' in os.environ:
               MAILTO = os.environ['MAILTO']
            else:
               raise RuntimeError(
                  "\"MAILTO\" must be set in environment if SENDMAIL == "
                  + "\"YES\""
               )
            missing_data_flag+=1
            data_info = [
                cutil.get_data_type(fname) 
                for fname in missing_fcst_files
            ]
            fcst_names = []
            unk_names = []
            fcst_fnames = []
            unk_fnames = []
            fcst_pnames = []
            unk_pnames = []
            for i, info in enumerate(data_info):
                if info[1] == "fcst":
                    fcst_names.append(info[0])
                    fcst_fnames.append(missing_fcst_files[i])
                    fcst_pnames.append(missing_fcst_paths[i])
                elif info[1] == "unk":
                    unk_names.append(info[0])
                    unk_fnames.append(missing_fcst_files[i])
                    unk_pnames.append(missing_fcst_paths[i])
                else:
                    print(f"FATAL ERROR: Undefined data type for missing data file: {info[1]}"
                          + f"\nPlease edit the get_data_type() function in"
                          + f" USHevs/cam/cam_util.py")
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
                                + f" {len(unk_pnames)} total files)\n")
                    for pname in unk_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in unk_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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
                if len(fcst_pnames) > max_num_files:
                    DATAmsg_body1 = (f"\nMissing files are: (showing"
                                + f" {max_num_files} of"
                                + f" {len(fcst_pnames)} total files)\n")
                    for pname in fcst_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in fcst_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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

    # Print error and send an email for missing data
    if missing_anl_paths:
        print(f"WARNING: The following analyses were not found:")
        for missing_anl_path in missing_anl_paths:
            print(missing_anl_path)
        if send_mail and str(SENDMAIL) == "YES":
            if 'MAILTO' in os.environ:
               MAILTO = os.environ['MAILTO']
            else:
               raise RuntimeError(
                  "\"MAILTO\" must be set in environment if SENDMAIL == "
                  + "\"YES\""
               )
            missing_data_flag+=1
            data_info = [
                cutil.get_data_type(fname) 
                for fname in missing_anl_files
            ]
            anl_names = []
            unk_names = []
            anl_fnames = []
            unk_fnames = []
            anl_pnames = []
            unk_pnames = []
            for i, info in enumerate(data_info):
                if info[1] == "anl":
                    anl_names.append(info[0])
                    anl_fnames.append(missing_anl_files[i])
                    anl_pnames.append(missing_anl_paths[i])
                elif info[1] == "unk":
                    unk_names.append(info[0])
                    unk_fnames.append(missing_anl_files[i])
                    unk_pnames.append(missing_anl_paths[i])
                else:
                    print(f"FATAL ERROR: Undefined data type for missing data file: {info[1]}"
                          + f"\nPlease edit the get_data_type() function in"
                          + f" USHevs/cam/cam_util.py")
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
                if len(unk_pnames) > max_num_files:
                    DATAmsg_body1 = (f"\nMissing files are: (showing"
                                + f" {max_num_files} of"
                                + f" {len(unk_pnames)} total files)\n")
                    for pname in unk_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in unk_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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
                if len(anl_pnames) > max_num_files:
                    DATAmsg_body1 = (f"\nMissing files are: (showing"
                                + f" {max_num_files} of"
                                + f" {len(anl_pnames)} total files)\n")
                    for pname in anl_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in anl_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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


    # Check for missing obs data (general)
    # Make list of paths
    gen_templates = []
    if STEP == 'stats':
        if VERIF_CASE == 'precip':
            if NEST in ['conus', 'subreg']:
                gen_templates.append(os.path.join(
                    EVSINccpa, 
                    'ccpa.{VDATE}',
                    'ccpa.t{VHOUR}z.01h.hrap.conus.gb2'
                ))
            elif NEST in ['ak', 'pr', 'hi']:
                gen_templates.append(os.path.join(
                    EVSINmrms, 
                    'mrms.{VDATE}',
                    'mrms.t{VHOUR}z.01h.'+NEST+'.gb2'
                ))
        elif VERIF_CASE == 'snowfall':
            gen_templates.append(os.path.join(
                DCOMINsnow,
                '{VDATE}',
                'wgrbbul',
                'nohrsc_snowfall',
                (
                    'sfav2_CONUS_'+str(int(OBS_ACC)).zfill(1)
                    +'h_{VDATE}{VHOUR}_grid184.grb2'
                )
            ))
        elif VERIF_CASE == 'grid2obs':
            pass
    elif STEP == 'prep':
        if VERIF_CASE == 'precip':
            if NEST in ['conus', 'subreg']:
                gen_templates.append(os.path.join(
                    COMINccpa,
                    'ccpa.{VDATE}',
                    'ccpa.t{VHOUR}z.01h.hrap.conus.gb2'
                ))
            elif NEST == 'ak':
                gen_templates.append(os.path.join(
                    DCOMINmrms,
                    'alaska',
                    'MultiSensorQPE',
                    (
                        'MultiSensor_QPE_01H_Pass2_00.00_'
                        + f'{VDATE}-{VHOUR}0000.grib2.gz'
                    )
                ))
            elif NEST == 'pr':
                gen_templates.append(os.path.join(
                    DCOMINmrms,
                    'carib',
                    'MultiSensorQPE',
                    (
                        'MultiSensor_QPE_01H_Pass2_00.00_'
                        + f'{VDATE}-{VHOUR}0000.grib2.gz'
                    )
                ))
            elif NEST == 'hi':
                gen_templates.append(os.path.join(
                    DCOMINmrms,
                    'hawaii',
                    'MultiSensorQPE',
                    (
                        'MultiSensor_QPE_01H_Pass2_00.00_'
                        + f'{VDATE}-{VHOUR}0000.grib2.gz'
                    )
                ))
            elif NEST == 'gu':
                gen_templates.append(os.path.join(
                    DCOMINmrms,
                    'guam',
                    'MultiSensorQPE',
                    (
                        'MultiSensor_QPE_01H_Pass2_00.00_'
                        + f'{VDATE}-{VHOUR}0000.grib2.gz'
                    )
                ))
    gen_paths = []
    for vdate in vdates:
        for template in gen_templates:
            gen_paths.append(fname_constructor(
                    template, VDATE=vdate.strftime('%Y%m%d'), VHOUR=vdate.strftime('%H')
            ))
    gen_paths = np.unique(gen_paths)
    
    # Record paths that don't exist
    missing_gen_files = []
    missing_gen_paths = []
    for gen_path in gen_paths:
        if not os.path.exists(gen_path):
            missing_gen_files.append(os.path.split(gen_path)[-1])
            missing_gen_paths.append(gen_path)

    # Print error and send an email for missing data
    if missing_gen_paths:
        print(f"WARNING: The following input data were not found:")
        for missing_gen_path in missing_gen_paths:
            print(missing_gen_path)
        if send_mail and str(SENDMAIL) == "YES":
            if 'MAILTO' in os.environ:
               MAILTO = os.environ['MAILTO']
            else:
               raise RuntimeError(
                  "\"MAILTO\" must be set in environment if SENDMAIL == "
                  + "\"YES\""
               )
            missing_data_flag+=1
            data_info = [
                cutil.get_data_type(fname) 
                for fname in missing_gen_files
            ]
            gen_names = []
            unk_names = []
            gen_fnames = []
            unk_fnames = []
            gen_pnames = []
            unk_pnames = []
            for i, info in enumerate(data_info):
                if info[1] == "gen":
                    gen_names.append(info[0])
                    gen_fnames.append(missing_gen_files[i])
                    gen_pnames.append(missing_gen_paths[i])
                elif info[1] == "unk":
                    unk_names.append(info[0])
                    unk_fnames.append(missing_gen_files[i])
                    unk_pnames.append(missing_gen_paths[i])
                else:
                    print(f"FATAL ERROR: Undefined data type for missing data file: {info[1]}"
                          + f"\nPlease edit the get_data_type() function in"
                          + f" USHevs/cam/cam_util.py")
                    sys.exit(1)
            gen_names = np.unique(gen_names)
            unk_names = np.unique(unk_names)
            if unk_names.size > 0:
                if len(unk_names) == 1:
                    DATAsubj = "Unrecognized"
                else:
                    DATAsubj = ', '.join(unk_names)
                subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                DATAmsg_head = (f"Warning: Some unrecognized data were unavailable"
                                + f" for valid date {VDATE} at {VHOUR}Z.")
                if len(unk_pnames) > max_num_files:
                    DATAmsg_body1 = (f"\nMissing files are: (showing"
                                + f" {max_num_files} of"
                                + f" {len(unk_pnames)} total files)\n")
                    for pname in unk_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in unk_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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
            if gen_names.size > 0:
                if len(gen_names) == 1:
                    DATAsubj = gen_names[0]
                else:
                    DATAsubj = ', '.join(gen_names)
                subject = f"{DATAsubj} Data Missing for EVS {COMPONENT}"
                DATAmsg_head = (f"Warning: No {DATAsubj} data were available"
                                + f" for valid date {VDATE} at {VHOUR}Z.")
                if len(gen_pnames) > max_num_files:
                    DATAmsg_body1 = (f"\nMissing files are: (showing"
                                + f" {max_num_files} of"
                                + f" {len(gen_pnames)} total files)\n")
                    for pname in gen_pnames[:max_num_files]:
                        DATAmsg_body1+=f"{pname}\n"
                else:
                    DATAmsg_body1 = (f"Missing files are:\n")
                    for pname in gen_pnames:
                        DATAmsg_body1+=f"{pname}\n"
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


    # If missing data, exit with 0 code 
    if missing_data_flag:
        sys.exit(0)

print(f"END: {os.path.basename(__file__)}")
