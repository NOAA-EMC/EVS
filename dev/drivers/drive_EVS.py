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
# Example: python drive_EVS.py ../parm/config.EVS
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
                os.remove(check_file)
            except OSError as e:
                error_and_exit(
                    f"Could not removed existing job or log file: {check_file}: {e}"
                )
    # --- Define Variables ---
    reset_value_dict = {}
    if "PREP" in step:
        component_idx = (
            user_config["RUN"]["component_list"].split(" ").index(comp_name)
        )
        reset_value_dict["component_list"] = comp_name
    # Set variables from config file
    SENDCOM = [config["INPUT_OUTPUT"]["SENDCOM"]][0]
    SENDMAIL = [config["INPUT_OUTPUT"]["SENDMAIL"]][0]
    KEEPDATA = [config["INPUT_OUTPUT"]["KEEPDATA"]][0]
    MAILTO = [config["INPUT_OUTPUT"]["MAILTO"]][0]
    HOMEevs = [config["INPUT_OUTPUT"]["HOMEevs"]][0]
    DATAROOT = [config["INPUT_OUTPUT"]["DATAROOT"]][0]
    TMPDIR = [config["INPUT_OUTPUT"]["DATAROOT"]][0]
    COMIN_ROOT = [config["INPUT_OUTPUT"]["COMIN_ROOT"]][0]
    COMOUT_ROOT = [config["INPUT_OUTPUT"]["COMOUT_ROOT"]][0]
    print(f"HOMEevs: {HOMEevs}")
    print(f"DATAROOT: {DATAROOT}")
    # Set job specifics
    jobname = jobfile.rpartition("/")[2].replace(".sh", "")
    print(f"jobname: {jobname}")
    if "atmos" in dev_driver:
        run = "atmos"
    elif "wave" in dev_driver:
        run = "wave"

    account = user_config["MACHINE"]["queue_account"]
    if "jevs_prep_global_det_atmos" == dev_driver:
        bin_bash = "/bin/bash"
        queue = "dev"
        walltime = "00:45:00"
        place = "place=shared"
        nodes = "1"
        nproc = "1"
        memory = "125GB"
        vhr="00"

    # Set machine specifics
    account = user_config["MACHINE"]["queue_account"]
    sh = open(jobfile, "w")
    submission_command = None

    # ------------------------------------------------------------------------
    # Machine-specific resource information
    # ------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------
    # General information
    # ------------------------------------------------------------------------
    sh.write("\n")
    sh.write(f"set -x\n")

    sh.write("\n")
    sh.write(f"if [ ! -d {HOMEevs}/exec ]; then\n")
    sh.write(f'	echo "The /exec directory does NOT exist. Building from /sorc now..."\n')
    sh.write(f"	cd {HOMEevs}/sorc\n")
    sh.write(f"	./build.sh\n")
    sh.write(f"fi\n")

    sh.write("\n")
    sh.write(f"if [ ! -d {HOMEevs}/fix ] || [ ! -L {HOMEevs}/fix ]; then\n")
    sh.write(f'	echo "The /fix directory is NOT linked. Linking /fix now..."\n')
    sh.write(f"	ln -sf {fix_files} {HOMEevs}/fix\n")
    sh.write(f"fi\n")

    sh.write("\n")
    sh.write(f"export model=evs\n")
    sh.write(f"export HOMEevs={HOMEevs}\n")

    sh.write("\n")
    sh.write(f"source {HOMEevs}/versions/run.ver\n")
    sh.write("evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)\n")

    sh.write("\n")
    sh.write(f"export KEEPDATA={KEEPDATA}\n")
    sh.write(f"export SENDCOM={SENDCOM}\n")
    sh.write(f"export SENDMAIL={SENDMAIL}\n")
    sh.write(f"export MAILTO={MAILTO}\n")

    sh.write("\n")
    sh.write(f"export envir=prod\n")
    sh.write(f"export NET=evs\n")
    sh.write(f"export STEP={step.lower()}\n")
    sh.write(f"export COMPONENT={component}\n")
    sh.write(f"export RUN={run}\n")

    sh.write("\n")
    sh.write(f"export DATAROOT={DATAROOT}\n")
    sh.write(f"export TMPDIR={DATAROOT}\n")
    sh.write(f"export COMIN={COMIN_ROOT}/$NET/$evs_ver_2d\n")
    sh.write(f"export COMOUT={COMOUT_ROOT}/$NET/$evs_ver_2d/$STEP/$COMPONENT/$RUN\n")

    sh.write("\n")
    line=f"export INITDATE={evsdate}"
    clean_line = line.replace("-", "")
    sh.write(f"{clean_line}\n")

    # ------------------------------------------------------------------------
    # Job-specific information
    # ------------------------------------------------------------------------
    if component == 'global_det' and step.lower() == 'prep' and run == 'atmos':
        sh.write("\n")
        modelname = "cfs cmc cmc_regional dwd fnmoc gfs aigfs jma metfra ukmet ecmwf"
        obsname = "osi_saf ghrsst_ospo ccpa_accum24hr prepbufr_gdas prepbufr_rrfs"
        sh.write(f'export MODELNAME="{modelname}"\n')
        sh.write(f'export OBSNAME="{obsname}"\n')
    else:
        pass

    # ------------------------------------------------------------------------
    # Final machine-specific information
    # ------------------------------------------------------------------------
    if machine_name == 'WCOSS2':
        sh.write(f"export job=${{PBS_JOBNAME:-{dev_driver}}}\n")
        sh.write("export jobid=$job.${PBS_JOBID:-$$}\n")
        sh.write("export SITE=$(cat /etc/cluster_name)\n")
        sh.write(f"export vhr={vhr}\n")
        sh.write("\n")
        sh.write(f"module reset\n")
        sh.write("module load prod_envir/${prod_envir_ver}\n")
        sh.write(f"source {HOMEevs}/dev/modulefiles/{component}/{component}_{step.lower()}.sh\n")
        sh.write(f"module list\n")

    # ------------------------------------------------------------------------
    # Final general information (submit j-job)
    # ------------------------------------------------------------------------
    sh.write("\n")
    sh.write(f"# CALL executable job script here\n")
    sh.write(f"{HOMEevs}/jobs/JEVS_{step}_{component.upper()}\n")

    sh.write("\n")
    sh.write(f"############################################\n")
    sh.write(f"############################################\n")
    sh.write(f"############################################\n")

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

### Run jobs
component_list = config["RUN"]["component_list"].split(" ")
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

            for component in component_list:
                for job_switch, job_switch_value in config[f'{step_switch.replace("RUN_", "")}_{component.upper()}'].items():
                    if job_switch_value == "YES":
                        print(
                            f"--- Generating submission script for {job_switch}, initdate {initdate:%Y%m%d} ---"
                        )
                        job_script = os.path.join(
                            os.path.join(config["INPUT_OUTPUT"]["DATAROOT"]), "jobs",
                            f"submit_{job_switch}_{initdate:%Y%m%d}.sh"
                        )
                        print(f"job_script: {job_script}")
                        log_script = job_script.replace("jobs", "logs").replace(".sh", ".log")
                        print(f"log_script: {log_script}")
                        create_job_script(
                            step_switch.replace("RUN_", ""), config, machine, component,
                            job_switch, initdate, job_script, log_script
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

