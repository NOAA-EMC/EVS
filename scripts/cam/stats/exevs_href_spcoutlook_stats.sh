#!/bin/ksh
#################################################################
# Script Name: verf_g2g_reflt.sh.sms $vday $vcyc
# Purpose:   To run grid-to-grid verification on reflectivity
#
# Log History:  Julia Zhu -- 2010.04.28 
################################################################
set -x


export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

#check input data are available:
$USHevs/cam/evs_check_href_files.sh 

#lvl = profile or sfc or both
export lvl='both'

#  verify_all = yes:  verify both profile and sfc (system + product)
#  if lvl is not both, verify_all = no
export verify_all='yes'

export prepare='yes'
export verif_system='es'
export verif_profile='es'
export verif_product='es'
export verif_spcoutlook='yes'
export gather=${gather:-'yes'}
export verify=$VERIF_CASE
export run_mpi=${run_mpi:-'yes'}

export COMHREF=$COMINhref
export PREPBUFR=$COMINprepbufr

export GATHER_CONF_PRECIP=$PRECIP_CONF
export GRID2OBS_CONF=$PARMevs/metplus_config/$COMPONENT/grid2obs/$STEP
export GATHER_CONF_GRID2OBS=$GRID2OBS_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE

#Define the spc outlook reqions mask file path
export COMINspcoutlook=${COMINspcoutlook:-$(compath.py -o ${NET}/${evs_ver})/prep/$COMPONENT/href}
export SPCoutlookMask=$COMINspcoutlook/spc.$VDATE



#  domain = conus or alaska or all
export domain="all"
#export domain="HI"


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"

if [ $prepare = yes ] ; then
  $USHevs/cam/evs_href_preppare.sh prepbufr CONUS
fi 


>run_href_all_grid2obs_poe

#Spc_outlook: 2 job
if [ $verif_spcoutlook = yes ] ; then
  $USHevs/cam/evs_href_spcoutlook.sh
  cat ${DATA}/run_all_href_spcoutlook_poe.sh >> run_href_all_grid2obs_poe
fi


#totall: 32 jobs for all (both conus and alaska, profile, system and product)
chmod 775 run_href_all_grid2obs_poe


if [ $run_mpi = yes ] ; then

    export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH

    mpiexec -np 2 -ppn 2 --cpu-bind verbose,depth cfp  ${DATA}/run_href_all_grid2obs_poe

else
    ${DATA}/run_href_all_grid2obs_poe

fi

if [ $gather = yes ] && [ -s ${DATA}/run_href_all_grid2obs_poe ] ; then
  $USHevs/cam/evs_href_gather.sh $VERIF_CASE  
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"


exit 0
