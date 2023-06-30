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
export job=jevs_hurricane_global_det_tcgen_stats_${cyc}

############################################################
# Load modules
############################################################
module reset
source ${HOMEevs}/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

#Set PDY to override setpdy.sh called in the j-jobs
export PDY=20221231

#Define the directories of your TC genesis data and A/Bdeck files
export COMINgenesis=/lfs/h2/emc/vpppg/noscrub/jiayi.peng/MetTCData/TCgen/Year2022
export COMINadeckNHC=/lfs/h2/emc/vpppg/noscrub/jiayi.peng/MetTCData/adeck/Year2022
export COMINbdeckNHC=/lfs/h2/emc/vpppg/noscrub/jiayi.peng/MetTCData/bdeck/Year2022
export COMINadeckJTWC=/lfs/h2/emc/vpppg/noscrub/jiayi.peng/MetTCData/adeck/Year2022
export COMINbdeckJTWC=/lfs/h2/emc/vpppg/noscrub/jiayi.peng/MetTCData/bdeck/Year2022

export DATAROOT=/lfs/h2/emc/ptmp/$USER
export COMROOT=${DATAROOT}/com
export KEEPDATA=YES

# CALL executable job script here
$HOMEevs/jobs/hurricane/stats/JEVS_HURRICANE_STATS

%include <tail.h>
%manual
######################################################################
# Purpose: This job will generate the grid2obs statistics for the HRRR
#          model and generate stat files.
######################################################################
%end

