#!/bin/ksh
#***********************************************************************************
#  Purpose: Run cnv job by using the mean CTC obtained from evs_sref_average_cnv.sh
#  Last update: 
#              04/10/2024, add restart capability,  Binbin Zhou Lynker@EMC/NCEP
#  10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************

set -x
export vday=$VDATE
export regrid='NONE'

#*******************************************
# Build POE script to collect sub-jobs
# ******************************************
>run_all_sref_cnv_poe.sh

export model=sref

for  obsv in prepbufr ; do 

 export domain=CONUS

  #**************************************************************
  # Get prepbufr data files for validation
  # In case of restart, First check if prepbufr directory exists
  # if yes, copy it to the working directory 
  # otherwise, run $USHevs/mesoscale/evs_prepare_sref.sh prepbufr
  #*************************************************************
  if [ ! -d $COMOUTrestart/prepbufr.${VDATE} ] ; then
    $USHevs/mesoscale/evs_prepare_sref.sh prepbufr 
    export err=$?; err_chk
  else
    #Restart: copy saved stat files from previous runs
    cp -r $COMOUTrestart/prepbufr.${VDATE} $WORK/.
  fi


  #*******************************************************
  # Build sub-jobs
  # First check if the sub-task has been done in the previous run
  # if yes, skip this sub-task, in this case the sub-task script
  # file run_sref_cnv_${fhr}_${vhr}.sh is 0-size in the working directory
  # otherwise, continue building this sub-task
  #*****************************************************

  cd $WORK/scripts
  for vhr in 00 06 12 18 ; do 
   for fhr in 03 09 15 21 27 33 39 45 51 57 63 69 75 81 87 ; do
    
       >run_sref_cnv_${fhr}_${vhr}.sh

    if [ ! -e $COMOUTrestart/run_sref_cnv_${fhr}_${vhr}.completed ] ; then

     ihr=`$NDATE -$fhr $VDATE$vhr|cut -c 9-10`
     iday=`$NDATE -$fhr $VDATE$vhr|cut -c 1-8`
     input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${vhr}z.grid212.nc"

       echo  "#!/bin/ksh" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export output_base=$WORK/grid2obs/run_sref_cnv_${fhr}_${vhr}" >> run_sref_cnv_${fhr}_${vhr}.sh 
       echo  "export domain=CONUS"  >> run_sref_cnv_${fhr}_${vhr}.sh 
  
       echo  "export domain=$domain" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export obsvhead=$obsv" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export obsvgrid=grid212" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export vbeg=$vhr" >>run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export vend=$vhr" >>run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export valid_increment=21600" >> run_sref_cnv_${fhr}_${vhr}.sh

       echo  "export lead=$fhr" >> run_sref_cnv_${fhr}_${vhr}.sh

       echo  "export domain=CONUS" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export model=sref"  >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export MODEL=SREF" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export regrid=NONE " >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export modelhead=sref" >> run_sref_cnv_${fhr}_${vhr}.sh
    
       echo  "export modelpath=$COMINsref" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo  "export extradir=''" >> run_sref_cnv_${fhr}_${vhr}.sh

       export base_model
       export mbr
       for base_model in arw nmb ; do 
	  for mbr in ctl p1 p2 p3 p4 p5 p6  n1 n2 n3 n4 n5 n6  ; do
	   input_fcst=${COMINsref}/sref.${iday}/${ihr}/pgrb/sref_${base_model}.t${ihr}z.pgrb212.${mbr}.f${fhr}.grib2
	   if [ -s $input_fcst ] && [ -s $input_obsv ] ; then
	    echo "export base_model=$base_model" >> run_sref_cnv_${fhr}_${vhr}.sh
	    echo "export mbr=$mbr" >> run_sref_cnv_${fhr}_${vhr}.sh 
            echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_cnv.conf">> run_sref_cnv_${fhr}_${vhr}.sh
	    export err=$?; err_chk
	   fi
         done
       done
       
       echo "cd \$output_base/stat" >> run_sref_cnv_${fhr}_${vhr}.sh 
       echo "$USHevs/mesoscale/evs_sref_average_cnv.sh $fhr $vhr" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo "export err=\$?; err_chk" >> run_sref_cnv_${fhr}_${vhr}.sh

       #echo "rm \$output_base/stat/*SREFarw*.stat ">> run_sref_cnv_${fhr}_${vhr}.sh
       #echo "rm \$output_base/stat/*SREFnmb*.stat ">> run_sref_cnv_${fhr}_${vhr}.sh

       echo "if [ -s \$output_base/stat/*CNV*.stat ] ; then" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo " cp \$output_base/stat/*CNV*.stat $COMOUTsmall" >> run_sref_cnv_${fhr}_${vhr}.sh
       echo "fi" >> run_sref_cnv_${fhr}_${vhr}.sh

       #For restart: 
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/run_sref_cnv_${fhr}_${vhr}.completed" >> run_sref_cnv_${fhr}_${vhr}.sh
      
       chmod +x run_sref_cnv_${fhr}_${vhr}.sh
       echo "${DATA}/scripts/run_sref_cnv_${fhr}_${vhr}.sh" >> run_all_sref_cnv_poe.sh

    fi # check restart for the sub-job

   done 
  done

done

#***************************************************
# Run POE script to get small stat files
#*************************************************
chmod 775 run_all_sref_cnv_poe.sh
if [ $run_mpi = yes ] ; then
   mpiexec  -n 15 -ppn 15 --cpu-bind verbose,core cfp ${DATA}/scripts/run_all_sref_cnv_poe.sh
else
   ${DATA}/scripts/run_all_sref_cnv_poe.sh
fi 
export err=$?; err_chk

if [ $? = 0 ] ; then
  >$COMOUTrestart/evs_sref_cnv.completed 
fi 


