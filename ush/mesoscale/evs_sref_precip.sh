#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


export vday=$VDATE
export regrid='NONE'
############################################################

$USHevs/mesoscale/evs_check_sref_files.sh

>run_all_sref_precip_poe

export model=sref

for  obsv in ccpa ; do 

#####for  obsv in ndas ccpa ; do 

 export domain=CONUS

  $USHevs/mesoscale/evs_prepare_sref.sh $obsv 


  if [ $obsv = ccpa ] ; then
    $USHevs/mesoscale/evs_prepare_sref.sh  sref_apcp06
    $USHevs/mesoscale/evs_prepare_sref.sh sref_apcp24_mean
  fi


  for fhr in fhr1 fhr2 ; do
  
       >run_sref_mpi_${domain}.${obsv}.${fhr}.sh

       echo  "export output_base=$WORK/precip/${domain}.${obsv}.${fhr}" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh 

   
       echo  "export obsvhead=$obsv" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export vbeg=03" >>run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export vend=21" >>run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export valid_increment=21600" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
    
       if [ $fhr = fhr1 ] ; then   
          echo  "export lead='6, 12, 18, 24, 30, 36, 42'" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       elif [ $fhr = fhr2 ] ; then
          echo  "export lead='48, 54, 60, 66, 72, 78, 84'" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       fi  

       echo  "export domain=CONUS" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export model=sref"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export MODEL=SREF" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export regrid=NONE " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export modelhead=sref" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

    if [ $obsv = ccpa ] ; then
       echo  "export modelpath=$WORK" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export modelgrid=pgrb212.6hr" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export modeltail='.nc'" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export extradir=''" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

    else
       echo  "export modelpath=$COMINsref" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo  "export extradir=''" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

    fi
       if [ $obsv = ndas ] ; then 

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstSREF_obsModelAnalysis.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

       elif [ $obsv = ccpa  ] ; then

	 echo  "export grid=G212"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh      
	 echo  "export obsvgrid=grid212" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GenEnsProd_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_prob_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

	 echo  "export obsvgrid=grid240" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
	 echo  "export grid=G240"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
	 echo  "export regrid=OBS" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G240.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

       else
         exit
       fi

       echo "cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

       chmod +x run_sref_mpi_${domain}.${obsv}.${fhr}.sh
       echo "${DATA}/run_sref_mpi_${domain}.${obsv}.${fhr}.sh" >> run_all_sref_precip_poe

  done

done

chmod +x  run_all_sref_precip_poe

if [ $run_mpi = yes ] ; then

  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH

  mpiexec  -n 4 -ppn 4 --cpu-bind core --depth=2 cfp ${DATA}/run_all_sref_precip_poe

else
   ${DATA}/run_all_sref_precip_poe
fi 


if [ $gather = yes ] ; then
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
fi 
