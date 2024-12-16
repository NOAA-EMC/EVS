#PBS -S /bin/bash
#PBS -N jevs_hurricane_global_ens_spread_plots
#PBS -j oe
#PBS -A VERF-DEV
#PBS -q dev
#PBS -l select=1:ncpus=1:mem=4GB
#PBS -l walltime=01:00:00
#PBS -l debug=true

set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source ${HOMEevs}/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export NET=evs
export COMPONENT=hurricane
export RUN=global_ens
export STEP=plots
export VERIF_CASE=spread
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

#Define the directory for TC-stats file 
export COMINstats=/lfs/h2/emc/vpppg/noscrub/$USER/evs/${evs_ver_2d}/stats/${COMPONENT}/${RUN}/${VERIF_CASE}

#Define TC-vital file, and the directory for Bdeck files
export COMINvit=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/syndat_tcvitals.2024
export COMINbdeckNHC=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/bdeck
export COMINbdeckJTWC=/lfs/h2/emc/vpppg/noscrub/$USER/evs_tc_2024/bdeck

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export KEEPDATA=YES

# CALL executable job script here
$HOMEevs/jobs/JEVS_HURRICANE_PLOTS


