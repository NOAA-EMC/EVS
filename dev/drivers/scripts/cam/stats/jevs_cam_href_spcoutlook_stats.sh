#PBS -N jevs_cam_href_spcoutlook_stats
#PBS -j oe
#PBS -q dev
#PBS -S /bin/bash
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=4:mem=100GB
#PBS -l debug=true

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=spcoutlook
export MODELNAME=href
export KEEPDATA=NO

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export run_envir=dev

export cyc=00

#export VDATE=20230312

export run_mpi=yes
export gather=yes

export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export jobid=$job.${PBS_JOBID:-$$}

#Define the spc outlook reqions mask file path
export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/${USER}/evs/v1.0/prep/cam


export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'
if [ -z "$maillist" ]; then

  echo "maillist variable is not defined. Exiting without continuing."

else

 ${HOMEevs}/jobs/cam/stats/JEVS_CAM_STATS

fi

