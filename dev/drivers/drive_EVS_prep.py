import os
import sys
import subprocess
import re
import configparser
from datetime import datetime, timedelta

###################################################################
# THERE IS NO NEED FOR USERS TO MODIFY THIS SCRIPT.
#
# Run this script: python drive_EVS_prep.py [path to config file]
# Example: python drive_EVS_prep.py config/config.prep.global_det
#
###################################################################

def error_and_exit(message):
    print(f"{message} EXITING!")
    sys.exit(1)

def check_machine(config_machine):
    if not 'HOSTNAME' in list(os.environ.keys()):
        hostname = subprocess.check_output(
            'hostname', shell=True, encoding='UTF-8'
        ).replace('\n', '')
    else:
        hostname = os.environ['HOSTNAME']
    ursa_match = re.match(re.compile(r"^ufe0[1-4]{1}$"), hostname)
    gaeac6_match = re.match(re.compile(r"^gaea6[1-8]{1}"), hostname)
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
    if cactus_match or dogwood_match or cactus_match2 or dogwood_match2:
        machine = "WCOSS2"
    elif ursa_match:
        machine = "URSA"
    elif gaeac6_match:
        machine = "GAEAC6"
    else:
        error_and_exit(f"Cannot find match for {hostname}")
    if config_machine != machine:
        error_and_exit(
            f"Machine name in config file is {config_machine}, "
            +f"but found hostname {hostname} matching {machine}.\n"
            +f"Please choose from allowed machines: {', '.join(ALLOWED_MACHINES)}."
        )

###############################################################

### Check for passed config argument
if len(sys.argv) != 2:
    error_and_exit(
        f"{sys.argv[0]} takes 1 command line argument "
        +f"(path to config file), but was given {len(sys.argv)-1}."
    )

### Verifying path to config file
config_path = os.path.abspath(sys.argv[1])
if not os.path.exists(config_path):
    error_and_exit(
        f"ERROR: {config_path} does not exist."
    )

### Parsing config file into sections
print(f"\nParsing config file:\n{config_path}\n")
config = configparser.ConfigParser(interpolation=None)
config.optionxform = str
config.read(config_path)

### Loop through config file to use $var and replace quotes
for section_name in config.sections():
    for name, value in config.items(section_name):
        if "$" in value:
            config[section_name][name] = os.path.expandvars(value)
        if '"' in value:
            config[section_name][name] = value.replace('"', '')

### Create run directories (DATAROOT, /jobs, /logs)
DATAROOT_dirs = [config["INPUT_OUTPUT"]["DATAROOT"]]
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "jobs"))
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "logs"))
for DATAROOT_dir in DATAROOT_dirs:
    if not os.path.exists(DATAROOT_dir):
        print(f"Creating {DATAROOT_dir}")
        os.makedirs(DATAROOT_dir, exist_ok=True)
        print("")

### Convert initdate strings into date objects
start_initdate_str = config["DATES"]["start_initdate"]
end_initdate_str = config["DATES"]["end_initdate"]
start_initdate, end_initdate = None, None
try:
    # Parse start_initdate from multiple date formats
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            start_initdate = datetime.strptime(start_initdate_str, fmt).date()
            break
        except ValueError:
            pass
    # Parse end_initdate from multiple date formats
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            end_initdate = datetime.strptime(end_initdate_str, fmt).date()
            break
        except ValueError:
            pass
    if start_initdate is None or end_initdate is None:
        raise ValueError("Invalid initdate format in given config file")
except ValueError:
    error_and_exit(
        "Invalid initdate format. Please use yyyymmdd or yyyy-mm-dd."
    )
if start_initdate > end_initdate:
    error_and_exit(
        "The start initdate cannot be after the end initdate for prep."
    )
print(f"Successfully parsed initdates from config file:")
print(f"Start initdate: {start_initdate} (Type: {type(start_initdate)})")
print(f"End initdate:   {end_initdate} (Type: {type(end_initdate)})")
print("")

### Check machine
ALLOWED_MACHINES = ["GAEAC6", "WCOSS2", "URSA"]
machine = config["MACHINE"]["name"].upper()
check_machine(machine)


