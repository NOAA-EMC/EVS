#PBS -N jevs_cam_href_grid2obs_cape_past90days_plots
#PBS -j oe
#PBS -q dev
#PBS -S /bin/bash
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter,select=8:ncpus=72:mpiprocs=72:mem=100GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export met_v=${met_ver:0:4}

export envir=prod

export NET=evs
export STEP=plots
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=grid2obs_cape
export MODELNAME=href


module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh


export KEEPDATA=YES

export cyc=00
#export VDATE=20221231
export past_days=90

export run_mpi=yes

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

${HOMEevs}/jobs/cam/plots/JEVS_CAM_PLOTS
