#PBS -S /bin/bash
#PBS -N jevs_narre_stats_%CYC%
#PBS -j oe
#PBS -q %QUEUE%
#PBS -A %PROJ%-%PROJENVIR%
#PBS -l walltime=00:30:00
#PBS -l place=vscatter,select=1:ncpus=16:mem=500GB
#PBS -l debug=true

model="evs"
export cyc=%CYC%
export NET=%NET%

%include <head.h>
%include <envir-p1.h>

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

# Not sure why HPC_OPT is being defined.  It is set in `envvar` module.
# NCO will remove this line and the next module use line.
export HPC_OPT=/apps/ops/prod/libs
module use /apps/ops/prod/libs/modulefiles/compiler/intel/$intel_ver
module load gsl/${gsl_ver}
module load python/$python_ver
module load met/$met_ver
module load metplus/$metplus_ver
module load udunits/${udunits_ver}

module list

export STEP=stats
export COMPONENT=narre
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=narre

# set variables needed/used in j-job called by this ecf script
export rum_mpi=yes  # rum?

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/ptmp/${USER}/evs/tmpnwprd

${HOMEevs}/jobs/narre/stats/JEVS_NARRE_STATS

if [ $? -ne 0 ]; then
   ecflow_client --msg="***JOB ${ECF_NAME} ERROR RUNNING J-SCRIPT ***"
   ecflow_client --abort
   exit
fi

%include <tail.h>

%manual

%end
