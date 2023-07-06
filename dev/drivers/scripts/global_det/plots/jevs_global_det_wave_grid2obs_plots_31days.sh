#PBS -N jevs_global_det_wave_grid2obs_plots_31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter,select=1:ncpus=10:mem=50G
#PBS -l debug=true
#PBS -V

set -x

#%include <head.h>
#%include <envir-p1.h>

export model=evs

############################################################
# For dev testing
############################################################
cd $PBS_O_WORKDIR
module reset
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export envir=dev
export RUN_ENVIR=nco
export SENDCOM=YES
export KEEPDATA=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_output/$envir/tmp
export job=${PBS_JOBNAME:-jevs_global_det_wave_grid2obs_plots_31days}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)
############################################################

############################################################
# Load modules
############################################################
module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}

module list

# Set job information
export USE_CFP=YES
export nproc=10

# Set cycle
export cyc=00

# Set verification information
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=wave
export VERIF_CASE=grid2obs
export NDAYS=31

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export PDYm1=$(date -d "24 hours ago" '+%Y%m%d')
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$PDYm1
export FIXevs='/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix'

############################################################
# CALL executable job script here
############################################################
${HOMEevs}/jobs/global_det/plots/JEVS_GLOBAL_DET_PLOTS

#%include <tail.h>
#%manual
#########################################################################
# Purpose: This does the plotting work for the global deterministic
#          wave grid-to-obs for past 31 days
#########################################################################
#%end
