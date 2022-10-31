'''
Program Name: global_det_atmos_get_machine.py
Contact(s): Mallory Row
Abstract: This script is run by global_det_atmos_set_up.sh.
          It gets the name of the name of the machine being
          run on by checking environment variables "machine"
          or "MACHINE". If not does matching based on environment
          variable "HOSTNAME" or output from hostname executable.
'''

import sys
import os
import re
import subprocess

print("BEGIN: "+os.path.basename(__file__))

supported_machine_list = ['WCOSS2', 'HERA']

# Read in environment variables
if not 'HOSTNAME' in list(os.environ.keys()):
    hostname = subprocess.check_output(
        'hostname', shell=True, encoding='UTF-8'
    ).replace('\n', '')
else:
    hostname = os.environ['HOSTNAME']

# Get machine name
for env_var in ['machine', 'MACHINE']:
    if env_var in os.environ:
        if os.environ[env_var] in supported_machine_list:
            print("Found environment variable "
                  +env_var+"="+os.environ[env_var])
            machine = os.environ[env_var]
            break
if 'machine' not in vars():
    cactus_match = re.match(
        re.compile(r"^clogin[0-9]{2}$"), hostname
    )
    cactus_match2 = re.match(
        re.compile(r"^cdecflow[0-9]{2}$"), hostname
    )
    dogwood_match = re.match(
        re.compile(r"^dlogin[0-9]{2}$"), hostname
    )
    dogwood_match2 = re.match(
        re.compile(r"^ddecflow[0-9]{2}$"), hostname
    )
    hera_match = re.match(re.compile(r"^hfe[0-9]{2}$"), hostname)
    jet_match = re.match(re.compile(r"^fe[0-9]{1}"), hostname)
    orion_match = re.match(
        re.compile(r"^Orion-login-[0-9]{1}.HPC.MsState.Edu$"), hostname
    )
    s4_match = re.match(re.compile(r"s4-submit.ssec.wisc.edu"), hostname)
    if cactus_match or dogwood_match or cactus_match2 or dogwood_match2:
        machine = 'WCOSS2'
    elif hera_match:
        machine = 'HERA'
    elif jet_match:
        machine = 'JET'
    elif orion_match:
        machine = 'ORION'
    elif s4_match:
        machine = 'S4'
    else:
        print("ERROR: Cannot find match for "+hostname)
        sys.exit(1)

# Check out machine is in the supported list
if machine not in supported_machine_list:
    print("ERROR:"+machine+" not in supported machine list: "
          +', '.join(supported_machine_list))
    sys.exit(1)

# Write to machine config file
if not os.path.exists('config.machine'):
    with open('config.machine', 'a') as file:
        file.write('#!/bin/sh\n')
        file.write('echo "BEGIN: config.machine"\n')
        file.write('echo "Setting machine='+'"'+machine+'""\n')
        file.write('export machine='+'"'+machine+'"\n')
        file.write('echo "END: config.machine"')

print("Currently on "+hostname+" on "+machine)

print("END: "+os.path.basename(__file__))
