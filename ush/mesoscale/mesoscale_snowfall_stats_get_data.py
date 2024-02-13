#!/usr/bin/env python3
'''
Name: mesoscale_snowfall_stats_get_data.py
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
COMINnohrsc = os.environ['DCOMINnohrsc']
COMOUT = os.environ['COMOUT']
COMINmodel_file_template = os.environ['MODEL_INPUT_TEMPLATE']
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
    accum_list = ['06']
    if int(VHOUR) == 0 or int(VHOUR) == 12:
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
        DATAmodel_file_template = os.path.join(
            DATAmodel, MODELNAME+'.init{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
        )
        for fhr in fhrs:
            init_dt = valid_dt - datetime.timedelta(hours=fhr)
            if f"{init_dt:%H}" in CYC_LIST:
                if MODELNAME == 'rap' \
                        and f"{init_dt:%H}" not in ['03','09','15','21'] \
                        and fhr > 21:
                    continue
                model_file_pairs_for_accum_list = []
                # Assuming continuous buckets present 
                COMINmodel_file = m_util.format_filler(
                    COMINmodel_file_template, valid_dt, init_dt, str(fhr), {}
                )
                DATAmodel_file = m_util.format_filler(
                    DATAmodel_file_template, valid_dt, init_dt, str(fhr), {}
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
                                        DATA, f"mail_{MODELNAME}_"
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
        # OBS: Get NOHRSC
        DATAnohrsc = os.path.join(DATA, 'data', 'nohrsc')
        if not os.path.exists(DATAnohrsc):
            os.makedirs(DATAnohrsc)
            print(f"Making directory {DATAnohrsc}")
        print(f"\nGetting NOHRSC files for accumulation {accum}hr valid "
              +f"{accum_start_dt:%Y%m%d %H}Z to {accum_end_dt:%Y%m%d %H}Z")
        COMINnohrsc_file = os.path.join(
            COMINnohrsc, f"{valid_dt:%Y%m%d}", 'wgrbbul', 'nohrsc_snowfall',
            f"sfav2_CONUS_{accum.replace('0','')}h_{valid_dt:%Y%m%d%H}_"
            +'grid184.grb2'
        )
        DATAnohrsc_file = os.path.join(
            DATAnohrsc, f"nohrsc.accum{accum}hr."
            +f"v{valid_dt:%Y%m%d%H}"
        )
        if m_util.check_file(COMINnohrsc_file):
            print(f"Linking {COMINnohrsc_file} to {DATAnohrsc_file}")
            os.symlink(COMINnohrsc_file, DATAnohrsc_file)
        else:
            print(f"WARNING: MISSING or ZERO SIZE: {COMINnohrsc_file}")
            if SENDMAIL == "YES":
                mail_COMINnohrsc_file = os.path.join(
                        DATA, f"mail_nohrsc_accum{accum}hr_"
                        +f"valid{valid_dt:%Y%m%d%H}.sh"
                )
                print(f"WARNING: MISSING or ZERO SIZE: {COMINnohrsc_file}")
                print(f"Mail File: {mail_COMINnohrsc_file}")
                if not os.path.exists(mail_COMINnohrsc_file):
                    mailmsg = open(mail_COMINnohrsc_file, 'w')
                    mailmsg.write('#!/bin/bash\n')
                    mailmsg.write('set -x\n\n')
                    mailmsg.write(
                            'export subject="NOHRSC Accum '+accum+'hr '
                            +'Data Missing for EVS '+COMPONENT+'"\n'
                    )
                    mailmsg.write(
                            "export MAILTO=${MAILTO:-'"
                            +USER.lower()+"@noaa.gov'}\n"
                    )
                    mailmsg.write(
                            'echo "WARNING: No NOHRSC accumulation '
                            +accum+' hour data was available for '
                            +f'valid date {valid_dt:%Y%m%d%H}" '
                            +'> mailmsg\n'
                    )
                    mailmsg.write(
                            'echo "Missing file is '+COMINnohrsc_file
                            +'" >> mailmsg\n'
                    )
                    mailmsg.write(
                            'echo "Job ID: '+jobid+'" >> mailmsg\n'
                    )
                    mailmsg.write('cat mailmsg | '+mail_cmd+'\n')
                    mailmsg.write('exit 0')
                    mailmsg.close()
                    os.chmod(mail_COMINnohrsc_file, 0o755)

print(f"END: {os.path.basename(__file__)}")
