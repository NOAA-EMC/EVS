#PBS -S /bin/bash
#PBS -N jevs_hurricane_global_det_tcgen_plots
#PBS -j oe
#PBS -A ENSTRACK-DEV
#PBS -q dev
#PBS -l select=1:ncpus=2:mem=4GB
##PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l walltime=00:30:00
#PBS -l debug=true
#PBS -V

set -x

#%include <head.h>
#%include <envir-p1.h>

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source ${HOMEevs}/versions/run.ver

export NET=evs
export COMPONENT=hurricane
export RUN=global_det
export STEP=plots
export VERIF_CASE=tcgen
export envir=dev
export cyc=00
export job=jevs_${COMPONENT}_${RUN}_${VERIF_CASE}_${STEP}_${cyc}

############################################################
# Load modules
############################################################
module reset
module load prod_envir/${prod_envir_ver}
source ${HOMEevs}/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

#Set PDY to override setpdy.sh called in the j-jobs
export PDY=20231231

#Define the directories of your TC genesis stats files
export COMINstats=/lfs/h2/emc/ptmp/$USER/com/evs/${evs_ver}/${COMPONENT}/${RUN}/${VERIF_CASE}/stats
#Define the directories of your NOAA/NWS logos
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export DATAROOT=/lfs/h2/emc/ptmp/$USER
export COMROOT=${DATAROOT}/com
rm -rf ${COMROOT}/evs/${evs_ver}/${COMPONENT}/${RUN}/${VERIF_CASE}/${STEP}
export KEEPDATA=YES


# CALL executable job script here
$HOMEevs/jobs/${COMPONENT}/${STEP}/JEVS_HURRICANE_PLOTS

%include <tail.h>
%manual
######################################################################
# Purpose: This job will generate the grid2obs statistics for the HRRR
#          model and generate stat files.
######################################################################
%end

