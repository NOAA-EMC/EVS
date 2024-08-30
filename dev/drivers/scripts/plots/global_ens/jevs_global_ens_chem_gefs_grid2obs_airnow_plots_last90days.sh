#PBS -N jevs_global_ens_chem_gefs_grid2obs_airnow_plots_last90days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter:exclhost,select=5:ncpus=128:ompthreads=1:mem=275GB
#PBS -l debug=true

set -x

cd ${PBS_O_WORKDIR}

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

############################################################
## Load modules
############################################################
############################################################
## Specify environment variables
############################################################
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=NO
export job=${PBS_JOBNAME:-jevs_global_ens_chem_grid2obs_airnow_plots_90days}
export jobid=${job}.${PBS_JOBID:-$$}
export vhr=00

source ${HOMEevs}/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_ens/global_ens_plots.sh

evs_ver_2d=$(echo ${evs_ver} | cut -d'.' -f1-2)

export machine=WCOSS2
export USE_CFP=YES
export nproc=128

export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=global_ens
export RUN=chem
export VERIF_CASE=grid2obs
export DATA_TYPE=airnow
export NDAYS=90

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/${envir}/tmp
export TMPDIR=${DATAROOT}
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}
today=$(cut -c7-14 ${COMROOT}/date/t${vhr}z)
export VDATE_END=$(finddate.sh ${today} d-4)
export COMOUT=/lfs/h2/emc/ptmp/${USER}/${NET}/${evs_ver_2d}/${STEP}/${COMPONENT}/${RUN}.${VDATE_END}

# CALL executable job script here
${HOMEevs}/jobs/JEVS_GLOBAL_ENS_PLOTS

######################################################################
# Purpose: This does the plotting work for the global ensemble chem
#          grid-to-observations airnow for last 90 days
######################################################################
