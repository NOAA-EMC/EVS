#PBS -S /bin/bash
#PBS -N jevs_hurricane_global_det_tcgen_stats
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

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/Fork/EVS
source ${HOMEevs}/versions/run.ver

export NET=evs
export COMPONENT=hurricane
export RUN=global_det
export STEP=stats
export VERIF_CASE=tcgen
export envir=dev
export cyc=00
export job=jevs_${COMPONENT}_${RUN}_${VERIF_CASE}_${STEP}_${cyc}

############################################################
# Load modules
############################################################
module reset
source ${HOMEevs}/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

#Set PDY to override setpdy.sh called in the j-jobs
export PDY=20230822

#Define the directories of your TC genesis data and A/Bdeck files
export COMINgenesis=/lfs/h2/emc/vpppg/noscrub/olivia.ostwald/Data/Year2023/TCgen
export COMINadeckNHC=/lfs/h2/emc/vpppg/noscrub/olivia.ostwald/Data/Year2023/adeck
export COMINbdeckNHC=/lfs/h2/emc/vpppg/noscrub/olivia.ostwald/Data/Year2023/bdeck
export COMINadeckJTWC=/lfs/h2/emc/vpppg/noscrub/olivia.ostwald/Data/Year2023/adeck
export COMINbdeckJTWC=/lfs/h2/emc/vpppg/noscrub/olivia.ostwald/Data/Year2023/bdeck

export DATAROOT=/lfs/h2/emc/ptmp/$USER
export COMROOT=${DATAROOT}/com
export KEEPDATA=YES

# CALL executable job script here
$HOMEevs/jobs/${COMPONENT}/${STEP}/JEVS_HURRICANE_STATS

%include <tail.h>
%manual
######################################################################
# Purpose: This job will generate the grid2obs statistics for the HRRR
#          model and generate stat files.
######################################################################
%end

