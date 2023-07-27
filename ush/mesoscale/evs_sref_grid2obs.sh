#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 

export vday=$VDATE
export regrid='NONE'
############################################################

$USHevs/evs_check_sref_files.sh

>run_all_sref_g2o_poe.sh

export model=sref

for  obsv in prepbufr ; do 

 export domain=CONUS

  $USHevs/mesoscale/evs_prepare_sref.sh prepbufr 

  for fhr in fhr1 fhr2 ; do
       >run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo  "export output_base=$WORK/grid2obs/${domain}.${obsv}.${fhr}" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh 
       echo  "export domain=CONUS"  >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh 
  
       echo  "export domain=$domain" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export obsvhead=$obsv" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export obsvgrid=grid212" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export vbeg=0" >>run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export vend=18" >>run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export valid_increment=21600" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       if [ $fhr = fhr1 ] ; then
           echo  "export lead='3, 9, 15, 21, 27, 33, 39'" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       elif [ $fhr = fhr2 ] ; then
           echo  "export lead='45, 51, 57, 63, 69, 75, 81, 87'" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       fi

       echo  "export domain=CONUS" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export model=sref"  >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export MODEL=SREF" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export regrid=NONE " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modelhead=sref" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
    
       echo  "export modelpath=$COMINsref" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modelmean=$COMINsrefmean" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export extradir=''" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_mean.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_prob.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo "cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       chmod +x run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "${DATA}/run_sref_g2o_${domain}.${obsv}.${fhr}.sh" >> run_all_sref_g2o_poe.sh

  done

done


chmod 775 run_all_sref_g2o_poe.sh
if [ $run_mpi = yes ] ; then
   export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec  -n 2 -ppn 2 --cpu-bind core --depth=2 cfp ${DATA}/run_all_sref_g2o_poe.sh
else
   ${DATA}/run_all_sref_g2o_poe.sh
fi 

if [ $gather = yes ] ; then 
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
fi


