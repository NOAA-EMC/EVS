#PBS -N jevs_mesoscale_grid2obs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=4:00:00
#PBS -l place=vscatter:exclhost,select=12:ncpus=128:mem=150GB
#PBS -l debug=true

set -x
export model=evs
module reset
export machine=WCOSS2

# ECF Settings
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=NO
export SENDDBN_NTC=
export SENDMAIL=YES
export job=${PBS_JOBNAME:-jevs_mesoscale_grid2obs_plots}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export USE_CFP=YES
export nproc=64
export evs_run_mode="production"

# General Verification Settings
export envir=prod
export NET="evs"
export STEP="plots"
export COMPONENT="mesoscale"
export RUN="atmos"
export VERIF_CASE="grid2obs"
export MODELNAME=${COMPONENT}

# EVS Settings
export HOMEevs="/lfs/h2/emc/vpppg/noscrub/${USER}/EVS_mesoscale_fixes_v2/EVS"
export HOMEevs=${HOMEevs:-${PACKAGEROOT}/evs.${evs_ver}}
export config=$HOMEevs/parm/evs_config/mesoscale/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}

# Load Modules
source $HOMEevs/versions/run.ver

module reset
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

# Developer Settings
export COMIN=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d/$STEP/$COMPONENT
export vhr=${vhr:-${vhr}}

# Job Settings and Run
. ${HOMEevs}/jobs/JEVS_MESOSCALE_PLOTS
