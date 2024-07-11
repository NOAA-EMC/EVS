#!/bin/ksh
#***********************************************************************************
#  Purpose: Run sref's precip stat job
#  Last update: 
#               01/10/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
##************************************************************************
set -x 

export vday=$VDATE
export regrid='NONE'
############################################################

#********************************************
# Check the input data files availability
# ******************************************
$USHevs/mesoscale/evs_check_sref_files.sh
export err=$?; err_chk

#*******************************************
# Build POE script to collect sub-jobs
# ******************************************
>run_all_sref_precip_poe

export model=sref

for  obsv in ccpa ; do 

#####for  obsv in ndas ccpa ; do 

 export domain=CONUS

  #***********************************************
  # Get prepbufr data files for validation
  #***********************************************
  if [ ! -d $COMOUTrestart/ccpa.$vday ] ; then
    $USHevs/mesoscale/evs_prepare_sref.sh $obsv 
    export err=$?; err_chk
  else
    #restart from previously existing ccpa files
    cp -r $COMOUTrestart/ccpa.$vday $WORK
  fi

  if [ $obsv = ccpa ] ; then
    #restart for sref_apcp06 is set within evs_prepare_sref.sh
    $USHevs/mesoscale/evs_prepare_sref.sh  sref_apcp06
    export err=$?; err_chk

    #if ${COMOUTfinal}/apcp24mean exists, is will be used in the restart next time 
    if [ ! -d ${COMOUTfinal}/apcp24mean ] ; then 
      $USHevs/mesoscale/evs_prepare_sref.sh sref_apcp24_mean
      export err=$?; err_chk
    fi
  fi

  #*******************************************************
  # Build sub-jobs
  #*****************************************************
  for fhr in fhr1 fhr2 ; do
  
    >run_sref_mpi_${domain}.${obsv}.${fhr}.sh

    #############################################################################################################
    # Adding following "if blocks"  for restart capability: 
    #  1. check if *.completed files for 5  METplus processes (genensprod, ens, mean and prob) exist, respectively
    #  2. if any of the 5 not exist, then run its METplus, then mark it completed for restart checking next time
    #  3. if any one of the 5 exits, skip it. But for genensprod, all of the nc files generated from previous run
    #       are copied back to the output_base/stat directory
    ###############################################################################################################
    if [ ! -e $COMOUTrestart/run_sref_mpi_${domain}.${obsv}.${fhr}.completed ] ; then

       echo  "#!/bin/ksh" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
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

	 echo  "export grid=G212"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh      
	 echo  "export obsvgrid=grid212" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

	 #Adding following 5 "if-blocks"  for restart capability:
         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.GenEnsProd.completed ] ; then " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GenEnsProd_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
	 echo " if [ -s \$output_base/stat/GenEnsProd_SREF_CCPA*.nc ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  cp \$output_base/stat/GenEnsProd_SREF_CCPA*.nc $COMOUTrestart" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.GenEnsProd.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
	 echo " fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "else" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  mkdir -p \$output_base/stat" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  cp $COMOUTrestart/GenEnsProd_SREF_CCPA*.nc \$output_base/stat" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.EnsembleStat.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/${domain}.${obsv}.${fhr}.EnsembleStat.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_mean.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_mean.completed " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_prob.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_prob_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo " [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_prob.completed " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_mean_G240.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  export obsvgrid=grid240" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  export grid=G240"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  export regrid=OBS" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G240.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "  [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.GridStat_mean_G240.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         echo "if [ -s \$output_base/stat/*.stat ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo " cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "fi" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

	 #Mark that all of the  5 METplus processes are completed for next restart run:
         echo "[[ \$? = 0 ]] && >$COMOUTrestart/run_sref_mpi_${domain}.${obsv}.${fhr}.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.sh

         chmod +x run_sref_mpi_${domain}.${obsv}.${fhr}.sh
         echo "${DATA}/run_sref_mpi_${domain}.${obsv}.${fhr}.sh" >> run_all_sref_precip_poe

    fi  # check restart for the sub-job

  done

done

chmod +x  run_all_sref_precip_poe

#***************************************************
# Run POE script to get small stat files
#*************************************************
if [ $run_mpi = yes ] ; then
  mpiexec  -n 4 -ppn 4 --cpu-bind core --depth=2 cfp ${DATA}/run_all_sref_precip_poe
else
   ${DATA}/run_all_sref_precip_poe
fi 
export err=$?; err_chk

echo "Print stat generation  metplus log files begin:"
log_dirs="$DATA/precip/*/logs"
for log_dir in $log_dirs; do
    if [ -d $log_dir ]; then
        log_file_count=$(find $log_dir -type f | wc -l)
        if [[ $log_file_count -ne 0 ]]; then
            log_files=("$log_dir"/*)
            for log_file in "${log_files[@]}"; do
                if [ -f "$log_file" ]; then
                    echo "Start: $log_file"
                    cat "$log_file"
                    echo "End: $log_file"
                fi
            done
        fi
    fi
done
echo "Print stat generation  metplus log files end"

#***********************************************
# Gather small stat files to forma big stat file
# **********************************************
if [ $gather = yes ] && [ -s $COMOUTsmall/*.stat ] ; then
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
  export err=$?; err_chk
fi 
