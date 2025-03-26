#PBS -N jevs_aqm_grid2obs_hourly_plots_last31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter:exclhost,select=5:ncpus=128:ompthreads=1:mem=275GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

############################################################
# Load modules
############################################################

source ${HOMEevs}/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

module reset
module load prod_envir/${prod_envir_ver}

source ${HOMEevs}/dev/modulefiles/aqm/aqm_plots.sh

############################################################
## For dev testing
#############################################################
export vhr=00
export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export KEEPDATA=NO
export SENDMAIL=YES
export SENDDBN=NO

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
today=$(cut -c7-14 ${COMROOT}/date/t${vhr}z)
export VDATE_END=$(finddate.sh ${today} d-4)
export COMOUT=/lfs/h2/emc/ptmp/$USER/${NET}/${evs_ver_2d}/${STEP}/${COMPONENT}/${RUN}.${VDATE_END}

export USE_CFP=YES
export nproc=128    ## nproc must match with the ncpus allocation above

export DATA_TYPE=hourly
export NDAYS=31

export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,andrew.benjamin@noaa.gov'}

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   ${HOMEevs}/jobs/JEVS_AQM_PLOTS

fi

exit

