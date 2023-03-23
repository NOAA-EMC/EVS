'''
Program Name: get_machine.py
Contact(s): Shannon Shields
Abstract: This script is run by set_up_seasonal_evs.sh.
          It gets the name of the machine being
          run on by checking environment variables "machine"
          or "MACHINE". If not does matching based on environment
          variable "HOSTNAME" or output from hostname executable.
'''

import sys
import os
import re
import subprocess

print("BEGIN: "+os.path.basename(__file__))

EMC_evs_machine_list = [
    'HERA', 'ORION', 'WCOSS_C'
]

# Read in environment variables
if not 'HOSTNAME' in list(os.environ.keys()):
    hostname = subprocess.check_output(
        'hostname', shell=True
    ).replace('\n', '')
else:
    hostname = os.environ['HOSTNAME']

# Get machine name
for env_var in ['machine', 'MACHINE']:
    if env_var in os.environ:
        if os.environ[env_var] in EMC_evs_machine_list:
            print("Found environment variable "
                  +env_var+"="+os.environ[env_var])
            machine = os.environ[env_var]
            break
if 'machine' not in vars():
    hera_match = re.match(re.compile(r"^hfe[0-9]{2}$"), hostname)
    orion_match = re.match(
        re.compile(r"^Orion-login-[0-9]{1}.HPC.MsState.Edu$"), hostname
    )
    #cactus_match = re.match(re.compile(r"^clogin[0-9]{1}$"), hostname)
    #dogwood_match = re.match(re.compile(r"^dlogin[0-9]{1}$"), hostname)
    wcoss2_match = hostname
    if hera_match:
        machine = 'HERA'
    elif orion_match:
        machine = 'ORION'
    #elif cactus_match or dogwood_match:
        #machine = 'WCOSS_C'
    elif wcoss2_match:
        machine = 'WCOSS_C'
    else:
        print("Cannot find match for "+hostname)
        sys.exit(1)

# Write to machine config file
if not os.path.exists('config.machine'):
    with open('config.machine', 'a') as file:
        file.write('#!/bin/sh\n')
        file.write('echo "BEGIN: config.machine"\n')
        file.write('echo "Setting machine='+'"'+machine+'""\n')
        file.write('export machine='+'"'+machine+'"\n')
        file.write('echo "END: config.machine"')

print("Working "+hostname+" on "+machine)

print("END: "+os.path.basename(__file__))
