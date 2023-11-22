#!/bin/ksh
#***********************************************************************************
#  Purpose: Run cnv job by using the mean CTC obtained from evs_sref_average_cnv.sh
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************

set -x
export vday=$VDATE
export regrid='NONE'

#********************************************
# Check the input data files availability
# ******************************************
$USHevs/mesoscale/evs_check_sref_files.sh
export err=$?; err_chk

#*******************************************
# Build POE script to collect sub-jobs
# ******************************************
>run_all_sref_cnv_poe.sh

export model=sref

for  obsv in prepbufr ; do 

 export domain=CONUS

  #***********************************************
  # Get prepbufr data files for validation
  #***********************************************
  $USHevs/mesoscale/evs_prepare_sref.sh prepbufr 
  export err=$?; err_chk

  #*******************************************************
  # Build sub-jobs
  #*****************************************************
  for fhr in 3 9 15 21 27 33 39 45 51 57 63 69 75 81 87 ; do
       >run_sref_cnv_${fhr}.sh

       echo  "export output_base=$WORK/grid2obs/run_sref_cnv_${fhr}" >> run_sref_cnv_${fhr}.sh 
       echo  "export domain=CONUS"  >> run_sref_cnv_${fhr}.sh 
  
       echo  "export domain=$domain" >> run_sref_cnv_${fhr}.sh
       echo  "export obsvhead=$obsv" >> run_sref_cnv_${fhr}.sh
       echo  "export obsvgrid=grid212" >> run_sref_cnv_${fhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_cnv_${fhr}.sh
       echo  "export vbeg=0" >>run_sref_cnv_${fhr}.sh
       echo  "export vend=18" >>run_sref_cnv_${fhr}.sh
       echo  "export valid_increment=21600" >> run_sref_cnv_${fhr}.sh

       echo  "export lead=$fhr" >> run_sref_cnv_${fhr}.sh

       echo  "export domain=CONUS" >> run_sref_cnv_${fhr}.sh
       echo  "export model=sref"  >> run_sref_cnv_${fhr}.sh
       echo  "export MODEL=SREF" >> run_sref_cnv_${fhr}.sh
       echo  "export regrid=NONE " >> run_sref_cnv_${fhr}.sh
       echo  "export modelhead=sref" >> run_sref_cnv_${fhr}.sh
    
       echo  "export modelpath=$COMINsref" >> run_sref_cnv_${fhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_cnv_${fhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_cnv_${fhr}.sh
       echo  "export extradir=''" >> run_sref_cnv_${fhr}.sh

       export base_model
       export mbr
       for base_model in arw nmb ; do 
	  for mbr in ctl p1 p2 p3 p4 p5 p6  n1 n2 n3 n4 n5 n6  ; do
	    echo "export base_model=$base_model" >> run_sref_cnv_${fhr}.sh
	    echo "export mbr=$mbr" >> run_sref_cnv_${fhr}.sh 
            echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_cnv.conf">> run_sref_cnv_${fhr}.sh
         done
       done
       


       echo "cd \$output_base/stat" >> run_sref_cnv_${fhr}.sh 
       echo "$USHevs/mesoscale/evs_sref_average_cnv.sh $fhr" >> run_sref_cnv_${fhr}.sh

       #echo "rm \$output_base/stat/*SREFarw*.stat ">> run_sref_cnv_${fhr}.sh
       #echo "rm \$output_base/stat/*SREFnmb*.stat ">> run_sref_cnv_${fhr}.sh

       if [ $SENDCOM = 'YES' ]; then
       echo "cp \$output_base/stat/*CNV*.stat $COMOUTsmall" >> run_sref_cnv_${fhr}.sh
       fi

       chmod +x run_sref_cnv_${fhr}.sh
       echo "${DATA}/run_sref_cnv_${fhr}.sh" >> run_all_sref_cnv_poe.sh


  done

done

#***************************************************
# Run POE script to get small stat files
#*************************************************
chmod 775 run_all_sref_cnv_poe.sh
if [ $run_mpi = yes ] ; then
   mpiexec  -n 15 -ppn 15 --cpu-bind core --depth=2 cfp ${DATA}/run_all_sref_cnv_poe.sh
else
   ${DATA}/run_all_sref_cnv_poe.sh
fi 
export err=$?; err_chk

echo "Print stat generation metplus log files begin:"
 cat $DATA/grid2obs/*/logs/*
echo "Print stat generation metplus log files end"

#***********************************************
# Gather small stat files to forma big stat file
# **********************************************
if [ $gather = yes ] ; then 
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
  export err=$?; err_chk
fi


