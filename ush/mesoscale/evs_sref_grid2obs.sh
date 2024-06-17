#!/bin/ksh
#***********************************************************************************
##  Purpose: Run sref's grid2obs stat job
#  Last update: 
#  04/10/2024, add restart capability,  Binbin Zhou Lynker@EMC/NCEP
#  10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
##************************************************************************
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
>run_all_sref_g2o_poe.sh

export model=sref

for  obsv in prepbufr ; do 

 export domain=CONUS

  #*************************************************
  # Get prepbufr data files for validation
  # Check if the prepbufr directory exists saved from 
  #             previous run
  # (1) if not, run evs_prepare_sref.sh
  # (2) else,  copy the existing prepbufr directory to the 
  #             working directory (restart)
  # ***********************************************
  if [ ! -d $COMOUTrestart/prepbufr.${VDATE} ] ; then
     $USHevs/mesoscale/evs_prepare_sref.sh prepbufr 
     export err=$?; err_chk
  else
     #Restart: copy saved stat files from previous runs
     cp -r $COMOUTrestart/prepbufr.${VDATE} $WORK/.
  fi

  #*****************************************
  # Build sub-jobs
  #*****************************************
  for fhr in fhr1 fhr2 ; do
       >run_sref_g2o_${domain}.${obsv}.${fhr}.sh

    if [ ! -e $COMOUTrestart/run_sref_g2o_${domain}.${obsv}.${fhr}.completed ] ; then

       echo  "#!/bin/ksh" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
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
       echo  "export modelmean=$EVSINsrefmean" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo  "export extradir=''" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       ###########################################################################################################
       # Adding following "if blocks"  for restart capability:
       #  1. check if *.completed files for 4  METplus processes (gneensprod, ens, mean and prob) exist, respectively
       #  2. if any of the 4 not exist, then run its METplus, then mark it completed for restart checking next time 
       #  3. if any one of the 4 exits, skip it. But for gneensprod, all of the nc files generated from previous run
       #       are copied back to the output_base/stat directory
       # ###########################################################################################################
       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_genensprod_${domain}.${obsv}.${fhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo " if [ -s \$output_base/stat/GenEnsProd_SREF_PREPBUFR*.nc ] ; then" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   cp \$output_base/stat/GenEnsProd_SREF_PREPBUFR*.nc $COMOUTrestart" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo " fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo " [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_genensprod_${domain}.${obsv}.${fhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "else " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "  mkdir -p \$output_base/stat" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "  cp $COMOUTrestart/GenEnsProd_SREF_PREPBUFR*.nc \$output_base/stat" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "fi" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_ens_${domain}.${obsv}.${fhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   [[ \$? = 0 ]] && >$COMOUTrestart/run_sref_g2o_ens_${domain}.${obsv}.${fhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_mean_${domain}.${obsv}.${fhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_mean.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_mean_${domain}.${obsv}.${fhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_prob_${domain}.${obsv}.${fhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_prob.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "   [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_prob_${domain}.${obsv}.${fhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       echo "if [ -s \$output_base/stat/*.stat ] ; then" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo " cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "fi" >> run_sref_g2o_${domain}.${obsv}.${fhr}.sh 

       #Mark that all of the 4 METplus processes are completed for next restart run:       
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/run_sref_g2o_${domain}.${obsv}.${fhr}.completed" >>run_sref_g2o_${domain}.${obsv}.${fhr}.sh

       chmod +x run_sref_g2o_${domain}.${obsv}.${fhr}.sh
       echo "${DATA}/run_sref_g2o_${domain}.${obsv}.${fhr}.sh" >> run_all_sref_g2o_poe.sh

     fi  # check restart for the sub-job

  done

done

#***************************************************
# Run POE script to get small stat files
#*************************************************
chmod 775 run_all_sref_g2o_poe.sh
if [ $run_mpi = yes ] ; then
   mpiexec  -n 2 -ppn 2 --cpu-bind core --depth=2 cfp ${DATA}/run_all_sref_g2o_poe.sh
else
   ${DATA}/run_all_sref_g2o_poe.sh
fi 
export err=$?; err_chk

echo "Print stat generation  metplus log files begin:"
log_dirs="$DATA/grid2obs/*/logs"
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



