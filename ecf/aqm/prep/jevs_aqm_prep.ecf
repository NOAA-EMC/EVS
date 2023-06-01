#PBS -N jevs_aqm_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:30:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

###%include <head.h>
###%include <envir-p1.h>

############################################################
# Load modules
############################################################
module reset

export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}/
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load gsl/${gsl_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${produtil_ver}
module load prod_envir/${prodenvir_ver}

module list

export cyc=00
echo $cyc
export NET=evs
export STEP=prep
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}

export MET_bin_exec=bin

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

########################################################################
## The following setting is for parallel test and need to be removed for operational code
########################################################################
export DATA=/lfs/h2/emc/ptmp/$USER/EVS/${cyc}_${MODELNAME}

rm -rf $DATA
mkdir -p $DATA
cd $DATA

export cycle=t${cyc}z

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMIN=/lfs/h2/emc/physics/noscrub/$USER/${NET}/${evs_ver}
##
## For aqmv7 NRT runs
## export fcst_input_ver=v7
## export COMINaqm=/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/v7.0
##
## For AQMv6 restrospective output
## export COMINaqm=/lfs/h2/emc/physics/noscrub/ho-chun.huang/verification/${MODELNAME}/${envir}
##
export COMOUT=$COMIN/${STEP}/${COMPONENT}

#
## export KEEPDATA=NO
#
########################################################################
## VDATE = ${PDYm2} is okay after 01Z today for the default
##               "export airnow_hourly_type=aqobs"
##         VDATE = ${PDYm3} is currrently set as default in
###              /EVS/jobs/aqm/prep/JEVS_AQM_PREP
## VDATE = ${PDYm3} is needed after 00Z and before 01Z today for a
##         option that is not "aqobs", i.e., one is using hourly input
##         HourlyData_yyyymmddhh.dat but not the HourlAQObs_yyyymmddhh.dat
########################################################################
#
## export VDATE=20230513
#
########################################################################

export maillist=${maillist:-'ho-chun.huang@noaa.gov,geoffrey.manikin@noaa.gov'}
## export maillist=${maillist:-'perry.shafran@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/aqm/prep/JEVS_AQM_PREP

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the AQM
##          model and generate stat files.
#######################################################################
#



