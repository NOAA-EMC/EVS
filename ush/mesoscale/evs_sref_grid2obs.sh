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
     if [ -d $COMOUTrestart/prepbufr.${VDATE} ] ; then
       cp -r $COMOUTrestart/prepbufr.${VDATE} $WORK/.
     fi
  fi

  #*****************************************
  # Build sub-jobs
  #*****************************************
  cd $WORK/scripts
  for vhr in 00 06 12 18 ; do 
   for fhr in 03 09 15 21 27 33 39 45 51 57 63 69 75 81 87 ; do
       >run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

    if [ ! -e $COMOUTrestart/run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$vhr|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$vhr|cut -c 1-8`
      input_fcst=${COMINsref}/sref.${iday}/${ihr}/pgrb/sref_???.t${ihr}z.pgrb212.*.f${fhr}.grib2
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${vhr}z.grid212.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

       echo  "#!/bin/ksh" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export output_base=$WORK/grid2obs/${domain}.${obsv}.${fhr}.${vhr}" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh 
       echo  "export domain=CONUS"  >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh 
  
       echo  "export domain=$domain" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export obsvhead=$obsv" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export obsvgrid=grid212" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export vbeg=$vhr" >>run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export vend=$vhr" >>run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export valid_increment=21600" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export lead=$fhr" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export domain=CONUS" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export model=sref"  >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export MODEL=SREF" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export regrid=NONE " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modelhead=sref" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
    
       echo  "export modelpath=$COMINsref" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modelmean=$EVSINsrefmean" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modelgrid=pgrb212" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modeltail='.grib2'" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export extradir=''" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       ###########################################################################################################
       # Adding following "if blocks"  for restart capability:
       #  1. check if *.completed files for 4  METplus processes (gneensprod, ens, mean and prob) exist, respectively
       #  2. if any of the 4 not exist, then run its METplus, then mark it completed for restart checking next time 
       #  3. if any one of the 4 exits, skip it. But for gneensprod, all of the nc files generated from previous run
       #       are copied back to the output_base/stat directory
       # ###########################################################################################################
       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_genensprod_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  export err=\$?; err_chk" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo " if [ -s \$output_base/stat/GenEnsProd_SREF_PREPBUFR*.nc ] ; then" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   cp \$output_base/stat/GenEnsProd_SREF_PREPBUFR*.nc $COMOUTrestart" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo " fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo " [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_genensprod_${domain}.${obsv}.${fhr}.${vhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "else " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  mkdir -p \$output_base/stat" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  if [ -s $COMOUTrestart/GenEnsProd_SREF_PREPBUFR*.nc ] ; then"  >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "    cp $COMOUTrestart/GenEnsProd_SREF_PREPBUFR*.nc \$output_base/stat" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  fi" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "fi" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_ens_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstSREF_obsPREPBUFR.conf " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   export err=\$?; err_chk" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   [[ \$? = 0 ]] && >$COMOUTrestart/run_sref_g2o_ens_${domain}.${obsv}.${fhr}.${vhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_mean_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo " [[ -s \$output_base/stat/GenEnsProd_SREF_PREPBUFR_${domain}_FHR${fhr}_${VDATE}_${vhr}0000V_ens.nc ]] && ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_mean.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  export err=\$?; err_chk" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_mean_${domain}.${obsv}.${fhr}.${vhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       echo "if [ ! -e $COMOUTrestart/run_sref_g2o_prob_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   [[ -s \$output_base/stat/GenEnsProd_SREF_PREPBUFR_${domain}_FHR${fhr}_${VDATE}_${vhr}0000V_ens.nc ]] &&  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstSREF_obsPREPBUFR_prob.conf">> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   export err=\$?; err_chk" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "   [[ \$? = 0 ]] &&  >$COMOUTrestart/run_sref_g2o_prob_${domain}.${obsv}.${fhr}.${vhr}.completed" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "fi " >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       echo "if [ -s \$output_base/stat/*.stat ] ; then" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo " cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "fi" >> run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh 

       #Mark that all of the 4 METplus processes are completed for next restart run:       
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.completed" >>run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh

       chmod +x run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo "${DATA}/scripts/run_sref_g2o_${domain}.${obsv}.${fhr}.${vhr}.sh" >> run_all_sref_g2o_poe.sh

      fi  
    fi  # check restart for the sub-job

  done
 done
done

#***************************************************
# Run POE script to get small stat files
#*************************************************
chmod 775 run_all_sref_g2o_poe.sh
if [ $run_mpi = yes ] ; then
   mpiexec  -n 15 -ppn 15 --cpu-bind verbose,core cfp ${DATA}/scripts/run_all_sref_g2o_poe.sh
else
   ${DATA}/scripts/run_all_sref_g2o_poe.sh
fi 
export err=$?; err_chk

#***********************************************
# Gather small stat files to forma big stat file
# **********************************************
if [ $gather = yes ] && [ -s $COMOUTsmall/*.stat ] ; then 
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
  export err=$?; err_chk
fi



