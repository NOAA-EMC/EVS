import os
import sys
import subprocess
import re
import configparser
from datetime import datetime, timedelta

###################################################################
# THERE IS NO NEED FOR USERS TO MODIFY THIS SCRIPT.
#
# Run this script: python drive_EVS.py [path to config file]
# Example: python drive_EVS.py config/config.EVS
###################################################################

def error_and_exit(message):
    print(f"{message} EXITING!")
    sys.exit(1)

#--------------------------------------

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

#--------------------------------------

def create_job_script(
    step, user_config, machine_name, comp_name, dev_driver, evsdate, jobfile, logfile
):
    for check_file in [jobfile, logfile]:
        if os.path.exists(check_file):
            try:
                print(f"Removing existing file {check_file}")
                os.remove(check_file)
            except OSError as e:
                error_and_exit(
                    f"Could not removed existing log file {check_file}: {e}"
                )
    # --- Define Variables ---
    reset_value_dict = {}
    if "PREP" in step:
        component_idx = (
            user_config["INPUT_OUTPUT"]\
            ["component_list"].split(" ").index(comp_name)
        )
        reset_value_dict["component_list"] = comp_name
    # Set EVS home location
    current_dir = os.getcwd()
    HOMEevs = os.path.abspath(
        os.path.join(current_dir, os.pardir, os.pardir)
    )
    print(f"HOMEevs: {HOMEevs}")
    # Set job specifics
    jobname = jobfile.rpartition("/")[2].replace(".sh", "")
    print(f"jobname: {jobname}")
    job_jevs_script = os.path.join(
        HOMEevs, "dev/drivers/scripts", step.lower(), comp_name, f"{dev_driver}.sh"
    )
    print(f"job_jevs_script: {job_jevs_script}")

    account = user_config["MACHINE"]["queue_account"]
    if "jevs_prep_global_det_atmos" == dev_driver:
        bin_bash = "/bin/bash"
        queue = "dev"
        walltime = "00:45:00"
        place = "place=shared"
        nodes = "1"
        nproc = "1"
        memory = "125GB"

    # Set machine specifics
    account = user_config["MACHINE"]["queue_account"]
    sh = open(jobfile, "w")
    submission_command = None

    # --- Write the machine-specific part ---
    if machine_name == 'WCOSS2':
        fix_files = (
            "/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
        )
        sh.write(f"#PBS -N {jobname}\n")
        sh.write(f"#PBS -o {logfile}\n")
        sh.write(f"#PBS -e {logfile}\n")
        sh.write(f"#PBS -S {bin_bash}\n")
        sh.write(f"#PBS -q {queue}\n")
        sh.write(f"#PBS -A {account}\n")
        sh.write(f"#PBS -l walltime={walltime}\n")
        sh.write(f"#PBS -l {place},select={nodes}:ncpus={nproc}:mem={memory}\n")
        sh.write("#PBS -l debug=true\n")
        submission_command = f"qsub {jobfile}"

    sh.write("\n")
    sh.write("# Link in fix files\n")
    sh.write(f"rm -rf {HOMEevs}/fix\n")
    sh.write(f"ln -sf {fix_files} {HOMEevs}/fix\n")

    sh.write("\n")
    sh.write("# Add INITDATE from config file\n")
    line=f"export INITDATE={evsdate}"
    clean_line = line.replace("-", "")
    sh.write(f"{clean_line}\n")

    sh.write("\n")
    sh.write("# Add HOMEevs\n")
    sh.write(f"export HOMEevs={HOMEevs}\n")

    # Read the contents of the source file
    with open(job_jevs_script, "r") as source_file:
        source_contents = source_file.read()

    # Write (or append) those contents into your target file
    sh.write("\n# --- Appended Content Start ---\n")
    sh.write(source_contents)
    sh.write("\n# --- Appended Content End ---\n")

    sh.close()

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

### Check machine
ALLOWED_MACHINES = ["GAEAC6", "WCOSS2", "URSA"]
machine = config["MACHINE"]["name"].upper()
check_machine(machine)
print(f"machine: {machine}")

### Create run directories (DATAROOT, /jobs, /logs)
DATAROOT_dirs = [config["INPUT_OUTPUT"]["DATAROOT"]]
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "jobs"))
DATAROOT_dirs.append(os.path.join(config["INPUT_OUTPUT"]["DATAROOT"], "logs"))
for DATAROOT_dir in DATAROOT_dirs:
    if not os.path.exists(DATAROOT_dir):
        print(f"Creating {DATAROOT_dir}")
        os.makedirs(DATAROOT_dir, exist_ok=True)
        print("")
print(f"DATAROOT: {DATAROOT_dirs[0]}\n")

### Run jobs
component_list = config["INPUT_OUTPUT"]["component_list"].split(" ")
print(f"component_list: {component_list}\n")
# Submit PREP, STATS, or PLOTS jobs
for step_switch, step_switch_value in config["RUN"].items():
    if step_switch_value == "YES":
        if "PREP" in step_switch:
        	### Convert initdate strings into date objects
        	initdate_str = config["DATES"]["initdate"]
        	initdate = None
        	try:
            		# Parse initdate from multiple date formats
            		for fmt in ('%Y-%m-%d', '%Y%m%d'):
                		try:
                    			initdate = datetime.strptime(initdate_str, fmt).date()
                    			break
                		except ValueError:
                    			pass
            		if initdate is None:
                		raise ValueError("Invalid initdate format in given config file")
        	except ValueError:
            		error_and_exit(
                		"Invalid initdate format. Please use yyyymmdd or yyyy-mm-dd."
            		)
        	print(f"EVS initdate for {step_switch}: {initdate} (Type: {type(initdate)})")
        	print("")

        	for component in component_list:
        		component_caps=component.upper()
        		for comp_switch, comp_switch_value in config[component_caps].items():
        			if comp_switch_value == "YES":
        				if "prep" in comp_switch:
        					print(
        						f"--- Generating scripts for {comp_switch}, initdate {initdate:%Y%m%d} ---"
        					)
        					job_script = os.path.join(
        						os.path.join(config["INPUT_OUTPUT"]["DATAROOT"]), "jobs",
        						f"submit_{comp_switch}_{initdate:%Y%m%d}.sh"
                				)
        					#print(f"job_script: {job_script}")
        					log_script = job_script.replace("jobs", "logs").replace(".sh", ".log")
        					#print(f"log_script: {log_script}")
        					create_job_script(
        						step_switch.replace("RUN_", ""), config, machine, component,
        						comp_switch, initdate, job_script, log_script
        					)

        if ("STATS" in step_switch or "PLOTS" in step_switch):
                ### Convert vdate strings into date objects
                vdate_str = config["DATES"]["vdate"]
                vdate = None
                try:
                        # Parse vdate from multiple date formats
                        for fmt in ('%Y-%m-%d', '%Y%m%d'):
                                try:
                                        vdate = datetime.strptime(vdate_str, fmt).date()
                                        break
                                except ValueError:
                                        pass
                        if vdate is None:
                                raise ValueError("Invalid vdate format in given config file")
                except ValueError:
                        error_and_exit(
                                "Invalid vdate format. Please use yyyymmdd or yyyy-mm-dd."
                        )
                print(f"EVS vdate for {step_switch}: {vdate} (Type: {type(vdate)})")
                print("")

