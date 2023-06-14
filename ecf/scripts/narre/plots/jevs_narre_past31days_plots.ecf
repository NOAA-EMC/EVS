#PBS -S /bin/bash
#PBS -N jevs_narre_plots_31days_%CYC%
#PBS -j oe
#PBS -q %QUEUE%
#PBS -A %PROJ%-%PROJENVIR%
#PBS -l walltime=02:30:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=8:mem=100GB
#PBS -l debug=true

model="evs"
export cyc=%CYC%
export NET=%NET%

%include <head.h>
%include <envir-p1.h>

# I am 100% positive this needs to be part of the HOMEevs/versions/run.ver
source $HOMEevs/versions/run.ver.metplus5.0.0

module load envvar/$envvar_ver
module load PrgEnv-intel/$PrgEnv_intel_ver
module load intel/$intel_ver
module load cray-pals/$craypals_ver
module load libjpeg/$libjpeg_ver
module load grib_util/$grib_util_ver
module load prod_util/$prod_util_ver
module load prod_envir/$prod_envir_ver
module load wgrib2/$wgrib2_ver
module load libpng/$libpng_ver
module load zlib/$zlib_ver
module load jasper/$jasper_ver
module load netcdf/$netcdf_ver
module load cfp/$cfp_ver
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/$intel_ver
module load gsl/${gsl_ver}
module load python/$python_ver
module load met/$met_ver
module load metplus/$metplus_ver
module load udunits/${udunits_ver}

module list

export STEP=plots
export COMPONENT=narre
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=narre

export past_days=31

# set variables needed/used in j-job called by this ecf script
export met_v=${met_ver:0:4}
export run_mpi=yes

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/ptmp/${USER}/evs/tmpnwprd

${HOMEevs}/jobs/narre/plots/JEVS_NARRE_PLOTS

if [ $? -ne 0 ]; then
   ecflow_client --msg="***JOB ${ECF_NAME} ERROR RUNNING J-SCRIPT ***"
   ecflow_client --abort
   exit
fi

%include <tail.h>

%manual

%end
