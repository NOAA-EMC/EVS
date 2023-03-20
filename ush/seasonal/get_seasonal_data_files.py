'''
Program Name: get_seasonal_data_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This gets the necessary data files to run
          the METplus use case.
'''

import os
import subprocess
import datetime
from time import sleep
import pandas as pd
import glob
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

def get_time_info(start_date_str, end_date_str,
                  start_hr_str, end_hr_str, hr_inc_str,
                  fhr_list, date_type):
    """! This creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             start_date_str - string of the verification start
                              date
             end_date_str   - string of the verification end
                              date
             start_hr_str   - string of the verification start
                              hour
             end_hr_str     - string of the verification end
                              hour
             hr_inc_str     - string of the increment between
                              start_hr and end_hr
             fhr_list       - list of strings of the forecast
                              hours to verify
             date_type      - string defining by what type
                              date and times to create METplus
                              data

         Returns:
             time_info - list of dictionaries with the valid,
                         initialization, and forecast hour
                         pairings
    """
    sdate = datetime.datetime(int(start_date_str[0:4]),
                              int(start_date_str[4:6]),
                              int(start_date_str[6:]),
                              int(start_hr_str))
    edate = datetime.datetime(int(end_date_str[0:4]),
                              int(end_date_str[4:6]),
                              int(end_date_str[6:]),
                              int(end_hr_str))
    date_inc = datetime.timedelta(seconds=int(hr_inc_str))
    time_info = []
    date = sdate
    while date <= edate:
        if date_type == 'VALID':
            valid_time = date
        elif date_type == 'INIT':
            init_time = date
        for fhr in fhr_list:
            if fhr == 'anl':
                lead = '0'
            else:
                lead = fhr
            if date_type == 'VALID':
                init_time = valid_time - datetime.timedelta(hours=int(lead))
            elif date_type == 'INIT':
                valid_time = init_time + datetime.timedelta(hours=int(lead))
            t = {}
            t['valid_time'] = valid_time
            t['init_time'] = init_time
            t['lead'] = lead
            time_info.append(t)
        date = date + date_inc
    return time_info

def format_filler(unfilled_file_format, dt_valid_time, dt_init_time, str_lead):
    """! This creates a list of objects containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             unfilled_file_format   - string of file naming convention
             dt_valid_time          - datetime object of the valid time
             dt_init_time           - datetime object of the
                                      initialization time
             str_lead               - string of the forecast lead

         Returns:
             filled_file_format - string of file_format
                                  filled in with verifying
                                  time information
    """
    filled_file_format = ''
    format_opt_list = ['lead', 'valid', 'init', 'cycle']
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   format_opt_count_fmt = (
                       filled_file_format_chunk \
                       .partition('{'+format_opt+'?fmt=')[2] \
                       .partition('}')[0]
                   )
                   if format_opt == 'valid':
                       replace_format_opt_count = dt_valid_time.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(str_lead) < 10:
                               replace_format_opt_count = str_lead[1]
                           else:
                               replace_format_opt_count = str_lead
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = str_lead.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = str_lead.zfill(3)
                       else:
                           replace_format_opt_count = str_lead
                   elif format_opt in ['init', 'cycle']:
                       replace_format_opt_count = dt_init_time.strftime(
                           format_opt_count_fmt
                       )
                   filled_file_format_chunk = (
                       filled_file_format_chunk.replace(
                           '{'+format_opt+'?fmt='
                           +format_opt_count_fmt+'}',
                           replace_format_opt_count
                       )
                   )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format

def set_up_cfs_hpss_info(dt_init_time, dt_valid_time, hpss_dir, model_dump,
                         hpss_file_suffix, save_data_dir):
    """! This sets up HPSS and job information specifically
         for getting CFS data from HPSS.

         Args:
             dt_init_time      - datetime object of the
                                 initialization time
             dt_valid_time     - datetime object of the
                                 valid time
             hpss_dir          - string of the base HPSS
                                 directory path
             model_dump        - string of model dump
                                 the beginning of the HPSS
                                 file
                                 (cfs, gfs)
             hpss_file_suffix  - string of information
                                 on the end of the HPSS
                                 file
             save_data_dir     - string of the path to the
                                 directory where the HPSS
                                 retrieved file will be
                                 saved

         Returns:
             hpss_tar          - string of the tar file
                                 path where hpss_file
                                 is located
             hpss_file         - string of the file name
                                 to be retrieved from HPSS
             hpss_job_filename - string of the path of the
                                 HPSS job card name
    """
    # Read in environment variables
    HTAR = os.environ['HTAR']
    # Set date variables
    vYYYYmmddHH = dt_valid_time.strftime('%Y%m%d%H')
    YYYYmmddHH = dt_init_time.strftime('%Y%m%d%H')
    YYYYmmdd = dt_init_time.strftime('%Y%m%d')
    YYYYmm = dt_init_time.strftime('%Y%m')
    YYYY = dt_init_time.strftime('%Y')
    mm = dt_init_time.strftime('%m')
    dd = dt_init_time.strftime('%d')
    HH = dt_init_time.strftime('%H')
    if 'NCEPPROD' in hpss_dir:
        # Operational CFS and GFS HPSS archive set up
        hpss_tar_filename_prefix = (model_dump+'.pgbf.'
                                    +YYYYmmddHH+'.m'+mb)
        hpss_file_prefix = os.path.join('pgbf.'+mb+'.'
                                        +YYYYmmddHH+'.'+vYYYYmm+'.')
        hpss_tar_filenameanl_prefix = ('com_gfs_prod_'+model_dump+'.'
                                       +YYYYmmdd+'_'+HH+'.gfs')
        hpss_fileanl_prefix = os.path.join('atmos', model_dump+'.'+YYYYmmdd,
                                           HH, model_dump+'.t'+HH+'z.')
        # cfs grib2 files
        if model_dump == 'cfs' and hpss_file_suffix[0] == 'grb2':
            hpss_file = hpss_file_prefix+'avrg.grib.'+hpss_file_suffix
            hpss_tar_filename = hpss_tar_filename_prefix+'.monthly.tar'
        # gfs grib2 files
        if model_dump == 'gfs' and hpss_file_suffix == 'anl':
            hpss_file = hpss_fileanl_prefix+'pgrb2.0p50.'+hpss_file_suffix
            hpss_tar_filename = hpss_tar_filenameanl_prefix+'_pgrb2.tar'    
        # gdas prepbufr file
        if model_dump == 'gdas' and hpss_file_suffix == 'prepbufr':
            hpss_tar_filename = hpss_tar_filename_prefix+'.tar'
            hpss_file = hpss_file_prefix+hpss_file_suffix
        hpss_tar = os.path.join(hpss_dir, 'cfs'+YYYY, YYYYmm, YYYYmmdd,
                                'monthly', hpss_tar_filename)
        #hpss_tar = os.path.join(hpss_dir, 'rh'+YYYY, YYYYmm, YYYYmmdd,
                                #hpss_tar_filename)
    else:
        # Set up tar file
        if model_dump == 'gfs':
            hpss_tar_filename = model_dump+'a.tar'
        else:
            hpss_tar_filename = model_dump+'.tar'
        hpss_tar = os.path.join(hpss_dir, YYYYmmddHH, hpss_tar_filename)
        # Set up file
        if hpss_file_suffix == 'cyclone.trackatcfunix':
            hpss_file = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                     'atmos', 'avno.t'+HH+'z.'
                                     +hpss_file_suffix)
        elif model_dump == 'enkfgdas':
            hpss_file = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                     'atmos', 'gdas.t'+HH+'z.'
                                     +hpss_file_suffix)
        else:
            hpss_file = os.path.join(model_dump+'.'+YYYYmmdd, HH,
                                     'atmos', model_dump+'.t'+HH
                                     +'z.pgrb2.0p25.'+hpss_file_suffix)
    # Set up job file name
    hpss_job_filename = os.path.join(save_data_dir, 'HPSS_jobs',
                                     'HPSS_'+hpss_tar.rpartition('/')[2]
                                     +'_'+hpss_file.replace('/', '_')+'.sh')
    return hpss_tar, hpss_file, hpss_job_filename

def get_hpss_data(hpss_job_filename, save_data_dir, save_data_file,
                  hpss_tar, hpss_file):
    """! This creates a job card with the necessary information
         to retrieve a file from HPSS. It then submits this
         job card to the transfer queue and the designating
         wall time.

         Args:
             hpss_job_filename - string of the path of the
                                 HPSS job card name
             save_data_dir     - string of the path to the
                                 directory where the HPSS
                                 retrieved file will be
                                 saved
             save_data_file    - string of the file name
                                 the HPSS retrieved file
                                 will be saved as
             hpss_tar          - string of the tar file
                                 path where hpss_file
                                 is located
             hpss_file         - string of the file name
                                 to be retrieved from HPSS

         Returns:
    """
    # Read in environment variables
    HTAR = os.environ['HTAR']
    hpss_walltime = os.environ['hpss_walltime']
    machine = os.environ['machine']
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    # Set up job wall time information
    walltime_seconds = (
        datetime.timedelta(minutes=int(hpss_walltime)).total_seconds()
    )
    walltime = (datetime.datetime.min
                + datetime.timedelta(minutes=int(hpss_walltime))).time()
    if os.path.exists(hpss_job_filename):
        os.remove(hpss_job_filename)
    # Create job card
    with open(hpss_job_filename, 'a') as hpss_job_file:
        hpss_job_file.write('#!/bin/sh'+'\n')
        hpss_job_file.write('cd '+save_data_dir+'\n')
        hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'+hpss_file+'\n')
        if '/NCEPPROD' not in hpss_tar:
            hpss_job_file.write(HTAR+' -xf '+hpss_tar+' ./'
                                +hpss_file.replace('atmos/','')+'\n')
        if 'grb2' in hpss_file:
            cnvgrib = os.environ['CNVGRIB']
            hpss_job_file.write(cnvgrib+' -g21 '+hpss_file+' '
                                +save_data_file+' > /dev/null 2>&1\n')
            if '/NCEPPROD' not in hpss_tar:
                hpss_job_file.write(cnvgrib+' -g21 '
                                    +hpss_file.replace('atmos/','')+' '
                                    +save_data_file+' > /dev/null 2>&1\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
        elif 'trackatcfunix' in hpss_file:
            hpss_job_file.write('cp '+hpss_file.split('avno')[0]+'avno* '
                                +save_data_file+'\n')
            if '/NCEPPROD' not in hpss_tar:
                hpss_job_file.write('cp '+hpss_file.replace('atmos/','') \
                                    .split('avno')[0]+'avno* '+save_data_file
                                    +'\n')
            hpss_job_file.write('rm -r '+hpss_file.split('/')[0]+'\n')
            model_atcf_abbrv = (save_data_file.split('/')[-2])[0:4].upper()
            hpss_job_file.write('sed -i s/AVNO/'+model_atcf_abbrv+'/g '
                                +save_data_file)
        else:
            if hpss_file[0:5] != 'ccpa.':
                hpss_job_file.write('cp '+hpss_file+' '+save_data_file+'\n')
                if '/NCEPPROD' not in hpss_tar:
                    hpss_job_file.write('cp '
                                        +hpss_file.replace('atmos/','')+' '
                                        +save_data_file+'\n')
                hpss_job_file.write('rm -r '+hpss_file.split('/')[0])
    # Submit job card
    os.chmod(hpss_job_filename, 0o755)
    hpss_job_output = hpss_job_filename.replace('.sh', '.out')
    if os.path.exists(hpss_job_output):
        os.remove(hpss_job_output)
    hpss_job_name = hpss_job_filename.rpartition('/')[2].replace('.sh', '')
    print("Submitting "+hpss_job_filename+" to "+QUEUESERV)
    print("Output sent to "+hpss_job_output)
    if machine == 'WCOSS_C':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+hpss_job_output+' -e '
                  +hpss_job_output+' '
                  +'-J '+hpss_job_name+' -R rusage[mem=2048] '
                  +hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'WCOSS_DELL_P3':
        os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
                  +'-P '+ACCOUNT+' -o '+hpss_job_output+' -e '
                  +hpss_job_output+' '
                  +'-J '+hpss_job_name+' -M 2048 -R "affinity[core(1)]" '
                  +hpss_job_filename)
        job_check_cmd = ('bjobs -a -u '+os.environ['USER']+' '
                         +'-noheader -J '+hpss_job_name
                         +'| grep "RUN\|PEND" | wc -l')
    elif machine == 'HERA':
        os.system('sbatch --ntasks=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --partition='+QUEUESERV+' '
                  +'--account='+ACCOUNT+' --output='+hpss_job_output+' '
                  +'--job-name='+hpss_job_name+' '+hpss_job_filename)
        job_check_cmd = ('squeue -u '+os.environ['USER']+' -n '
                         +hpss_job_name+' -t R,PD -h | wc -l')
    elif machine == 'ORION':
        print("ERROR: No HPSS access from Orion")
    if machine != 'ORION':
        sleep_counter, sleep_checker = 1, 10
        while (sleep_counter*sleep_checker) <= walltime_seconds:
            sleep(sleep_checker)
            print("Walltime checker: "+str(sleep_counter*sleep_checker)+" "
                  +"out of "+str(int(walltime_seconds))+" seconds")
            check_job = subprocess.check_output(job_check_cmd, shell=True,
                                                encoding='UTF-8')
            if check_job[0] == '0':
                break
            sleep_counter+=1

def convert_grib2_grib1(grib2_file, grib1_file):
    """! This converts GRIB2 data to GRIB1

         Args:
             grib2_file - string of the path to
                          the GRIB2 file to
                          convert
             grib1_file - string of the path to
                          save the converted GRIB1
                          file

         Returns:
    """
    print("Converting GRIB2 file "+grib2_file+" "
          +"to GRIB1 file "+grib1_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g21 '+grib2_file+' '
              +grib1_file+' > /dev/null 2>&1')

def get_model_file(valid_time_dt, init_time_dt, lead_str,
                   name, data_dir, file_format, run_hpss,
                   hpss_data_dir, link_data_dir, link_file_format):
    """! This links a model file from its archive.
         If the file does not exist locally, then retrieve
         from HPSS if requested.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             data_dir         - string of the online archive
                                for model
             file_format      - string of the file format the
                                files are saved as in the data_dir
             run_hpss         - string of whether to get missing
                                online model data (YES) or not (NO)
             hpss_data_dir    - string of the path to model data
                                on HPSS
             link_data_dir    - string of the directory to link
                                model data to
             link_file_format - string of the linked file name

         Returns:
    """
    
    grib2_file_names = ['grib2', 'grb2']
    link_filename = format_filler(link_file_format, valid_time_dt,
                                  init_time_dt, lead_str)
    link_model_file = os.path.join(link_data_dir, link_filename)
    if not os.path.exists(link_model_file):
        model_filename = format_filler(file_format, valid_time_dt,
                                       init_time_dt, lead_str)
        model_file = os.path.join(data_dir, name, model_filename)
        if os.path.exists(model_file):
            if any(g in model_file for g in grib2_file_names):
                convert_grib2_grib1(model_file, link_model_file)
            else:
                if 'track' in link_filename:
                    os.system('cp '+model_file+' '+link_model_file)
                else:
                    os.system('ln -sf '+model_file+' '+link_model_file)
        else:
            if run_hpss == 'YES':
                print("Did not find "+model_file+" online..."
                      +"going to try to get file from HPSS")
                if 'enkfgdas' in file_format:
                    model_dump = 'enkfgdas'
                elif 'gdas' in file_format:
                    model_dump = 'gdas'
                elif 'gfs' in file_format:
                    model_dump = 'gfs'
                else:
                    model_dump = name
                if lead_str != 'anl':
                   file_lead = 'f'+lead_str.zfill(3)
                else:
                   file_lead = lead_str
                if 'track' in link_file_format:
                    (model_hpss_tar, model_hpss_file,
                     model_hpss_job_filename) = set_up_gfs_hpss_info(
                         init_time_dt, hpss_data_dir, model_dump,
                         'cyclone.trackatcfunix', link_data_dir
                    )
                elif 'ensspread' in link_file_format \
                        or 'ensmean' in link_file_format:
                    if 'spread' in file_format:
                        file_type = 'spread'
                    elif 'mean' in file_format:
                        file_type = 'mean'
                    if '.nc4' in file_format:
                        nc_type = 'nc4'
                    else:
                        nc_type = 'nc'
                    (model_hpss_tar, model_hpss_file,
                     model_hpss_job_filename) = set_up_gfs_hpss_info(
                         init_time_dt, hpss_data_dir, model_dump,
                         'atm'+file_lead+'.ens'+file_type+'.'+nc_type,
                         link_data_dir
                    )
                else:
                    (model_hpss_tar, model_hpss_file,
                     model_hpss_job_filename) = set_up_cfs_hpss_info(
                         init_time_dt, valid_time_dt, hpss_data_dir, 
                         model_dump, file_lead,
                         link_data_dir
                    )
                get_hpss_data(model_hpss_job_filename, link_data_dir,
                              link_model_file, model_hpss_tar, model_hpss_file)
    if not os.path.exists(link_model_file):
        if run_hpss == 'YES':
            print("WARNING: "+model_file+" does not exist and did not find "
                  +"HPSS file "+model_hpss_file+" from "+model_hpss_tar+" or "
                  +"walltime exceeded")
        else:
            print("WARNING: "+model_file+" does not exist")

def get_model_stat_file(valid_time_dt, init_time_dt, lead_str,
                        name, stat_data_dir, gather_by, RUN_dir_name,
                        RUN_sub_dir_name, link_data_dir):
    """! This links a model .stat file from its archive.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             stat_data_dir    - string of the online archive
                                for model MET .stat files
             gather_by        - string of the file format the
                                files are saved as in the data_dir
             RUN_dir_name     - string of RUN directory name
                                in 'metplus_data' archive
             RUN_sub_dir_name - string of RUN sub-directory name
                                (under RUN_dir_name)
                                in 'metplus_data' archive
             link_data_dir    - string of the directory to link
                                model data to

         Returns:
    """
    model_stat_gather_by_RUN_dir = os.path.join(stat_data_dir, 'stats',
                                                'seasonal', name+'.'
                                                +valid_time.strftime('%Y%m%d')
                                                )
    if gather_by == 'VALID':
         model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                        name+'_atmos_'+RUN_dir_name+'_v'
                                        +valid_time.strftime('%Y%m%d')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir,
                                             name+'_atmos_'+RUN_dir_name+'_v'
                                             +valid_time.strftime('%Y%m%d')
                                             +'.stat')
    elif gather_by == 'INIT':
         model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                        name+'_atmos_'+RUN_dir_name+'_'
                                        +init_time.strftime('%Y%m%d')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir,
                                             name+'_atmos_'+RUN_dir_name+'_'
                                             +init_time.strftime('%Y%m%d')
                                             +'.stat')
    elif gather_by == 'VSDB':
         if RUN_dir_name in ['grid2grid']:
             model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                            valid_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'_valid'
                                                 +valid_time.strftime('%H')
                                                 +'.stat')
         elif RUN_dir_name in ['grid2obs', 'precip']:
             model_stat_file = os.path.join(model_stat_gather_by_RUN_dir,
                                            init_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'_init'
                                                 +init_time.strftime('%H')
                                                 +'.stat')
    if not os.path.exists(link_model_stat_file):
        if os.path.exists(model_stat_file):
            os.system('ln -sf '+model_stat_file+' '+link_model_stat_file)
        else:
            print("WARNING: "+model_stat_file+" does not exist")

# Read in common environment variables
RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
model_data_run_hpss = os.environ['model_data_run_hpss']
model_hpss_dir_list = os.environ['model_hpss_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
machine = os.environ['machine']
RUN_abbrev = os.environ['RUN_abbrev']
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Set some common variables
hpss_prod_base_dir = '/NCEPPROD/hpssprod/runhistory'
cwdplt = os.getcwd()
cwd = '/lfs/h2/emc/ptmp/Shannon.Shields/prep/seasonal/atmos'


if RUN == 'grid2grid_stats':
    # Read in RUN related environment variables
    global_archive = os.environ['global_archive']
    # Get model forecast and truth files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_truth_name = os.environ[
            RUN_abbrev_type+'_truth_name'
        ]
        RUN_abbrev_type_truth_file_format_list = os.environ[
            RUN_abbrev_type+'_truth_file_format_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, make_met_data_by
        )
        # Get forecast and truth files for each model
        for model in model_list:
            model_idx = model_list.index(model)
            model_dir = model_dir_list[model_idx]
            model_file_form = model_file_format_list[model_idx]
            model_hpss_dir = model_hpss_dir_list[model_idx]
            model_RUN_abbrev_type_truth_file_format = (
                RUN_abbrev_type_truth_file_format_list[model_idx]
            )
            #link_model_dir = os.path.join(cwd, 'data', model)
            #if not os.path.exists(link_model_dir):
                #os.makedirs(link_model_dir)
                #os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
            # Set up model RUN_type truth info
            RUN_abbrev_type_truth_name_lead = (
                RUN_abbrev_type_truth_name.split('_')[1]
            )
            if RUN_abbrev_type_truth_name in ['self_anl', 'self_f00']:
                model_RUN_abbrev_type_truth_dir = model_dir
                RUN_abbrev_type_truth_name_short = model
                model_RUN_abbrev_type_truth_hpss_dir = model_hpss_dir
            elif RUN_abbrev_type_truth_name in ['gfs_anl', 'gfs_f00']:
                model_RUN_abbrev_type_truth_dir = model_dir
                RUN_abbrev_type_truth_name_short = (
                    RUN_abbrev_type_truth_name.split('_')[0]
                )
                model_RUN_abbrev_type_truth_hpss_dir = hpss_prod_base_dir
                #if RUN_abbrev_type_truth_name \
                        #== 'gfs_'+RUN_abbrev_type_truth_name_lead \
                        #and model_RUN_abbrev_type_truth_file_format != \
                        #('pgb'+RUN_abbrev_type_truth_name_lead
                         #+'.gfs.{valid?fmt=%Y%m%d%H}'):
                    #print("WARNING: "+RUN_abbrev_type+"_truth_name set to "
                          #+"gfs_"+RUN_abbrev_type_truth_name_lead+" but "
                          #+"file format does not match expected value. "
                          #+"Using to pgb"+RUN_abbrev_type_truth_name_lead
                          #+".gfs.{valid?fmt=%Y%m%d%H}")
                    #model_RUN_abbrev_type_truth_file_format = (
                        #'pgb'+RUN_abbrev_type_truth_name_lead
                        #+'.gfs.{valid?fmt=%Y%m%d%H}'
                    #)
            if RUN_abbrev_type_truth_name_lead == 'f00':
                RUN_abbrev_type_truth_name_lead = '00'
            # Get model forecast and truth files
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    cwdm = cwd+'.{init?fmt=%Y%m%d%H}'
                    link_model_dir = os.path.join(cwdm, model)
                    if not os.path.exists(link_model_dir):
                        os.makedirs(link_model_dir)
                        os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
                    link_anl_dir = os.path.join(cwd, 'anl')
                    if not os.path.exists(link_anl_dir):
                        os.makedirs(link_anl_dir)
                        os.makedirs(os.path.join(link_anl_dir, 'HPSS_jobs'))
                    mbr = 1
                    total = 4
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        model_file_format = os.path.join(
                            model_file_form, 'monthly_grib_'+mb,
                            'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                            +'{valid?fmt=%Y%m}.avrg.grib.grb2') 
                        get_model_file(valid_time, init_time, lead,
                                       model, model_dir, model_file_format,
                                       model_data_run_hpss, model_hpss_dir,
                                       link_model_dir,
                                       'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                                       +'{valid?fmt=%Y%m}.avrg.grib.grb2')
                        del model_file_format
                        mbr = mbr+1
                        #COPYGB = os.environ['copygb']
                        #fdatao_file = os.path.join(
                            #link_model_dir, 'f'+lead+'.ens'+mb
                            #+'.'+init_time.strftime('%Y%m%d%H')
                        #)
                        #fdatac_file = os.path.join(
                            #link_model_dir, 'f'+lead+'.ens'+mb
                            #+'.'+init_time.strftime('%Y%m%d%H')
                        #)
                        #os.system(COPYGB+'""" -g 0 6 0 0 0 0 0 0 360 181 0 -1 
                                  #+90000000 0 48 -90000000 359000000 1000000
                                  #+ 1000000 0""" -x' +fdatao_file+' '
                                  #+fdatac_file)
                        #os.system(COPYGB+' -g 3 -x' +fdatao_file+' '
                                  #+fdatac_file)
                    get_model_file(valid_time, valid_time,
                                   RUN_abbrev_type_truth_name_lead,
                                   RUN_abbrev_type_truth_name_short,
                                   model_RUN_abbrev_type_truth_dir,
                                   model_RUN_abbrev_type_truth_file_format,
                                   model_data_run_hpss,
                                   model_RUN_abbrev_type_truth_hpss_dir,
                                   link_anl_dir,
                                   RUN_abbrev_type_truth_name_short
                                   +'.{valid?fmt=%Y%m%d%H}')
                    
                    #COPYGB = os.environ['copygb']
                    #adatao_file = os.path.join(
                        #link_model_dir, 'anom.truth.'
                        #+valid_time.strftime('%Y%m%d%H')
                    #)
                    #adatac_file = os.path.join(
                        #link_model_dir, 'anom.truth.'
                        #+valid_time.strftime('%Y%m%d%H')
                    #)
                    #os.system(COPYGB+' -g 3 -x' +adatao_file+' '
                              #+adatac_file)
                    #fix = os.environ['BinClim_Path']
                    #climo_file = os.path.join(
                        #fix, 'cmean_1d.1959'+valid_time.strftime('%m%d%H')
                    #)
                    #cdata_file = os.path.join(
                        #link_model_dir, 'cavg_1d.1959'
                        #+valid_time.strftime('%m%d%H')
                    #)
                    #print("Copying "+climo_file+" to "+cdata_file)
                    #os.system('cpfs '+climo_file+' '+cdata_file)
                    #c1_file = os.path.join(
                        #link_model_dir, 'cmean.1959'
                        #+valid_time.strftime('%m%d%H')
                    #)
                    #convert_grib2_grib1(cdata_file, c1_file)
                    
                    # Check model RUN_type truth file exists
                    truth_file = os.path.join(
                        model_RUN_abbrev_type_truth_dir,
                        RUN_abbrev_type_truth_name_short,
                        format_filler(model_RUN_abbrev_type_truth_file_format,
                                      valid_time, valid_time,
                                      RUN_abbrev_type_truth_name_lead)
                    )
                    link_truth_file = os.path.join(
                        link_anl_dir,
                        format_filler(RUN_abbrev_type_truth_name_short
                                      +'.{valid?fmt=%Y%m%d%H}',
                                      valid_time, valid_time,
                                      RUN_abbrev_type_truth_name_lead)
                    )
                    if not os.path.exists(link_truth_file) \
                            and RUN_abbrev_type_truth_name != 'self_f00':
                        print("WARNING: "+RUN_abbrev_type_truth_name_short
                              +" truth file not found")
elif RUN == 'grid2grid_plots':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_gather_by_list = os.environ[
            RUN_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, plot_by
        )
        # Get model stat files
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_RUN_abbrev_type_gather_by = (
                RUN_abbrev_type_gather_by_list[model_idx]
            )
            link_model_RUN_type_dir = os.path.join(cwdplt, 'data',
                                                   model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'grid2grid', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'grid2obs_stats':
    # Read in RUN related environment variables
    prepbufr_run_hpss = os.environ[RUN_abbrev+'_prepbufr_data_run_hpss']
    prepbufr_prod_upper_air_dir = os.environ['prepbufr_prod_upper_air_dir']
    prepbufr_prod_conus_sfc_dir = os.environ['prepbufr_prod_conus_sfc_dir']
    prepbufr_arch_dir = os.environ['prepbufr_arch_dir']
    iabp_ftp = os.environ['iabp_ftp']
    
    # Get model forecast and observation files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, make_met_data_by
        )
        RUN_abbrev_type_valid_time_list = []
        # Get model forecast files
        for model in model_list:
            model_idx = model_list.index(model)
            model_dir = model_dir_list[model_idx]
            model_file_form = model_file_format_list[model_idx]
            model_hpss_dir = model_hpss_dir_list[model_idx]
            #link_model_dir = os.path.join(cwd, 'data', model)
            #if not os.path.exists(link_model_dir):
                #os.makedirs(link_model_dir)
                #os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    if valid_time not in RUN_abbrev_type_valid_time_list:
                        RUN_abbrev_type_valid_time_list.append(valid_time)
                    cwdm = cwd+'.{init?fmt=%Y%m%d%H}'
                    link_model_dir = os.path.join(cwdm, model)
                    if not os.path.exists(link_model_dir):
                        os.makedirs(link_model_dir)
                        os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
                    mbr = 1
                    total = 4
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        model_file_format = os.path.join(
                            model_file_form, 'monthly_grib_'+mb,
                            'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                            +'{valid?fmt=%Y%m}.avrg.grib.grb2')
                        get_model_file(valid_time, init_time, lead,
                                   model, model_dir, model_file_format,
                                   model_data_run_hpss, model_hpss_dir,
                                   link_model_dir,
                                   'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                                   +'{valid?fmt=%Y%m}.avrg.grib.grb2')
                        del model_file_format
                        mbr = mbr+1
                    #fix = os.environ['BinClim_Path']
                    #climo_file = os.path.join(
                        #fix, 'cmean_1d.1959'+valid_time.strftime('%m%d%H')
                    #)
                    #cdata_file = os.path.join(
                        #link_model_dir, 'cavg_1d.1959'
                        #+valid_time.strftime('%m%d%H')
                    #)
                    #print("Copying "+climo_file+" to "+cdata_file)
                    #os.system('cpfs '+climo_file+' '+cdata_file)
                    #c1_file = os.path.join(
                        #link_model_dir, 'cmean.1959'
                        #+valid_time.strftime('%m%d%H')
                    #)
                    #convert_grib2_grib1(cdata_file, c1_file)
        # Get RUN_type observation files
        for valid_time in RUN_abbrev_type_valid_time_list:
            YYYYmmddHH = valid_time.strftime('%Y%m%d%H')
            YYYYmmdd = valid_time.strftime('%Y%m%d')
            YYYYmm = valid_time.strftime('%Y%m')
            YYYY = valid_time.strftime('%Y')
            mm = valid_time.strftime('%m')
            dd = valid_time.strftime('%d')
            HH = valid_time.strftime('%H')
            DOY = valid_time.strftime('%j')
            if valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                continue
            else:
                if RUN_type == 'polar_sfc':
                    iabp_dir = os.path.join(cwd, 'data', 'iabp')
                    if not os.path.exists(iabp_dir):
                        os.makedirs(iabp_dir)
                    iabp_YYYYmmdd_file = os.path.join(iabp_dir,
                                                      'iabp.'+YYYYmmdd)
                    iabp_region_list = ['Arctic', 'Antarctic']
                    iabp_var_dict = {
                        'BP': ('PRES', '0'),
                        'Ts': ('TMP', '0'),
                        'Ta': ('TMP', '2')
                    }
                    niabp_vars = len(list(iabp_var_dict.keys()))
                    ascii2nc_file_cols = [
                      'Message_Type', 'Station_ID', 'Valid_Time', 'Lat', 'Lon',
                      'Elevation', 'Variable_Name', 'Level', 'Height',
                      'QC_String', 'Observation_Value'
                    ]
                    if not os.path.exists(iabp_YYYYmmdd_file):
                        # Get IABP data from web
                        for iabp_region in iabp_region_list:
                            iabp_region_YYYYmmdd_file = os.path.join(
                                iabp_dir, iabp_region+'_FR_'+YYYYmmdd+'.dat'
                            )
                            if not os.path.exists(iabp_region_YYYYmmdd_file):
                                iabp_ftp_region_YYYYmmdd_file = os.path.join(
                                    iabp_ftp, iabp_region,'FR_'+YYYYmmdd+'.dat'
                                )
                                os.system('wget -q '
                                          +iabp_ftp_region_YYYYmmdd_file+' '
                                          +'--no-check-certificate -O '
                                          +iabp_region_YYYYmmdd_file)
                            if not os.path.exists(iabp_region_YYYYmmdd_file):
                                print("WARNING: Could not get IABP files from "
                                      +"FTP for "+iabp_region+" on "+YYYYmmdd)
                            else:
                                if os.path.getsize(iabp_region_YYYYmmdd_file) \
                                        == 0:
                                    print("WARNING: Could not get IABP files "
                                          +"from FTP for "+iabp_region+" "
                                          +"on "+YYYYmmdd)
                                    os.remove(iabp_region_YYYYmmdd_file)
                        iabp_reg_YYYYmmdd_file_list = glob.glob(
                            os.path.join(iabp_dir, '*'+YYYYmmdd+'.dat')
                        )
                        # Combine and reformat files for ascii2nc
                        if len(iabp_reg_YYYYmmdd_file_list) != 0:
                            iabp_ascii2nc_data = pd.DataFrame(
                                columns=ascii2nc_file_cols
                            )
                            idx_ascii2nc = 0
                            for iabp_reg_YYYYmmdd_file \
                                    in iabp_reg_YYYYmmdd_file_list:
                                iabp_reg_YYYYmmdd_data = pd.read_csv(
                                    iabp_reg_YYYYmmdd_file, sep=";",
                                    skipinitialspace=True, header=0, dtype=str
                                )
                                niabp_reg_YYYYmmdd_data = len(
                                    iabp_reg_YYYYmmdd_data.index
                                )
                                dates = []
                                for idx in iabp_reg_YYYYmmdd_data.index:
                                    dates.append(
                                        datetime.datetime.strptime(
                                            iabp_reg_YYYYmmdd_data.loc[
                                                idx,'Year'
                                            ]+' '
                                            +iabp_reg_YYYYmmdd_data.loc[
                                                idx,'DOY'
                                            ].split('.')[0]+' '
                                            +iabp_reg_YYYYmmdd_data.loc[
                                                idx,'Hour'
                                            ]+' '
                                            +iabp_reg_YYYYmmdd_data.loc[
                                                idx,'Min'
                                            ],
                                            '%Y %j %H %M'
                                        ).strftime('%Y%m%d_%H%M%S')
                                    )
                                iabp_ascii2nc_reg_data = pd.DataFrame(
                                    index=pd.RangeIndex(
                                        0,
                                        niabp_reg_YYYYmmdd_data * niabp_vars,
                                        1
                                    ),
                                    columns=ascii2nc_file_cols
                                )
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Message_Type'
                                ] = 'IABP'
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Station_ID'
                                ] = iabp_reg_YYYYmmdd_data.loc[:, 'BuoyID'] \
                                    .tolist() * niabp_vars
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Valid_Time'
                                ] = dates * 3
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Lat'
                                ] = iabp_reg_YYYYmmdd_data.loc[:, 'Lat'] \
                                    .tolist() * niabp_vars
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Lon'
                                ] = iabp_reg_YYYYmmdd_data.loc[:, 'Lon'] \
                                    .tolist() * niabp_vars
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Elevation'
                                ] = '0'
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'Level'
                                ] = '0'
                                iabp_ascii2nc_reg_data.loc[
                                    :, 'QC_String'
                                ] = 'NA'
                                for iabp_var in list(iabp_var_dict.keys()):
                                    start_var_idx = (
                                        niabp_reg_YYYYmmdd_data
                                        * list(iabp_var_dict.keys()) \
                                        .index(iabp_var)
                                    )
                                    end_var_idx = (
                                        niabp_reg_YYYYmmdd_data
                                        * (list(iabp_var_dict.keys()) \
                                        .index(iabp_var)+1) - 1
                                    )
                                    iabp_ascii2nc_reg_data.loc[
                                       start_var_idx:end_var_idx,
                                       'Variable_Name'
                                    ] = iabp_var_dict[iabp_var][0]
                                    iabp_ascii2nc_reg_data.loc[
                                        start_var_idx:end_var_idx,
                                        'Height'
                                    ] = iabp_var_dict[iabp_var][1]
                                    iabp_var_vals = np.array(
                                        iabp_reg_YYYYmmdd_data \
                                        .loc[:, iabp_var].tolist(),
                                        dtype=float
                                    )
                                    iabp_var_vals = np.ma.masked_where(
                                        iabp_var_vals <= -999.00,
                                        iabp_var_vals
                                    )
                                    if iabp_var == 'BP':
                                        iabp_var_vals = iabp_var_vals * 100.
                                    else:
                                        iabp_var_vals = iabp_var_vals + 273.15
                                    iabp_var_vals = iabp_var_vals.astype(str)
                                    iabp_var_vals.set_fill_value('NA')
                                    iabp_ascii2nc_reg_data.loc[
                                        start_var_idx:end_var_idx,
                                        'Observation_Value'
                                    ] = iabp_var_vals.filled()
                                iabp_ascii2nc_data = (
                                    iabp_ascii2nc_data.append(
                                        iabp_ascii2nc_reg_data
                                    ).reset_index(drop=True)
                                )
                            iabp_ascii2nc_data_string = (
                                iabp_ascii2nc_data.to_string(header=False,
                                                             index=False)
                            )
                            if os.path.exists(iabp_YYYYmmdd_file):
                                os.remove(iabp_YYYYmmdd_file)
                            with open(iabp_YYYYmmdd_file, 'a') as output_file:
                                output_file.write(iabp_ascii2nc_data_string)
                elif RUN_type in ['upper_air', 'conus_sfc']:
                    link_prepbufr_dir = os.path.join(cwd, 'anl', 'prepbufr')
                    if not os.path.exists(link_prepbufr_dir):
                        os.makedirs(link_prepbufr_dir)
                        os.makedirs(
                            os.path.join(link_prepbufr_dir, 'HPSS_jobs')
                        )
                    prepbufr_dict_list = []
                    # Set up prepbufr file information
                    if RUN_type == 'upper_air':
                        prepbufr = 'gdas'
                        link_prepbufr_file = os.path.join(
                            link_prepbufr_dir, 'prepbufr.'+prepbufr+'.'
                            +YYYYmmddHH
                        )
                        prepbufr_prod_file = os.path.join(
                            prepbufr_prod_upper_air_dir, prepbufr+'.'+YYYYmmdd,
                            HH, 'atmos', prepbufr+'.t'+HH+'z.prepbufr'
                        )
                        prepbufr_arch_file = os.path.join(
                            prepbufr_arch_dir, prepbufr, 'prepbufr.'+prepbufr
                            +'.'+YYYYmmddHH
                        )
                        (prepbufr_hpss_tar, prepbufr_hpss_file,
                         prepbufr_hpss_job_filename) = set_up_cfs_hpss_info(
                             valid_time, hpss_prod_base_dir, prepbufr, 'prepbufr',
                             link_prepbufr_dir
                        )
                        prepbufr_dict = {}
                        prepbufr_dict['prod_file'] = prepbufr_prod_file
                        prepbufr_dict['arch_file'] = prepbufr_arch_file
                        prepbufr_dict['hpss_tar'] = prepbufr_hpss_tar
                        prepbufr_dict['hpss_file'] = prepbufr_hpss_file
                        prepbufr_dict['hpss_job_filename'] = (
                            prepbufr_hpss_job_filename
                        )
                        prepbufr_dict['file_type'] = prepbufr
                        prepbufr_dict_list.append(prepbufr_dict)
                    elif RUN_type == 'conus_sfc':
                        if valid_time \
                                >= datetime.datetime.strptime('20170320',
                                                              '%Y%m%d'):
                            prepbufr = 'nam' #'rap'
                        else:
                            prepbufr = 'ndas'
                        link_prepbufr_file = os.path.join(
                            link_prepbufr_dir, 'prepbufr.'+prepbufr+'.'
                            +YYYYmmddHH
                        )
                        if prepbufr == 'nam':
                            offset_hr = str(int(HH)%6).zfill(2)
                            offset_time = valid_time + datetime.timedelta(
                                hours=int(offset_hr)
                            )
                            offset_YYYYmmddHH = offset_time.strftime('%Y%m%d%H')
                            offset_YYYYmmdd = offset_time.strftime('%Y%m%d')
                            offset_YYYYmm = offset_time.strftime('%Y%m')
                            offset_YYYY = offset_time.strftime('%Y')
                            offset_mm = offset_time.strftime('%m')
                            offset_dd = offset_time.strftime('%d')
                            offset_HH = offset_time.strftime('%H')
                            offset_filename = (
                                'nam.t'+offset_HH+'z.prepbufr.tm'+offset_hr
                            )
                            prepbufr_prod_file = os.path.join(
                                prepbufr_prod_conus_sfc_dir, 'nam.'
                                +offset_YYYYmmdd, offset_filename
                            )
                            prepbufr_arch_file = os.path.join(
                                prepbufr_arch_dir, 'nam', 'nam.'
                                +offset_YYYYmmdd, offset_filename
                            )
                            if offset_time \
                                    >= datetime.datetime.strptime('20200227',
                                                                  '%Y%m%d') \
                                   or offset_time \
                                   == datetime.datetime.strptime('20170320'
                                                                 +offset_HH,
                                                                 '%Y%m%d%H'):
                                prepbufr_hpss_tar_prefix = 'com_nam_prod_nam.'
                            elif offset_time \
                                    >= datetime.datetime.strptime('20190821',
                                                                  '%Y%m%d') \
                                    and offset_time \
                                    < datetime.datetime.strptime('20200227',
                                                                 '%Y%m%d'):
                                prepbufr_hpss_tar_prefix = (
                                    'gpfs_dell1_nco_ops_com_nam_prod_nam.'
                                )
                            else:
                                prepbufr_hpss_tar_prefix = 'com2_nam_prod_nam.'
                            prepbufr_hpss_tar = os.path.join(
                                hpss_prod_base_dir, 'rh'+offset_YYYY,
                                offset_YYYYmm, offset_YYYYmmdd,
                                prepbufr_hpss_tar_prefix
                                +offset_YYYYmmddHH+'.bufr.tar')
                            prepbufr_hpss_file = offset_filename
                            prepbufr_dict = {}
                            prepbufr_dict['prod_file'] = prepbufr_prod_file
                            prepbufr_dict['arch_file'] = prepbufr_arch_file
                            prepbufr_dict['hpss_tar'] = prepbufr_hpss_tar
                            prepbufr_dict['hpss_file'] = prepbufr_hpss_file
                            prepbufr_dict['hpss_job_filename'] = os.path.join(
                                link_prepbufr_dir, 'HPSS_jobs', 'HPSS_'
                                +prepbufr_hpss_tar.rpartition('/')[2]
                                +'_'+prepbufr_hpss_file.replace('/', '_')+'.sh'
                            )
                            prepbufr_dict_list.append(prepbufr_dict)
                        elif prepbufr == 'ndas':
                            ndas_date_dict = {}
                            for xhr in ['00', '03', '06', '09',
                                        '12', '15', '18', '21']:
                                xdate = valid_time + datetime.timedelta(hours=int(xhr))
                                ndas_date_dict['YYYY'+xhr] = xdate.strftime('%Y')
                                ndas_date_dict['YYYYmm'+xhr] = xdate.strftime('%Y%m')
                                ndas_date_dict['YYYYmmdd'+xhr] = xdate.strftime('%Y%m%d')
                                ndas_date_dict['HH'+xhr] = xdate.strftime('%H')
                            if ndas_date_dict['HH00'] in ['00', '06', '12', '18']:
                                ndas_hour_list = ['12', '06', '00']
                            elif ndas_date_dict['HH00'] in ['03', '09', '15', '21']:
                                ndas_hour_list = ['09', '03']
                            for ndas_hour in ndas_hour_list:
                                ndas_hour_filename = (
                                    'ndas.t'+ndas_date_dict['HH'+ndas_hour]
                                     +'z.prepbufr.tm'+ndas_hour
                                )
                                prepbufr_prod_file = os.path.join(
                                    prepbufr_prod_conus_sfc_dir, 'ndas.'
                                    +ndas_date_dict['YYYYmmdd'+ndas_hour],
                                    ndas_hour_filename
                                )
                                prepbufr_arch_file = os.path.join(
                                    prepbufr_arch_dir, 'ndas', 'ndas.'
                                    +ndas_date_dict['YYYYmmdd'+ndas_hour],
                                    ndas_hour_filename
                                )
                                prepbufr_hpss_tar = os.path.join(
                                    hpss_prod_base_dir, 'rh'
                                    +ndas_date_dict['YYYY'+ndas_hour],
                                    ndas_date_dict['YYYYmm'+ndas_hour],
                                    ndas_date_dict['YYYYmmdd'+ndas_hour],
                                    'com_nam_prod_ndas.'
                                    +ndas_date_dict['YYYYmmdd'+ndas_hour]
                                    +ndas_date_dict['HH'+ndas_hour]
                                    +'.bufr.tar'
                                )
                                prepbufr_hpss_file = ndas_hour_filename
                                prepbufr_dict = {}
                                prepbufr_dict['prod_file'] = prepbufr_prod_file
                                prepbufr_dict['arch_file'] = prepbufr_arch_file
                                prepbufr_dict['hpss_tar'] = prepbufr_hpss_tar
                                prepbufr_dict['hpss_file'] = prepbufr_hpss_file
                                prepbufr_dict['hpss_job_filename'] = (
                                    os.path.join(link_prepbufr_dir,
                                                 'HPSS_jobs', 'HPSS_'
                                                 +prepbufr_hpss_tar \
                                                 .rpartition('/')[2]
                                                 +'_'+prepbufr_hpss_file \
                                                 .replace('/', '_')+'.sh')
                                )
                                prepbufr_dict_list.append(prepbufr_dict)
                    # Get prepbufr file
                    if not os.path.exists(link_prepbufr_file):
                        for prepbufr_dict in prepbufr_dict_list:
                            prod_file = prepbufr_dict['prod_file']
                            arch_file = prepbufr_dict['arch_file']
                            hpss_tar = prepbufr_dict['hpss_tar']
                            hpss_file = prepbufr_dict['hpss_file']
                            hpss_job_filename = (
                                prepbufr_dict['hpss_job_filename']
                            )
                            if os.path.exists(prod_file):
                                os.system('ln -sf '+prod_file+' '
                                          +link_prepbufr_file)
                            elif os.path.exists(arch_file):
                                os.system('ln -sf '+arch_file+' '
                                          +link_prepbufr_file)
                            else:
                                if prepbufr_run_hpss == 'YES':
                                    print("Did not find "+prod_file+" or "
                                          +arch_file+" online...going to try "
                                          +"to get file from HPSS")
                                    get_hpss_data(hpss_job_filename,
                                                  link_prepbufr_dir,
                                                  link_prepbufr_file,
                                                  hpss_tar, hpss_file)
                            if os.path.exists(link_prepbufr_file):
                                break
                            else:
                                if prepbufr_run_hpss == 'YES':
                                    print("WARNING: "+prod_file+" and "
                                          +arch_file+" do not exist and did "
                                          +"not find HPSS file "+hpss_file+" "
                                          +"from "+hpss_tar+" or walltime "
                                          +"exceeded")
                                else:
                                    print("WARNING: "+prod_file+" and "
                                          +arch_file+" do not exist")
                                if prepbufr_dict != prepbufr_dict_list[-1]:
                                    print("Checking next prepbufr file valid "
                                          +"at "+YYYYmmddHH)
elif RUN == 'grid2obs_plots':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_gather_by_list = os.environ[
            RUN_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, plot_by
        )
        # Get model stat files
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_RUN_abbrev_type_gather_by = (
                RUN_abbrev_type_gather_by_list[model_idx]
            )
            link_model_RUN_type_dir = os.path.join(cwdplt, 'data',
                                                        model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'grid2obs', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'precip_stats':
    # Read in RUN related environment variables
    obs_run_hpss = os.environ[RUN_abbrev+'_obs_data_run_hpss']
    ccpa_accum24hr_prod_dir = os.environ['ccpa_24hr_prod_dir']
    ccpa_accum24hr_arch_dir = os.environ['ccpa_24hr_arch_dir']
    # Get model forecast and observation files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_model_bucket_list = os.environ[
            RUN_abbrev_type+'_model_bucket_list'
        ].split(' ')
        RUN_abbrev_type_model_var_list = os.environ[
            RUN_abbrev_type+'_model_var_list'
        ].split(' ')
        RUN_abbrev_type_model_file_format_list = os.environ[
            RUN_abbrev_type+'_model_file_format_list'
        ].split(' ')
        RUN_abbrev_type_accum_length = (
            RUN_type.split('accum')[1].replace('hr','')
        )
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, make_met_data_by
        )
        RUN_abbrev_type_valid_time_list = []
        # Get model forecast files
        for model in model_list:
            model_idx = model_list.index(model)
            model_dir = model_dir_list[model_idx]
            model_hpss_dir = model_hpss_dir_list[model_idx]
            model_bucket = RUN_abbrev_type_model_bucket_list[model_idx]
            model_var = RUN_abbrev_type_model_var_list[model_idx]
            model_file_form = (
                RUN_abbrev_type_model_file_format_list[model_idx]
            )
            #link_model_dir = os.path.join(cwd, 'data', model)
            #if not os.path.exists(link_model_dir):
                #os.makedirs(link_model_dir)
                #os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead_end = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    if valid_time not in RUN_abbrev_type_valid_time_list:
                        RUN_abbrev_type_valid_time_list.append(valid_time)
                    lead_in_accum_list = []
                    if model_bucket == 'continuous':
                        nfiles_in_accum = 2
                        lead_in_accum_list.append(lead_end)
                        lead_start = (
                            int(lead_end)-int(RUN_abbrev_type_accum_length)
                        )
                        if lead_start > 0:
                            lead_in_accum_list.append(str(lead_start))
                    else:
                        nfiles_in_accum = (
                            int(RUN_abbrev_type_accum_length)/int(model_bucket)
                        )
                        nf = 1
                        while nf <= nfiles_in_accum:
                            lead_now = int(lead_end)-((nf-1)*int(model_bucket))
                            if lead_now >= 0:
                                lead_in_accum_list.append(str(lead_now))
                            nf+=1
                    if len(lead_in_accum_list) == nfiles_in_accum:
                        for lead in lead_in_accum_list:
                            cwdm = cwd+'.{init?fmt=%Y%m%d%H}'
                            link_model_dir = os.path.join(cwdm, model)
                            if not os.path.exists(link_model_dir):
                                os.makedirs(link_model_dir)
                                os.makedirs(
                                    os.path.join(link_model_dir, 'HPSS_jobs')
                                    )
                            mbr = 1
                            total = 4
                            while mbr <= total:
                                if model_var == 'PRATE':
                                    mb = str(mbr).zfill(2)
                                    model_file_format = os.path.join(
                                        model_file_form, 'monthly_grib_'+mb,
                                        'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                                        +'{valid?fmt=%Y%m}.avrg.grib.grb2')
                                    get_model_file(
                                        valid_time, init_time, lead, model,
                                        model_dir, model_file_format,
                                        model_data_run_hpss, model_hpss_dir,
                                        link_model_dir,
                                        'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}'
                                        +'.PRATE'
                                    )
                                    del model_file_format
                                    mbr = mbr+1
                                link_model_file = os.path.join(
                                    link_model_dir, format_filler(
                                        'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}',
                                         valid_time, init_time, lead
                                    )
                                )
                                if os.path.exists(link_model_file+'.PRATE') \
                                       and not os.path.exists(link_model_file):
                                    cnvgrib = os.environ['CNVGRIB']
                                    wgrib2 = os.environ['WGRIB2']
                                    tmp_gb2_file = os.path.join(link_model_dir,
                                                                'tmp_gb2')
                                    tmp_gb2_APCP_file = os.path.join(
                                        link_model_dir, 'tmp_gb2_APCP'
                                    )
                                    os.system(
                                        cnvgrib+' -g12 '
                                        +link_model_file+'.PRATE'+' '
                                        +tmp_gb2_file
                                    )
                                    os.system(
                                        wgrib2+' '+tmp_gb2_file+' -match '
                                        +'":PRATE:" -rpn "3600:*" -set_var '
                                        +'APCP -set table_4.10 1 -grib_out '
                                        +tmp_gb2_APCP_file+' >>/dev/null'
                                    )
                                    os.system(
                                        cnvgrib+' -g21 '+tmp_gb2_APCP_file+' '
                                        +link_model_file
                                    )
                                    os.system(
                                        'rm '+os.path.join(link_model_dir,
                                                           'tmp*')
                                    )
                                elif model_var == 'APCP':
                                    mb = str(mbr).zfill(2)
                                    model_file_format = os.path.join(
                                        model_file_form, 'monthly_grib_'+mb,
                                        'pgbf.'+mb+'.{init?fmt=%Y%m%d%H}.'
                                        +'.{valid?fmt=%Y%m}.avrg.grib.grb2')
                                    get_model_file(
                                        valid_time, init_time, lead, model,
                                        model_dir, model_file_format,
                                        model_data_run_hpss, model_hpss_dir,
                                        link_model_dir,
                                        'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}'
                                    )
                                    del model_file_format
                                    mbr = mbr+1
        # Get RUN_type observation files
        for valid_time in RUN_abbrev_type_valid_time_list:
            YYYYmmddHH = valid_time.strftime('%Y%m%d%H')
            YYYYmmdd = valid_time.strftime('%Y%m%d')
            YYYYmm = valid_time.strftime('%Y%m')
            YYYY = valid_time.strftime('%Y')
            mm = valid_time.strftime('%m')
            dd = valid_time.strftime('%d')
            HH = valid_time.strftime('%H')
            if valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                continue
            else:
                link_RUN_type_dir = os.path.join(cwd, 'anl', RUN_type)
                if not os.path.exists(link_RUN_type_dir):
                    os.makedirs(link_RUN_type_dir)
                    os.makedirs(os.path.join(link_RUN_type_dir, 'HPSS_jobs'))
                if RUN_type == 'ccpa_accum24hr':
                    link_RUN_type_file = os.path.join(
                        link_RUN_type_dir, 'ccpa.'+YYYYmmdd+'12.24h'
                    )
                    #RUN_type_prod_file = os.path.join(
                        #ccpa_accum24hr_prod_dir, 'precip.'+YYYYmmdd,
                        #'ccpa.'+YYYYmmdd+'12.24h'
                    #)
                    RUN_type_prod_file = os.path.join(
                        ccpa_accum24hr_prod_dir, 'ccpa.'+YYYYmmdd,
                        HH, 'ccpa.t'+HH+'z.06h.hrap.conus.gb2'
                    RUN_type_arch_file = os.path.join(
                        ccpa_accum24hr_arch_dir, 'ccpa.'+YYYYmmdd+'12.24h'
                    )
                    if valid_time \
                            >= datetime.datetime.strptime('20200226',
                                                          '%Y%m%d'):
                        RUN_type_hpss_tar_prefix = 'com_verf_prod_precip.'
                    if valid_time \
                            >= datetime.datetime.strptime('20200126',
                                                          '%Y%m%d') \
                            and valid_time \
                            < datetime.datetime.strptime('20200226',
                                                          '%Y%m%d'):
                        RUN_type_hpss_tar_prefix = (
                            'gpfs_dell1_nco_ops_com_verf_prod_precip.'
                        )
                    else:
                        RUN_type_hpss_tar_prefix = 'com_verf_prod_precip.'
                    RUN_type_hpss_tar = os.path.join(
                        hpss_prod_base_dir, 'rh'+YYYY, YYYYmm, YYYYmmdd,
                        RUN_type_hpss_tar_prefix+YYYYmmdd+'.precip.tar'
                    )
                    RUN_type_hpss_file = 'ccpa.'+YYYYmmdd+'12.24h'
                if not os.path.exists(link_RUN_type_file):
                    if os.path.exists(RUN_type_prod_file):
                        os.system('ln -sf '+RUN_type_prod_file+' '
                                 +link_RUN_type_file)
                    elif os.path.exists(RUN_type_arch_file):
                        os.system('ln -sf '+RUN_type_arch_file+' '
                                  +link_RUN_type_file)
                    else:
                        if obs_run_hpss == 'YES':
                            print("Did not find "+RUN_type_prod_file+" or "
                                  +RUN_type_arch_file+" online...going to try "
                                  +"to get file from HPSS")
                            hpss_job_filename = os.path.join(
                                link_RUN_type_dir, 'HPSS_jobs',
                                'HPSS_'+RUN_type_hpss_tar.rpartition('/')[2]
                                +'_'+RUN_type_hpss_file.replace('/', '_')+'.sh'
                            )
                            get_hpss_data(hpss_job_filename,
                                          link_RUN_type_dir,
                                          link_RUN_type_file,
                                          RUN_type_hpss_tar,
                                          RUN_type_hpss_file)
                if not os.path.exists(link_RUN_type_file):
                    if obs_run_hpss == 'YES':
                        print("WARNING: "+RUN_type_prod_file+" and "
                              +RUN_type_arch_file+" do not exist and did "
                              +"not find HPSS file "+RUN_type_hpss_file+" "
                              +"from "+RUN_type_hpss_tar+" or walltime "
                              +"exceeded")
                    else:
                        print("WARNING: "+RUN_type_prod_file+" and "
                               +RUN_type_arch_file+" do not exist")
elif RUN == 'precip_plots':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_gather_by_list = os.environ[
            RUN_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, plot_by
        )
        # Get model stat files
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_RUN_abbrev_type_gather_by = (
                RUN_abbrev_type_gather_by_list[model_idx]
            )
            link_model_RUN_type_dir = os.path.join(cwdplt, 'data',
                                                   model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'precip', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'satellite_step1':
    # Read in RUN related environment variables
    ghrsst_ncei_avhrr_anl_ftp = os.environ['ghrsst_ncei_avhrr_anl_ftp']
    ghrsst_ospo_geopolar_anl_ftp = os.environ['ghrsst_ospo_geopolar_anl_ftp']
    # Get model forecast and truth files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, make_met_data_by
        )
        RUN_abbrev_type_valid_time_list = []
        # Get forecast and truth files for each model
        for model in model_list:
            model_idx = model_list.index(model)
            model_dir = model_dir_list[model_idx]
            model_file_format = model_file_format_list[model_idx]
            model_hpss_dir = model_hpss_dir_list[model_idx]
            link_model_dir = os.path.join(cwd, 'data', model)
            if not os.path.exists(link_model_dir):
                os.makedirs(link_model_dir)
                os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
            # Get model forecast files
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead_end = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    if valid_time not in RUN_abbrev_type_valid_time_list:
                        RUN_abbrev_type_valid_time_list.append(valid_time)
                    if RUN_type in ['ghrsst_ncei_avhrr_anl',
                                    'ghrsst_ospo_geopolar_anl']:
                        lead_intvl = 6
                        nfiles_in_mean = 5
                        lead_in_mean_list = []
                        nf = 1
                        while nf <= nfiles_in_mean:
                            lead_now = int(lead_end)-((nf-1)*lead_intvl)
                            if lead_now >= 0:
                                lead_in_mean_list.append(str(lead_now))
                            nf+=1
                    if len(lead_in_mean_list) == nfiles_in_mean:
                        for lead in lead_in_mean_list:
                            get_model_file(valid_time, init_time, lead,
                                           model, model_dir, model_file_format,
                                           model_data_run_hpss, model_hpss_dir,
                                           link_model_dir,
                                           'f{lead?fmt=%3H}'
                                           +'.{init?fmt=%Y%m%d%H}')
        # Get RUN_type observation files
        for valid_time in RUN_abbrev_type_valid_time_list:
            YYYYmmddHH = valid_time.strftime('%Y%m%d%H')
            YYYYmmdd = valid_time.strftime('%Y%m%d')
            YYYYmm = valid_time.strftime('%Y%m')
            YYYY = valid_time.strftime('%Y')
            mm = valid_time.strftime('%m')
            dd = valid_time.strftime('%d')
            HH = valid_time.strftime('%H')
            DOY = valid_time.strftime('%j')
            valid_timeM1 = valid_time - datetime.timedelta(hours=24)
            YYYYmmddHHM1 = valid_timeM1.strftime('%Y%m%d%H')
            YYYYmmddM1 = valid_timeM1.strftime('%Y%m%d')
            YYYYmmM1 = valid_timeM1.strftime('%Y%m')
            YYYYM1 = valid_timeM1.strftime('%Y')
            mmM1 = valid_timeM1.strftime('%m')
            ddM1 = valid_timeM1.strftime('%d')
            HHM1 = valid_timeM1.strftime('%H')
            DOYM1 = valid_timeM1.strftime('%j')
            if valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                continue
            else:
                link_RUN_type_dir = os.path.join(cwd, 'data', RUN_type)
                if not os.path.exists(link_RUN_type_dir):
                    os.makedirs(link_RUN_type_dir)
                link_RUN_type_file = os.path.join(link_RUN_type_dir,
                                                  RUN_type+'.'+YYYYmmddHH)
                if RUN_type in ['ghrsst_ncei_avhrr_anl',
                                'ghrsst_ospo_geopolar_anl']:
                    # ghrsst_ncei_avhrr_anl: YYYYmmddM-1 00Z-YYYYmmdd 00Z
                    if RUN_type == 'ghrsst_ncei_avhrr_anl':
                        RUN_type_ftp_file = os.path.join(
                            ghrsst_ncei_avhrr_anl_ftp,
                            YYYYM1, DOYM1,
                            YYYYmmddM1
                            +'120000-NCEI-L4_GHRSST-SSTblend-AVHRR_OI-GLOB-'
                            +'v02.0-fv02.1.nc'
                        )
                        adjust_time = '86400'
                    # ghrsst_ospo_geopolar_anl: YYYYmmddM-1 00Z-YYYYmmdd 00Z
                    elif RUN_type == 'ghrsst_ospo_geopolar_anl':
                        RUN_type_ftp_file = os.path.join(
                            ghrsst_ospo_geopolar_anl_ftp,
                            YYYYM1, DOYM1,
                            YYYYmmddM1
                            +'000000-OSPO-L4_GHRSST-SSTfnd-Geo_Polar_Blended'
                            +'-GLOB-v02.0-fv01.0.nc'
                        )
                        adjust_time = '43200'
                    os.system('wget -q '+RUN_type_ftp_file+' '
                               +'-O '+link_RUN_type_file)
                    if os.path.exists(link_RUN_type_file) \
                            and os.path.getsize(link_RUN_type_file) > 0:
                        ncap2 = os.environ['NCAP2']
                        os.system(ncap2+' -s "time=time+'+adjust_time+'" -O '
                                  +link_RUN_type_file+' '+link_RUN_type_file)
                        os.system(ncap2+' -s "'
                                  +'sea_ice_fraction=float(sea_ice_fraction) " '
                                  +'-O '+link_RUN_type_file+' '+link_RUN_type_file)
                        os.system(ncap2+' -s "'
                                  +'mask=float(mask) " '
                                  +'-O '+link_RUN_type_file+' '+link_RUN_type_file)
                        gen_vx_mask = subprocess.check_output(
                            'which gen_vx_mask', shell=True, encoding='UTF-8'
                        ).replace('\n', '')
                        os.system(
                            gen_vx_mask+' '+link_RUN_type_file+' '
                            +link_RUN_type_file+' '
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.WATER.nc ')
                            +'-type data -thresh ==1 -mask_field '
                            +"'name="+'"mask"; level="(0,*,*)";'+"' "
                            +'-name WATER'
                        )
                        os.system(
                            gen_vx_mask+' '+link_RUN_type_file+' '
                            +link_RUN_type_file+' '
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.SEA_ICE.nc ')
                            +'-type data -thresh '+'">=0.15"'+' -mask_field '
                            +"'name="+'"sea_ice_fraction"; level="(0,*,*)";'
                            +"' "+'-name SEA_ICE'
                        )
                        os.system(
                            gen_vx_mask+' '
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.SEA_ICE.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.SEA_ICE.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH
                                          +'.vx_mask.SEA_ICE_POLAR.nc ')
                            +'-type lat -thresh '+"'<60&&>-60'"+' -mask_field '
                            +"'name="+'"SEA_ICE"; level="(*,*)";'+"' "
                            +'-name SEA_ICE_POLAR -value "0"'
                        )
                        os.system(
                            gen_vx_mask+' '
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.WATER.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH+'.vx_mask.SEA_ICE.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH
                                          +'.vx_mask.SEA_ICE_FREE.nc ')
                            +'-type data -thresh '+"'==0'"+' -intersection '
                            +'-mask_field '+"'name="+'"SEA_ICE"; '
                            +'level="(*,*)";'+"' "+'-name SEA_ICE_FREE'
                        )
                        os.system(
                            gen_vx_mask+' '
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH
                                          +'.vx_mask.SEA_ICE_FREE.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH
                                          +'.vx_mask.SEA_ICE_FREE.nc ')
                            +os.path.join(link_RUN_type_dir, RUN_type+'.'
                                          +YYYYmmddHH
                                          +'.vx_mask.SEA_ICE_FREE_POLAR.nc ')
                            +'-type lat -thresh '+"'<60&&>-60'"+' -mask_field '
                            +"'name="+'"SEA_ICE_FREE"; level="(*,*)";'+"' "
                            +'-name SEA_ICE_FREE_POLAR -value "0"'
                        )
                    elif os.path.exists(link_RUN_type_file) \
                            and os.path.getsize(link_RUN_type_file) == 0:
                        print("WARNING: could not get "+RUN_type_ftp_file)
                        os.remove(link_RUN_type_file)
                    else:
                        print("WARNING: could not get "+RUN_type_ftp_file)
elif RUN == 'satellite_step2':
    # Read in RUN related environment variables
    # Get stat files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_fcyc_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
        RUN_abbrev_type_vhr_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        RUN_abbrev_type_fhr_list = os.environ[
            RUN_abbrev_type+'_fhr_list'
        ].split(', ')
        RUN_abbrev_type_gather_by_list = os.environ[
            RUN_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            RUN_abbrev_type_fhr_list, plot_by
        )
        # Get stat files model
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_RUN_abbrev_type_gather_by = (
                RUN_abbrev_type_gather_by_list[model_idx]
            )
            link_model_RUN_type_dir = os.path.join(cwd, 'data',
                                                        model, RUN_type)
            if not os.path.exists(link_model_RUN_type_dir):
                os.makedirs(link_model_RUN_type_dir)
            for time in RUN_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in RUN_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in RUN_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_RUN_abbrev_type_gather_by,
                                        'satellite', RUN_type,
                                        link_model_RUN_type_dir)
elif RUN == 'tropcyc':
    # Read in RUN related environment variables
    RUN_abbrev_fcyc_list = os.environ[RUN_abbrev+'_fcyc_list'].split(' ')
    RUN_abbrev_vhr_list = os.environ[RUN_abbrev+'_vhr_list'].split(' ')
    RUN_abbrev_model_atcf_name_list = (
        os.environ[RUN_abbrev+'_model_atcf_name_list'].split(' ')
    )
    RUN_abbrev_model_file_format_list = (
        os.environ[RUN_abbrev+'_model_file_format_list'].split(' ')
    )
    RUN_abbrev_config_storm_list = (
        os.environ[RUN_abbrev+'_storm_list'].split(' ')
    )
    RUN_abbrev_fhr_list = os.environ[RUN_abbrev+'_fhr_list'].split(', ')
    # Check storm_list to see if all storms for basin and year requested
    import get_tc_info
    tc_dict = get_tc_info.get_tc_dict()
    RUN_abbrev_tc_list = []
    for config_storm in RUN_abbrev_config_storm_list:
        config_storm_basin = config_storm.split('_')[0]
        config_storm_year = config_storm.split('_')[1]
        config_storm_name = config_storm.split('_')[2]
        if config_storm_name == 'ALLNAMED':
            for byn in list(tc_dict.keys()):
                if config_storm_basin+'_'+config_storm_year in byn:
                    RUN_abbrev_tc_list.append(byn)
        else:
            RUN_abbrev_tc_list.append(config_storm)
    # Get bdeck/truth and  model track files
    for tc in RUN_abbrev_tc_list:
        basin = tc.split('_')[0]
        year = tc.split('_')[1]
        name = tc.split('_')[2]
        tc_id = tc_dict[tc]
        # Get adeck/bdeck files
        for deck in ['a', 'b']:
            link_deck_dir = os.path.join(cwd, 'data', deck+'deck')
            if not os.path.exists(link_deck_dir):
                os.makedirs(link_deck_dir)
            deck_filename = deck+tc_id+'.dat'
            link_deck_file = os.path.join(link_deck_dir, deck_filename)
            if deck == 'a':
                link_adeck_file = link_deck_file
            elif deck == 'b':
                link_bdeck_file = link_deck_file
            nhc_atcfnoaa_deck_dir = os.environ['nhc_atcfnoaa_'+deck+'deck_dir']
            nhc_atcfnavy_deck_dir = os.environ['nhc_atcfnavy_'+deck+'deck_dir']
            nhc_atcf_deck_ftp = os.environ['nhc_atcf_'+deck+'deck_ftp']
            nhc_atfc_arch_ftp = os.environ['nhc_atfc_arch_ftp']
            if deck == 'b':
                navy_atcf_bdeck_ftp = os.environ['navy_atcf_bdeck_ftp']
            nhc_deck_file = os.path.join(nhc_atcfnoaa_deck_dir, deck_filename)
            navy_deck_file = os.path.join(nhc_atcfnavy_deck_dir, deck_filename)
            if os.path.exists(nhc_deck_file):
                os.system('ln -sf '+nhc_deck_file+' '+link_deck_file)
            elif os.path.exists(navy_deck_file):
                os.system('ln -sf '+navy_deck_file+' '+link_deck_file)
            else:
                if basin in ['AL', 'CP', 'EP']:
                    nhc_ftp_deck_file = os.path.join(nhc_atcf_deck_ftp,
                                                     deck_filename)
                    os.system('wget -q '+nhc_ftp_deck_file+' -P '
                              +link_deck_dir)
                    nhc_ftp_deck_gzfile = os.path.join(nhc_atfc_arch_ftp, year,
                                                       deck_filename+'.gz')
                    nhc_deck_gzfile = os.path.join(link_deck_dir,
                                                   deck_filename+'.gz')
                    os.system('wget -q '+nhc_ftp_deck_gzfile+' -P '
                              +link_deck_dir)
                    if os.path.exists(nhc_deck_gzfile):
                        os.system('gunzip -q -f '+nhc_deck_gzfile)
                    if not os.path.exists(link_deck_file):
                        print("Did not find "+nhc_deck_file+" or "
                              +navy_deck_file+" and could not get from NHC "
                              +"ftp ("+nhc_ftp_deck_file+", "
                              +nhc_ftp_deck_gzfile+") for "+tc)
                elif basin == 'WP' and deck == 'b':
                    navy_ftp_bdeck_zipfile = os.path.join(navy_atcf_bdeck_ftp,
                                                          year, year+'s-bwp',
                                                          'bwp'+year+'.zip')
                    navy_bdeck_zipfile = os.path.join(link_deck_dir,
                                                      'bwp'+year+'.zip')
                    if not os.path.exists(navy_bdeck_zipfile):
                        os.system('wget -q '+navy_ftp_bdeck_zipfile+' -P '
                                  +link_deck_dir)
                    if os.path.exists(navy_bdeck_zipfile):
                        os.system('unzip -qq -o -d '+link_deck_dir+' '
                                  +navy_bdeck_zipfile+' '+deck_filename)
                    if not os.path.exists(link_deck_file):
                        print("Did not find "+nhc_deck_file+" or "
                              +navy_deck_file+" and could not get from Navy "
                              +"ftp ("+navy_ftp_bdeck_zipfile+" "
                              +deck_filename+") for "+tc)
                elif basin == 'WP' and deck == 'a':
                    if not os.path.exists(link_deck_file):
                        print("Did not find "+nhc_deck_file+" or "
                              +navy_deck_file+" for "+tc)
        # Get model track files
        # currently set up to mimic VSDB verification
        # which uses model track data initialized
        # in storm dates
        if os.path.exists(link_bdeck_file):
            tc_start_date, tc_end_date = get_tc_info.get_tc_dates(
                link_bdeck_file
            )
            tc_time_info_dict = get_time_info(
                tc_start_date[0:8], tc_end_date[0:8],
                tc_start_date[-2:], tc_end_date[-2:],
                '21600', ['00'], 'INIT'
            )
            for model in model_list:
                model_idx = model_list.index(model)
                model_num = model_idx + 1
                model_dir = model_dir_list[model_idx]
                model_hpss_dir = model_hpss_dir_list[model_idx]
                model_file_format = (
                    RUN_abbrev_model_file_format_list[model_idx]
                )
                model_atcf_name = (
                    RUN_abbrev_model_atcf_name_list[model_idx]
                )
                link_model_dir = os.path.join(cwd, 'data', model)
                if not os.path.exists(link_model_dir):
                    os.makedirs(link_model_dir)
                    os.makedirs(os.path.join(link_model_dir, 'HPSS_jobs'))
                for time in tc_time_info_dict:
                    valid_time = time['valid_time']
                    init_time = time['init_time']
                    lead = time['lead']
                    if init_time.strftime('%H') not in RUN_abbrev_fcyc_list:
                        continue
                    elif valid_time.strftime('%H') not in RUN_abbrev_vhr_list:
                        continue
                    else:
                        if 'NCEPPROD' in model_hpss_dir:
                            RUN_model_data_run_hpss = 'NO'
                        else:
                            RUN_model_data_run_hpss = model_data_run_hpss
                        link_track_file = os.path.join(
                           link_model_dir,
                           format_filler('track.{init?fmt=%Y%m%d%H}.dat',
                                          valid_time, init_time, '00')
                        )
                        if not os.path.exists(link_track_file):
                            if model_file_format != 'ADECK':
                                get_model_file(valid_time, init_time, lead,
                                               model, model_dir,
                                               model_file_format,
                                               RUN_model_data_run_hpss,
                                               model_hpss_dir, link_model_dir,
                                              'track.{init?fmt=%Y%m%d%H}.dat')
                            if not os.path.exists(link_track_file) \
                                    and os.path.exists(link_adeck_file):
                                print("Going to try to make "
                                      +link_track_file+" from adeck file "
                                      +link_adeck_file+" for "+model+" "
                                      +"searching for ATCF name "
                                      +model_atcf_name+" and init time "
                                      +init_time.strftime('%Y%m%d%H'))
                                try:
                                    adeck_grep = subprocess.check_output(
                                        'grep -R "'+model_atcf_name+'" '
                                        +link_adeck_file+' | grep "'
                                        +init_time.strftime('%Y%m%d%H')+'"',
                                        shell=True, encoding='UTF-8'
                                    )
                                    if len(adeck_grep) > 0:
                                        with open(link_track_file, 'w') as ltf:
                                             ltf.write(adeck_grep)
                                except:
                                    print("WARNING: Could not make "
                                          +link_track_file+" from adeck file "
                                          +link_adeck_file)
                                    pass
                            ## Check to make sure listed ATCF name in the file
                            ## and do replacements
                            if os.path.exists(link_track_file):
                                try:
                                    model_atcf_name_grep = (
                                        subprocess.check_output(
                                            'grep -R "'+model_atcf_name+'" '
                                             +link_track_file, shell=True,
                                             encoding='UTF-8'
                                        )
                                    )
                                    model_tmp_atcf_name = (
                                        'M'+str(model_num).zfill(3)
                                    )
                                    print("Replacing "+model+" ATCF name "
                                          +model_atcf_name+" with "
                                          +model_tmp_atcf_name+" in "
                                          +link_track_file)
                                    os.system('sed -i s/'+model_atcf_name+'/'
                                              +model_tmp_atcf_name+'/g '
                                              +link_track_file)
                                except:
                                     print("WARNING: "+model_atcf_name+" "
                                           +"ATCF name for "+model+" not in "
                                           +link_track_file)
                                     pass
elif RUN == 'maps2d':
    # Read in RUN related environment variables
    global_archive = os.environ['global_archive']
    obdata_dir = os.environ['obdata_dir']
    RUN_abbrev_plot_diff = os.environ[RUN_abbrev+'_plot_diff']
    RUN_abbrev_anl_file_format_list = (
        os.environ[RUN_abbrev+'_anl_file_format_list'].split(' ')
    )
    RUN_abbrev_model2model_forecast_anl_diff = os.environ[
        RUN_abbrev+'_model2model_forecast_anl_diff'
    ]
    RUN_abbrev_model2obs_use_ceres = os.environ[
        RUN_abbrev+'_model2obs_use_ceres'
    ]
    RUN_abbrev_model2obs_use_monthly_mean = os.environ[
        RUN_abbrev+'_model2obs_use_monthly_mean'
    ]
    # Get model forecast, analysis, and observation files
    # for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_make_met_data_by = os.environ[
            RUN_abbrev_type+'_make_met_data_by'
        ]
        RUN_abbrev_type_hour_list = os.environ[
            RUN_abbrev_type+'_hour_list'
        ].split(' ')
        RUN_abbrev_type_forecast_to_plot_list = os.environ[
            RUN_abbrev_type+'_forecast_to_plot_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_hour_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_hour_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_hour_inc'
        ]
        # Make forecast hour list
        forecast_to_plot_fhr_list = []
        for forecast_to_plot in RUN_abbrev_type_forecast_to_plot_list:
            if forecast_to_plot == 'anl':
                forecast_to_plot_fhr_list.append([forecast_to_plot])
            elif forecast_to_plot[0] == 'f':
                forecast_to_plot_fhr_list.append([forecast_to_plot[1:]])
            elif forecast_to_plot[0] == 'd':
                fhr4 = int(forecast_to_plot[1:]) * 24
                fhr3 = str(fhr4 - 6)
                fhr2 = str(fhr4 - 12)
                fhr1 = str(fhr4 - 18)
                fhr0 = str(fhr4 - 24)
                forecast_to_plot_fhr_list.append([fhr1, fhr2, fhr3, str(fhr4)])
        # Get model forecast, analysis, observation files
        # for all forecast_to_plot
        for forecast_to_plot in RUN_abbrev_type_forecast_to_plot_list:
            forecast_to_plot_idx = (
                RUN_abbrev_type_forecast_to_plot_list.index(forecast_to_plot)
            )
            fhr_list = (
                forecast_to_plot_fhr_list[forecast_to_plot_idx]
            )
            # Get date and time information for RUN_type
            RUN_abbrev_type_time_info_dict = get_time_info(
                start_date, end_date, RUN_abbrev_type_start_hr,
                RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
                fhr_list,
                RUN_abbrev_type_make_met_data_by
            )
            # Get forecast, analysis, observation files for each model
            for model in model_list:
                model_idx = model_list.index(model)
                model_dir = model_dir_list[model_idx]
                model_file_format = model_file_format_list[model_idx]
                model_hpss_dir = model_hpss_dir_list[model_idx]
                anl_file_format = RUN_abbrev_anl_file_format_list[model_idx]
                link_model_data_dir = os.path.join(cwd, 'data', model)
                if not os.path.exists(link_model_data_dir):
                    os.makedirs(link_model_data_dir)
                    os.makedirs(os.path.join(link_model_data_dir, 'HPSS_jobs'))
                # Get model forecast files
                for time in RUN_abbrev_type_time_info_dict:
                    valid_time = time['valid_time']
                    init_time = time['init_time']
                    lead = time['lead']
                    if RUN_abbrev_type_make_met_data_by == 'INIT':
                        hour = init_time.strftime('%H')
                    elif RUN_abbrev_type_make_met_data_by == 'VALID':
                        hour = valid_time.strftime('%H')
                    if hour not in RUN_abbrev_type_hour_list:
                        continue
                    else:
                        if forecast_to_plot == 'anl':
                            ftp_file_format = anl_file_format
                            ftp_link_file_format = (
                                'anl.{'+RUN_abbrev_type_make_met_data_by \
                                .lower()+'?fmt=%Y%m%d%H}'
                            )
                            ftp_lead = 'anl'
                        else:
                            ftp_file_format = model_file_format
                            ftp_link_file_format = (
                                'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}'
                            )
                            ftp_lead = lead
                        get_model_file(valid_time, init_time, ftp_lead,
                                       model, model_dir, ftp_file_format,
                                       model_data_run_hpss, model_hpss_dir,
                                       link_model_data_dir,
                                       ftp_link_file_format)
                        model_fcst_ftp_lead_file = os.path.join(
                            link_model_data_dir, format_filler(
                                ftp_link_file_format, valid_time, init_time,
                                ftp_lead
                             )
                        )
                        # Get observation files if needed
                        if RUN_type == 'model2model':
                            if RUN_abbrev_model2model_forecast_anl_diff \
                                    == 'YES':
                                obtype_list = [model+'_anl']
                            else:
                                obtype_list = [model]
                        elif RUN_type == 'model2obs':
                            obtype_list = ['gpcp', 'ghcn_cams']
                            if RUN_abbrev_model2obs_use_ceres == 'YES':
                                obtype_list.append('ceres')
                            else:
                                obtype_list.extend(
                                    ['clwp', 'nvap', 'rad_isccp', 'rad_srb2']
                                )
                            link_obs_dir = os.path.join(cwd, 'data', 'obs')
                            if not os.path.exists(link_obs_dir):
                                os.makedirs(link_obs_dir)
                        for obtype in obtype_list:
                            model_fcst_ftp_files_filename = os.path.join(
                                link_model_data_dir,
                                RUN_type+'_fcst_'+model+'_obs_'+obtype+'_'
                                +forecast_to_plot+'_fcst_file_list.txt'
                            )
                            model_obs_ftp_files_filename = os.path.join(
                                link_model_data_dir,
                                RUN_type+'_fcst_'+model+'_obs_'+obtype+'_'
                                +forecast_to_plot+'_obs_file_list.txt'
                            )
                            if obtype == model:
                                model_obs_ftp_lead_file = (
                                    model_fcst_ftp_lead_file
                                )
                            elif obtype == model+'_anl':
                                get_model_file(valid_time, valid_time, 'anl',
                                               model, model_dir,
                                               anl_file_format,
                                               model_data_run_hpss,
                                               model_hpss_dir,
                                               link_model_data_dir,
                                               'anl.{valid?fmt=%Y%m%d%H}')
                                model_obs_ftp_lead_file = os.path.join(
                                    link_model_data_dir, format_filler(
                                        'anl.{valid?fmt=%Y%m%d%H}', valid_time,
                                        valid_time, 'anl'
                                    )
                                )
                            else:
                                link_obtype_dir = os.path.join(link_obs_dir,
                                                               obtype)
                                if not os.path.exists(link_obtype_dir):
                                    os.makedirs(link_obtype_dir)
                                YYYY = valid_time.strftime('%Y')
                                B = valid_time.strftime('%B')[0:3]
                                if obtype in ['clwp', 'nvap', 'rad_isccp',
                                              'rad_srb2']:
                                    obtype_dir = os.path.join(
                                        obdata_dir, 'vsdb_climo_data',
                                        'CF_compliant'
                                    )
                                    obtype_filename = obtype+'_'+B+'.nc'
                                else:
                                    if RUN_abbrev_model2obs_use_monthly_mean \
                                            == 'YES':
                                        obtype_dir = os.path.join(
                                            obdata_dir, obtype, 'monthly_mean'
                                        )
                                        obtype_filename = (
                                            obtype+'_'+B+YYYY+'.nc'
                                        )
                                        if not os.path.exists(
                                                os.path.join(obtype_dir,
                                                             obtype_filename)
                                        ):
                                            print(
                                                "WARNING: "
                                                +os.path.join(obtype_dir,
                                                              obtype_filename)
                                                +" does not exist. Will try "
                                                +"substituting climo file "
                                                +os.path.join(obdata_dir,
                                                              obtype,
                                                              'monthly_climo',
                                                              obtype+'_'+B
                                                              +'.nc')
                                            )
                                            obtype_dir = os.path.join(
                                                obdata_dir, obtype,
                                                'monthly_climo'
                                            )
                                            obtype_filename = (
                                                obtype+'_'+B+'.nc'
                                            )
                                    else:
                                        obtype_dir = os.path.join(
                                            obdata_dir, obtype, 'monthly_climo'
                                        )
                                        obtype_filename = obtype+'_'+B+'.nc'
                                obtype_file = os.path.join(obtype_dir,
                                                           obtype_filename)
                                link_obtype_file = os.path.join(
                                    link_obtype_dir, obtype_filename
                                )
                                model_obs_ftp_lead_file = link_obtype_file
                                if not os.path.exists(link_obtype_file):
                                    if os.path.exists(obtype_file):
                                        os.system('ln -sf '+obtype_file+' '
                                                  +link_obtype_file)
                                    else:
                                        print("WARNING: "+obtype_file+" does "
                                              +"not exist")
                            # Add to file list
                            if os.path.exists(model_fcst_ftp_lead_file) \
                                    and \
                                    os.path.exists(model_obs_ftp_lead_file):
                                with open(model_fcst_ftp_files_filename,
                                          'a') as \
                                        fcst_files:
                                    fcst_files.write(
                                        model_fcst_ftp_lead_file+'\n'
                                    )
                                with open(model_obs_ftp_files_filename,
                                          'a') as \
                                        obs_files:
                                    obs_files.write(
                                        model_obs_ftp_lead_file+'\n'
                                    )
elif RUN == 'mapsda':
    # Read in RUN related environment variables
    RUN_abbrev_gdas_model_file_format_list = os.environ[
        RUN_abbrev+'_gdas_model_file_format_list'
    ].split(' ')
    RUN_abbrev_gdas_anl_file_format_list = os.environ[
        RUN_abbrev+'_gdas_anl_file_format_list'
    ].split(' ')
    RUN_abbrev_ens_model_dir_list = os.environ[
        RUN_abbrev+'_ens_model_dir_list'
    ].split(' ')
    RUN_abbrev_ens_model_data_run_hpss = os.environ[
        RUN_abbrev+'_ens_model_data_run_hpss'
    ]
    # Get model forecast and truth files for each option in RUN_type_list
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        # Read in RUN_type environment variables
        RUN_abbrev_type_make_met_data_by = os.environ[
            RUN_abbrev_type+'_make_met_data_by'
        ]
        RUN_abbrev_type_hour_list = os.environ[
            RUN_abbrev_type+'_hour_list'
        ].split(' ')
        RUN_abbrev_type_guess_hour = os.environ[
            RUN_abbrev_type+'_guess_hour'
        ]
        RUN_abbrev_type_model_file_format_list = os.environ[
            RUN_abbrev_type+'_model_file_format_list'
        ].split(' ')
        RUN_abbrev_type_start_hr = os.environ[
            RUN_abbrev_type+'_hour_beg'
        ]
        RUN_abbrev_type_end_hr = os.environ[
            RUN_abbrev_type+'_hour_end'
        ]
        RUN_abbrev_type_hr_inc = os.environ[
            RUN_abbrev_type+'_hour_inc'
        ]
        # Get date and time information for RUN_type
        RUN_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, RUN_abbrev_type_start_hr,
            RUN_abbrev_type_end_hr, RUN_abbrev_type_hr_inc,
            [RUN_abbrev_type_guess_hour],
            RUN_abbrev_type_make_met_data_by
        )
        for model in model_list:
            model_idx = model_list.index(model)
            model_hpss_dir = model_hpss_dir_list[model_idx]
            model_file_format = RUN_abbrev_type_model_file_format_list[
                model_idx
            ]
            link_model_data_dir = os.path.join(cwd, 'data', model)
            if not os.path.exists(link_model_data_dir):
                os.makedirs(link_model_data_dir)
                os.makedirs(os.path.join(link_model_data_dir, 'HPSS_jobs'))
            # Get RUN_type gdas files
            if RUN_type == 'gdas':
                model_dir = model_dir_list[model_idx]
                anl_file_format = RUN_abbrev_gdas_anl_file_format_list[
                    model_idx
                ]
                obtype = model+'_anl'
                # Get model guess and analysis files
                for time in RUN_abbrev_type_time_info_dict:
                    valid_time = time['valid_time']
                    init_time = time['init_time']
                    lead = time['lead']
                    if RUN_abbrev_type_make_met_data_by == 'INIT':
                        hour = init_time.strftime('%H')
                    elif RUN_abbrev_type_make_met_data_by == 'VALID':
                        hour = valid_time.strftime('%H')
                    if hour not in RUN_abbrev_type_hour_list:
                        continue
                    else:
                        get_model_file(valid_time, init_time, lead,
                                       model, model_dir, model_file_format,
                                       model_data_run_hpss, model_hpss_dir,
                                       link_model_data_dir,
                                       'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}')
                        model_fcst_file = os.path.join(
                            link_model_data_dir, format_filler(
                                'f{lead?fmt=%3H}.{init?fmt=%Y%m%d%H}',
                                valid_time, init_time, lead
                             )
                        )
                        get_model_file(valid_time, valid_time, 'anl',
                                       model, model_dir, anl_file_format,
                                       model_data_run_hpss, model_hpss_dir,
                                       link_model_data_dir,
                                       'anl.{valid?fmt=%Y%m%d%H}')
                        model_obs_file = os.path.join(
                            link_model_data_dir, format_filler(
                                'anl.{valid?fmt=%Y%m%d%H}',
                                valid_time, valid_time, 'anl'
                             )
                        )
                        model_fcst_files_filename = os.path.join(
                            link_model_data_dir,
                            RUN_type+'_fcst_'+model+'_obs_'+obtype+'_fhr'
                            +lead+'_fcst_file_list.txt'
                        )
                        model_obs_files_filename = os.path.join(
                            link_model_data_dir,
                             RUN_type+'_fcst_'+model+'_obs_'+obtype+'_fhr'
                             +lead+'_obs_file_list.txt'
                        )
                        # Add to file list
                        if os.path.exists(model_fcst_file) \
                                and \
                                os.path.exists(model_obs_file):
                            with open(model_fcst_files_filename,
                                      'a') as \
                                    fcst_files:
                                fcst_files.write(
                                    model_fcst_file+'\n'
                                )
                            with open(model_obs_files_filename,
                                      'a') as \
                                    obs_files:
                                obs_files.write(
                                    model_obs_file+'\n'
                                )
            # Get RUN_type ens files
            if RUN_type == 'ens':
                model_dir = RUN_abbrev_ens_model_dir_list[model_idx]
                exisiting_file_list = ''
                for ens_file_type in ['mean', 'spread']:
                    ens_model_file_format = model_file_format.replace(
                        '[mean,spread]', ens_file_type
                    )
                    exisiting_file_list = ''
                    for time in RUN_abbrev_type_time_info_dict:
                        valid_time = time['valid_time']
                        init_time = time['init_time']
                        lead = time['lead']
                        if RUN_abbrev_type_make_met_data_by == 'INIT':
                            hour = init_time.strftime('%H')
                        elif RUN_abbrev_type_make_met_data_by == 'VALID':
                            hour = valid_time.strftime('%H')
                        if hour not in RUN_abbrev_type_hour_list:
                            continue
                        else:
                            get_model_file(valid_time, init_time, lead,
                                           model, model_dir,
                                           ens_model_file_format,
                                           RUN_abbrev_ens_model_data_run_hpss,
                                           model_hpss_dir,
                                           link_model_data_dir,
                                           'atmf{lead?fmt=%3H}.ens'
                                           +ens_file_type+'.'
                                           +'{init?fmt=%Y%m%d%H}.nc')
                            link_ens_file = os.path.join(
                                link_model_data_dir, format_filler(
                                    'atmf{lead?fmt=%3H}.ens'+ens_file_type+'.'
                                    +'{init?fmt=%Y%m%d%H}.nc', valid_time,
                                    init_time, lead
                                )
                            )
                            if os.path.exists(link_ens_file):
                                exisiting_file_list= (exisiting_file_list
                                                      +link_ens_file+' ')
                    avg_file = os.path.join(link_model_data_dir,
                                            format_filler('atmf{lead?fmt=%3H}'
                                                          '.ens'+ens_file_type
                                                          +'.nc', valid_time,
                                                          init_time, lead))
                    print("Creating average files for "+model+" "
                          +"ens"+ens_file_type+" from available data. "
                          +"Saving as "+avg_file)
                    ncea = subprocess.check_output(
                        'which ncea', shell=True, encoding='UTF-8'
                    ).replace('\n', '')
                    if '.nc4' in model_file_format:
                        process_vars = ''
                    else:
                        process_vars = (
                            ' -v tmp,ugrd,vgrd,spfh,pressfc,o3mr,clwmr '
                        )
                    if exisiting_file_list != '':
                        os.system(ncea+' '+exisiting_file_list+' -o '
                                  +avg_file+process_vars)

print("END: "+os.path.basename(__file__))
