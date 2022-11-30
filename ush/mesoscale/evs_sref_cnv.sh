#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 

export vday=$VDATE
export regrid='NONE'
############################################################

$USHevs/mesoscale/evs_check_sref_files.sh

>run_all_sref_cnv_poe.sh

export model=sref

for  obsv in prepbufr ; do 

 export domain=CONUS

  $USHevs/mesoscale/evs_prepare_sref.sh prepbufr 

  for fhr in 3 9 15 21 27 33 39 45 51 57 63 69 75 81 87 ; do
#  for fhr in 3 ; do
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
       echo "cp \$output_base/stat/*CNV*.stat $COMOUTsmall" >> run_sref_cnv_${fhr}.sh

       chmod +x run_sref_cnv_${fhr}.sh
       echo "run_sref_cnv_${fhr}.sh" >> run_all_sref_cnv_poe.sh

  done

done


chmod 775 run_all_sref_cnv_poe.sh
if [ $run_mpi = yes ] ; then
   export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec  -n 15 -ppn 15 --cpu-bind core --depth=2 cfp run_all_sref_cnv_poe.sh
else
  sh run_all_sref_cnv_poe.sh
fi 

if [ $gather = yes ] ; then 
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
fi


