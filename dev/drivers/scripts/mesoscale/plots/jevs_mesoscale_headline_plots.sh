#PBS -S /bin/bash
#PBS -N jevs_mesoscale_headline_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l debug=true
#PBS -V

set -x
export model=evs
export machine=WCOSS2

# ECF Settings
export RUN_ENVIR=nco
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=NO
export SENDDBN=YES
export SENDDBN_NTC=
export job=${PBS_JOBNAME:-jevs_mesoscale_headline_plots}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export USE_CFP=YES
export nproc=128

# General Verification Settings
export NET="evs"
export STEP="plots"
export COMPONENT="mesoscale"
export RUN="atmos"
export VERIF_CASE="headline"
export MODELNAME=${COMPONENT}

# EVS Settings
export HOMEevs="/lfs/h2/emc/vpppg/noscrub/$USER/EVS"
export HOMEevs=${HOMEevs:-${PACKAGEROOT}/evs.${evs_ver}}
export config=$HOMEevs/parm/evs_config/mesoscale/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}

# Load Modules
source $HOMEevs/versions/run.ver

source /usr/share/lmod/lmod/init/sh
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export MET_PLUS_PATH="/apps/ops/prod/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/prod/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

# Developer Settings
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/stats
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export cyc=$(date -d "today" +"%H")

# Job Settings and Run
. ${HOMEevs}/jobs/${COMPONENT}/plots/JEVS_MESOSCALE_PLOTS
