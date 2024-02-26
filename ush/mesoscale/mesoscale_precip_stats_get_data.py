#!/usr/bin/env python3
'''
Name: mesoscale_precip_get_data.py
Contact(s): Mallory Row, Roshan Shrestha
Abstract: This gather model and observation data files
'''

import os
import datetime
import shutil
import mesoscale_util as m_util

print(f"BEGIN: {os.path.basename(__file__)}")

cwd = os.getcwd()
print(f"Working in: {cwd}")

# Read in common environment variables
DATA = os.environ['DATA']
MODELNAME = os.environ['MODELNAME']
EVSINccpa = os.environ['COMINccpa']
EVSINmrms = os.environ['DCOMINmrms']
COMOUT = os.environ['COMOUT']
VDATE = os.environ['VDATE']
VHOUR_LIST = os.environ['VHOUR_LIST'].split(' ')
CYC_LIST = os.environ['CYC_LIST'].split(' ')
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
USER = os.environ['USER']
jobid = os.environ['jobid']
SENDMAIL = os.environ['SENDMAIL']

# mail_cmd = 'mail.py -s "$subject" $MAILTO -v'
mail_cmd = 'mail -s "$subject" $MAILTO'

for VHOUR in VHOUR_LIST:
    # What accumulations stats will be run for
    accum_list = ['01']
    if int(VHOUR) % 3 == 0:
        accum_list.append('03')
    if int(VHOUR) == 12:
        accum_list.append('24')
    for accum in accum_list:
        accum_end_dt = datetime.datetime.strptime(VDATE+VHOUR, '%Y%m%d%H')
        accum_start_dt = accum_end_dt - datetime.timedelta(hours=int(accum))
        valid_dt = accum_end_dt
        # MODEL
        DATAmodel = os.path.join(DATA, 'data', MODELNAME)
        if not os.path.exists(DATAmodel):
            os.makedirs(DATAmodel)
            print(f"Making directory {DATAmodel}")
        fhr_start = os.environ[f"ACCUM{accum}_FHR_START"]
        fhr_end = os.environ[f"ACCUM{accum}_FHR_END"]
        fhr_incr = os.environ[f"ACCUM{accum}_FHR_INCR"]
        print(f"\nGetting {MODELNAME} files for accumulation {accum}hr valid "
              +f"{accum_start_dt:%Y%m%d %H}Z to {accum_end_dt:%Y%m%d %H}Z")
        fhrs = range(int(fhr_start), int(fhr_end)+int(fhr_incr), int(fhr_incr))
        area_list = ['CONUS', 'ALASKA']
        if accum == '24':
            area_list.append('HAWAII')
            area_list.append('PUERTO_RICO')
        for area in area_list:
            COMINmodel_file_template = os.environ[f"{area}_MODEL_INPUT_TEMPLATE"]
            DATAmodel_file_template = os.path.join(
                DATAmodel, MODELNAME+'.'+area.lower()+'.init{init?fmt=%Y%m%d%H}.'
                +'f{lead?fmt=%3H}'
            )
            for fhr in fhrs:
                init_dt = valid_dt - datetime.timedelta(hours=fhr)
                if f"{init_dt:%H}" in CYC_LIST:
                    if MODELNAME == 'rap' \
                            and f"{init_dt:%H}" not in ['03','09','15','21'] \
                            and fhr > 21:
                        continue
                    model_file_pairs_for_accum_list = []
                    if MODELNAME == 'nam':
                        if accum == '01':
                            COMINmodel_file = m_util.format_filler(
                                COMINmodel_file_template, valid_dt, init_dt,
                                str(fhr), {}
                            )
                            DATAmodel_file = m_util.format_filler(
                                DATAmodel_file_template, valid_dt, init_dt,
                                str(fhr), {}
                            )
                            model_file_pairs_for_accum_list.append(
                                (COMINmodel_file, DATAmodel_file)
                            )
                            if f"{init_dt:%H}" in ['00', '12']:
                                precip_bucket = 12
                            else:
                                precip_bucket = 3
                            if fhr % precip_bucket != 1 and fhr-1 >=0:
                                COMINmodel_file = m_util.format_filler(
                                    COMINmodel_file_template, valid_dt,
                                    init_dt, str(fhr-1), {}
                                )
                                DATAmodel_file = m_util.format_filler(
                                    DATAmodel_file_template, valid_dt, init_dt,
                                    str(fhr-1), {}
                                )
                                model_file_pairs_for_accum_list.append(
                                    (COMINmodel_file, DATAmodel_file)
                                )  
                        else:
                            nfiles_in_accum = int(accum)/3
                            nfile = 1
                            while nfile <= nfiles_in_accum:
                                nfile_fhr = fhr - ((nfile-1)*3)
                                if nfile_fhr >= 0:
                                    COMINmodel_file = m_util.format_filler(
                                        COMINmodel_file_template, valid_dt,
                                        init_dt, str(nfile_fhr), {}
                                    )
                                    DATAmodel_file = m_util.format_filler(
                                        DATAmodel_file_template, valid_dt, init_dt,
                                        str(nfile_fhr), {}
                                    )
                                    model_file_pairs_for_accum_list.append(
                                        (COMINmodel_file, DATAmodel_file)
                                    )
                                nfile+=1
                    else:
                        # Assuming continuous precip buckets
                        COMINmodel_file = m_util.format_filler(
                            COMINmodel_file_template, valid_dt, init_dt,
                            str(fhr), {}
                        )
                        DATAmodel_file = m_util.format_filler(
                            DATAmodel_file_template, valid_dt, init_dt,
                            str(fhr), {}
                        )
                        model_file_pairs_for_accum_list.append(
                            (COMINmodel_file, DATAmodel_file)
                        )
                        if fhr - int(accum) >= 0:
                            COMINmodel_file = m_util.format_filler(
                                COMINmodel_file_template, valid_dt, init_dt,
                                str(fhr - int(accum)), {}
                            )
                            DATAmodel_file = m_util.format_filler(
                                DATAmodel_file_template, valid_dt, init_dt,
                                str(fhr - int(accum)), {}
                            )
                            model_file_pairs_for_accum_list.append(
                                (COMINmodel_file, DATAmodel_file)
                            )
                    for model_file_pair in model_file_pairs_for_accum_list:
                        COMINmodel_file = model_file_pair[0]
                        DATAmodel_file = model_file_pair[1]
                        if not os.path.exists(DATAmodel_file):
                            if m_util.check_file(COMINmodel_file):
                                print(f"Linking {COMINmodel_file} to "
                                      +f"{DATAmodel_file}")
                                os.symlink(COMINmodel_file, DATAmodel_file)
                            else:
                                print("WARNING: MISSING or ZERO SIZE: "
                                      +f"{COMINmodel_file}")
                                if SENDMAIL == "YES":
                                    mail_COMINmodel_file = os.path.join(
                                            DATA, f"mail_{MODELNAME}_{area.lower()}_"
                                            +f"init{init_dt:%Y%m%d%H}_"
                                            +f"{str(fhr).zfill(3)}.sh"
                                    )
                                    print("WARNING: MISSING or ZERO SIZE: "
                                          +f"{COMINmodel_file}")
                                    print("Mail File: "
                                          +f"{mail_COMINmodel_file}")
                                    if not os.path.exists(mail_COMINmodel_file):
                                        mailmsg = open(mail_COMINmodel_file, 'w')
                                        mailmsg.write('#!/bin/bash\n')
                                        mailmsg.write('set -x\n\n')
                                        mailmsg.write(
                                                'export subject="F'+str(fhr).zfill(3)
                                                +' '+MODELNAME.upper()+' Forecast '
                                                +'Data Missing for EVS '+COMPONENT
                                                +'"\n'
                                        )
                                        mailmsg.write(
                                                "export MAILTO=${MAILTO:-'"
                                                +USER.lower()+"@noaa.gov'}\n"
                                        )
                                        mailmsg.write(
                                                'echo "WARNING: No '+MODELNAME.upper()
                                                +' was available for '
                                                +f'{init_dt:%Y%m%d%H}f'
                                                +f'{str(fhr).zfill(3)}" > mailmsg\n'
                                        )
                                        mailmsg.write(
                                                'echo "Missing file is '
                                                +COMINmodel_file+'" >> mailmsg\n'
                                        )
                                        mailmsg.write(
                                                'echo "Job ID: '+jobid+'" >> mailmsg\n'
                                        )
                                        mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                                        mailmsg.write('exit 0')
                                        mailmsg.close()
                                        os.chmod(mail_COMINmodel_file, 0o755)
        # OBS: Get CCPA files -- CONUS
        DATAccpa = os.path.join(DATA, 'data', 'ccpa')
        if not os.path.exists(DATAccpa):
            os.makedirs(DATAccpa)
            print(f"Making directory {DATAccpa}")
        print(f"\nGetting CCPA files for accumulation {accum}hr valid "
              +f"{accum_start_dt:%Y%m%d %H}Z to {accum_end_dt:%Y%m%d %H}Z")
        if accum == '24':
            ccpa_file_dt_in_accum_list = [
                accum_end_dt,
                accum_end_dt - datetime.timedelta(hours=6),
                accum_end_dt - datetime.timedelta(hours=12),
                accum_end_dt - datetime.timedelta(hours=18)
            ]
            ccpa_file_accum = '06'
        else:
            ccpa_file_dt_in_accum_list = [
                accum_end_dt
            ]
            ccpa_file_accum = accum
        for ccpa_file_dt_in_accum in ccpa_file_dt_in_accum_list:
            ccpa_file_HH = int(f"{ccpa_file_dt_in_accum:%H}")
            ccpa_file_YYYYmmdd = f"{ccpa_file_dt_in_accum:%Y%m%d}"
            if ccpa_file_HH > 0 and ccpa_file_HH <= 6:
                EVSINccpa_file_dir = os.path.join(
                    EVSINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '06'
                )
            elif ccpa_file_HH > 6 and ccpa_file_HH <= 12:
                EVSINccpa_file_dir = os.path.join(
                    EVSINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '12'
                )
            elif ccpa_file_HH > 12 and ccpa_file_HH <= 18:
                EVSINccpa_file_dir = os.path.join(
                    EVSINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '18'
                )
            elif ccpa_file_HH == 0:
                EVSINccpa_file_dir = os.path.join(
                    EVSINccpa, f"ccpa.{ccpa_file_YYYYmmdd}", '00'
                )
            else:
                EVSINccpa_file_dir = os.path.join(
                    EVSINccpa, 'ccpa.'+((ccpa_file_dt_in_accum
                                      +datetime.timedelta(days=1))\
                                      .strftime('%Y%m%d')),  '00'
                )
            EVSINccpa_file = os.path.join(
                EVSINccpa_file_dir,
                f"ccpa.t{str(ccpa_file_HH).zfill(2)}z."
                +f"{ccpa_file_accum}h.hrap.conus.gb2"
            )
            DATAccpa_file = os.path.join(
                DATAccpa, f"ccpa.accum{ccpa_file_accum}hr."
                +f"v{ccpa_file_dt_in_accum:%Y%m%d%H}"
            )
            if m_util.check_file(EVSINccpa_file):
                print(f"Linking {EVSINccpa_file} to {DATAccpa_file}")
                os.symlink(EVSINccpa_file, DATAccpa_file)
            else:
                print(f"WARNING: MISSING or ZERO SIZE: {EVSINccpa_file}")
                if SENDMAIL == "YES":
                    mail_EVSINccpa_file = os.path.join(
                            DATA, f"mail_ccpa_accum{ccpa_file_accum}hr_"
                            +f"valid{ccpa_file_dt_in_accum:%Y%m%d%H}.sh"
                    )
                    print(f"WARNING: MISSING or ZERO SIZE: {EVSINccpa_file}")
                    print(f"Mail File: {mail_EVSINccpa_file}")
                    if not os.path.exists(mail_EVSINccpa_file):
                        mailmsg = open(mail_EVSINccpa_file, 'w')
                        mailmsg.write('#!/bin/bash\n')
                        mailmsg.write('set -x\n\n')
                        mailmsg.write(
                                'export subject="CCPA Accum '+ccpa_file_accum+'hr '
                                +'Data Missing for EVS '+COMPONENT+'"\n'
                        )
                        mailmsg.write(
                                "export MAILTO=${MAILTO:-'"
                                +USER.lower()+"@noaa.gov'}\n"
                        )
                        mailmsg.write(
                                'echo "WARNING: No CCPA accumulation '
                                +ccpa_file_accum+' hour data was available for '
                                +f'valid date {ccpa_file_dt_in_accum:%Y%m%d%H}" '
                                +'> mailmsg\n'
                        )
                        mailmsg.write(
                                'echo "Missing file is '+EVSINccpa_file
                                +'" >> mailmsg\n'
                        )
                        mailmsg.write(
                                'echo "Job ID: '+jobid+'" >> mailmsg\n'
                        )
                        mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                        mailmsg.write('exit 0')
                        mailmsg.close()
                        os.chmod(mail_EVSINccpa_file, 0o755)
        # OBS: Get MRMSE files -- Alaska
        DATAmrms = os.path.join(DATA, 'data', 'mrms')
        if not os.path.exists(DATAmrms):
            os.makedirs(DATAmrms)
            print(f"Making directory {DATAmrms}")
        mrms_area_list = []
        if os.environ['CONUS_VERIF_SOURCE'] == 'mrms':
            mrms_area_list.append('conus')
        if os.environ['ALASKA_VERIF_SOURCE'] == 'mrms':
            mrms_area_list.append('alaska')
        for mrms_area in mrms_area_list:
            print(f"\nGetting MRMS files for accumulation {accum}hr valid "
                  +f"{accum_start_dt:%Y%m%d %H} to {accum_end_dt:%Y%m%d %H}Z "
                  +f"over {mrms_area.title()}")
            EVSINmrms_area = os.path.join(EVSINmrms, mrms_area, 'MultiSensorQPE')
            EVSINmrms_gzfile = os.path.join(
                EVSINmrms, mrms_area, 'MultiSensorQPE',
                 f"MultiSensor_QPE_{accum}H_Pass2_00.00_"
                +f"{accum_end_dt:%Y%m%d}-{accum_end_dt:%H}0000.grib2.gz"
            )
            if m_util.check_file(EVSINmrms_gzfile):
                DATAmrms_gzfile = os.path.join(
                    DATAmrms, EVSINmrms_gzfile.rpartition('/')[2]
                )
                print(f"Copying {EVSINmrms_gzfile} to "
                      +f"{DATAmrms_gzfile}")
                shutil.copy2(EVSINmrms_gzfile, DATAmrms_gzfile)
                print(f"Unzipping {DATAmrms_gzfile}")
                os.system(f"gunzip {DATAmrms_gzfile}")
                DATAmrms_file = os.path.join(
                    DATAmrms, f"{mrms_area}_"
                    +(DATAmrms_gzfile.rpartition('/')[2]\
                      .replace('.gz', ''))
                )
                print("Moving "
                      +f"{DATAmrms_gzfile.replace('.gz', '')} "
                      +f"to {DATAmrms_file}")
                os.system("mv "
                         +f"{DATAmrms_gzfile.replace('.gz', '')} "
                         +f"{DATAmrms_file}")
            else:
                print(f"WARNING: MISSING or ZERO SIZE: {EVSINmrms_gzfile}")
                if SENDMAIL == "YES":
                    mail_EVSINmrms_file = os.path.join(
                            DATA, f"mail_mrms_accum{accum}hr_{mrms_area}_"
                            +f"valid{accum_end_dt:%Y%m%d%H}.sh"
                    )
                    print(f"WARNING: MISSING or ZERO SIZE: {EVSINmrms_gzfile}")
                    print(f"Mail File: {mail_EVSINmrms_file}")
                    if not os.path.exists(mail_EVSINmrms_file):
                        mailmsg = open(mail_EVSINmrms_file, 'w')
                        mailmsg.write('#!/bin/bash\n')
                        mailmsg.write('set -x\n\n')
                        mailmsg.write(
                                'export subject="MRMS '+mrms_area.title()+' Accum '
                                +accum+'hr Data Missing for EVS '
                                +COMPONENT+'"\n'
                        )
                        mailmsg.write(
                                "export MAILTO=${MAILTO:-'"
                                +USER.lower()+"@noaa.gov'}\n"
                        )
                        mailmsg.write(
                                'echo "WARNING: No MRMS '+mrms_area.title()+' '
                                +'accumulation '+accum+' hour data was available '
                                +f'for valid date {accum_end_dt:%Y%m%d%H}" '
                                +'> mailmsg\n'
                        )
                        mailmsg.write(
                                'echo "Missing file is '+EVSINmrms_gzfile
                                +'" >> mailmsg\n'
                        )
                        mailmsg.write(
                                'echo "Job ID: '+jobid+'" >> mailmsg\n'
                        )
                        mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                        mailmsg.write('exit 0')
                        mailmsg.close()
                        os.chmod(mail_EVSINmrms_file, 0o755)

print(f"END: {os.path.basename(__file__)}")
