#PBS -N jevs_global_ens_gefs_chem_g2g_abi_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=1:mpiprocs=1:mem=10G
#PBS -l debug=true
#PBS -o g2g_abiout.t00z
#PBS -e g2g_abierr.t00z
#PBS -V

set -x 
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

##%include <head.h>
##%include <envir-p1.h>

############################################################
# Load modules
############################################################
module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_stats.sh

module load cray-mpich/${craympich_ver}

module list

export MET_PLUS_PATH="/apps/ops/para/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
export MET_bin_exec=bin

############################################################
# set some variables
############################################################
export cyc=00
echo $cyc
#export envir=prod

export KEEPDATA=YES
export NET=evs
export STEP=stats
export COMPONENT=global_ens
export RUN=chem
export VERIF_CASE=grid2grid
export MODELNAME=gefs
export OBTTYPE=abi
export MET_bin_exec=bin

export run_mpi='yes'
export gather='yes'

export VDATE=$PDYm3

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
export COMINfcst=/lfs/h1/ops/prod/com/gefs/v12.3
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export USHevs=$HOMEevs/ush/$COMPONENT
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/global_ens/stats/JEVS_GLOBAL_ENS_CHEM_GRID2GRID_STATS

##%include <tail.h>
##%manual
#######################################################################
# Purpose: This calculates the stats for the global_ens GEFS-Chem model
#######################################################################
##%end
exit
