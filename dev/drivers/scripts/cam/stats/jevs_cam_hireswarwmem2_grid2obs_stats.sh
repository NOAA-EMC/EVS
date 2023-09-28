#PBS -S /bin/bash
#PBS -N jevs_cam_hireswarwmem2_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:45:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=32GB
#PBS -l debug=true
#PBS -V

set -x
export model=evs
export machine=WCOSS2

# ECF Settings
export SENDMAIL=YES
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=YES
export SENDDBN_NTC=
export job=${PBS_JOBNAME:-jevs_cam_hireswarwmem2_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export USE_CFP=YES
export nproc=128

# General Verification Settings
export NET="evs"
export STEP="stats"
export COMPONENT="cam"
export RUN="atmos"
export VERIF_CASE="grid2obs"
export MODELNAME="hireswarwmem2"

# EVS Settings
export HOMEevs="/lfs/h2/emc/vpppg/noscrub/$USER/EVS"
export HOMEevs=${HOMEevs:-${PACKAGEROOT}/evs.${evs_ver}}
export config=$HOMEevs/parm/evs_config/cam/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

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
export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMROOT=/lfs/h2/emc/vpppg/noscrub/${USER}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export cyc=$(date -d "today" +"%H")
export maillist="alicia.bentley@noaa.gov,marcel.caron@noaa.gov"

# Job Settings and Run
. ${HOMEevs}/jobs/JEVS_CAM_STATS
