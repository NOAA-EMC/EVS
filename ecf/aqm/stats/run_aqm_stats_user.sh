#PBS -N run_aqm_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "debug"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true

set -x

BASE=/lfs/h2/emc/vpppg/noscrub/ho-chun.huang/EVS/ecf/aqm/stats

## for fhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
for fhr in 15 
do
   export fhr
   qsub -v cyc=$fhr ${BASE}/jevs_aqm_stats.ecf
   ### sleep 120
done

 exit
