#PBS -N jevs_rtofs_argo_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=03:00:00
#PBS -l select=1:ncpus=1:mem=500GB
#PBS -l debug=true

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################
set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver

module reset
#export HPC_OPT=/apps/ops/prod/libs
#module use /apps/ops/prod/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load rsync/${rsync_ver}
module list

# specify environment variables
export NET=evs
export STEP=stats
export RUN=argo
export RUNupper=ARGO
export VERIF_CASE=grid2obs
export VARS="temp psal"
export COMPONENT=rtofs

# set up VDATE and COMIN and COMOUT
export VDATE=$(date --date="3 days ago" +%Y%m%d)

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
export COMINfcst=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/prep/$COMPONENT
export COMINclimo=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/climos/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTfinal=$COMOUT/$STEP/$COMPONENT/$COMPONENT.$VDATE
export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT
export ARCHevs=/lfs/h2/emc/vpppg/noscrub/$USER/stat_archive/RTOFS

export maillist=${maillist:-'geoffrey.manikin@noaa.gov,lichuan.chen@noaa.gov'}

# call j-job
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_RTOFS_STATS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to create stat
#          files for RTOFS forecast verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
#%end
