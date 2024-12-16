#PBS -S /bin/bash
#PBS -N jevs_hurricane_global_ens_tropcyc_stats
#PBS -j oe
#PBS -A VERF-DEV
#PBS -q dev
#PBS -l select=1:ncpus=1:mem=4GB
##PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l walltime=00:30:00
#PBS -l debug=true

set -x

#%include <head.h>
#%include <envir-p1.h>

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source ${HOMEevs}/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export NET=evs
export COMPONENT=hurricane
export RUN=global_ens
export STEP=stats
export VERIF_CASE=tropcyc
export envir=dev
export cyc=00
export job=jevs_${COMPONENT}_${RUN}_${VERIF_CASE}_${STEP}_${cyc}
export jobid=$job.${PBS_JOBID:-$$}

############################################################
# Load modules
############################################################
module reset
module load prod_envir/${prod_envir_ver}
source ${HOMEevs}/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

#Set PDY to override setpdy.sh called in the j-jobs
export PDY=20241231

#Define TC-vital file, TC track file and the directory for Bdeck files
export COMINvit=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/syndat_tcvitals.2024
export COMINtrack=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/tracks.atcfunix.24
export COMINbdeckNHC=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/bdeck
export COMINbdeckJTWC=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/bdeck

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export KEEPDATA=YES

# CALL executable job script here
$HOMEevs/jobs/JEVS_HURRICANE_STATS

%include <tail.h>
%manual

%end

