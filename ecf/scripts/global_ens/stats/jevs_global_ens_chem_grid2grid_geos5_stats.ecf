#PBS -N jevs_global_ens_chem_g2g_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=1:mpiprocs=1:mem=40G
#PBS -l debug=true
#PBS -o g2g_ge5out.t00z
#PBS -e g2g_ge5err.t00z
#PBS -V

set -x 
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver

##%include <head.h>
##%include <envir-p1.h>

############################################################
# Load modules
############################################################
module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load cfp/${cfp_ver}
module load gsl/${gsl_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load netcdf/${netcdf_ver}
module load python/${python_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}

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
export OBTTYPE=geos5
export VARS="taod daod bcaod ocaod suaod ssaod"
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
