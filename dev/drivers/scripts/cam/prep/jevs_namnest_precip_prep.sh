#PBS -S /bin/bash
#PBS -N jevs_namnest_precip_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=10:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l debug=true
#PBS -V

set -x
export model=evs
module reset
export machine=WCOSS2

# ECF Settings
export RUN_ENVIR=nco
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=YES
export SENDDBN_NTC=
export job=${PBS_JOBNAME:-jevs_namnest_precip_prep}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export USE_CFP=NO
export nproc=128

# General Verification Settings
export NET="evs"
export STEP="prep"
export COMPONENT="cam"
export RUN="atmos"
export VERIF_CASE="precip"
export MODELNAME="namnest"

# EVS Settings
export HOMEevs="/lfs/h2/emc/vpppg/noscrub/$USER/EVS"
export HOMEevs=${HOMEevs:-${PACKAGEROOT}/evs.${evs_ver}}
export config=$HOMEevs/parm/evs_config/cam/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# Load Modules
source $HOMEevs/versions/run.ver
source /usr/share/lmod/lmod/init/sh
module reset
source $HOMEevs/modulefiles/$COMPONENT/$COMPONENT_$STEP.sh
export MET_bin_exec="bin"
export MET_PLUS_PATH="/apps/ops/para/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

# Developer Settings
export DATA=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp/${jobid:?}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
export cyc=$(date -d "today" +"%H")

# Job Settings and Run
. ${HOMEevs}/jobs/cam/prep/JEVS_CAM_PREP
