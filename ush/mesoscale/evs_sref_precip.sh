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

#*******************************************
# Build POE script to collect sub-jobs
# ******************************************
cd $WORK/scripts
>run_all_sref_precip_poe

export model=sref

for  obsv in ccpa ; do 

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
  for vhr in 03 09 15 21 ; do
    for fhr in 06 12 18 24 30 36 42 48 54 60 66 72 78 84 ; do
  
    >run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

    #############################################################################################################
    # Adding following "if blocks"  for restart capability: 
    #  1. check if *.completed files for 5  METplus processes (genensprod, ens, mean and prob) exist, respectively
    #  2. if any of the 5 not exist, then run its METplus, then mark it completed for restart checking next time
    #  3. if any one of the 5 exits, skip it. But for genensprod, all of the nc files generated from previous run
    #       are copied back to the output_base/stat directory
    ###############################################################################################################
    if [ ! -e $COMOUTrestart/run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$vhr|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$vhr|cut -c 1-8`
      input_fcst="${WORK}/sref.${iday}/sref_???.t${ihr}z.*.pgrb212.6hr.f${fhr}.nc"
      input_obsv212="$WORK/ccpa.${VDATE}/ccpa.t${vhr}z.grid212.06h.f00.nc"
      input_obsv240="$WORK/ccpa.${VDATE}/ccpa.t${vhr}z.grid240.06h.f00.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv212 ] && [ -s $input_obsv240 ] ; then
       echo  "#!/bin/ksh" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export output_base=$WORK/precip/${domain}.${obsv}.${fhr}.${vhr}" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh 
   
       echo  "export obsvhead=$obsv" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export obsvpath=$WORK" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export vbeg=$vhr" >>run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export vend=$vhr" >>run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export valid_increment=21600" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export lead=$fhr" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export domain=CONUS" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export model=sref"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export MODEL=SREF" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export regrid=NONE " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modelhead=sref" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

       echo  "export modelpath=$WORK" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modelgrid=pgrb212.6hr" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export modeltail='.nc'" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
       echo  "export extradir=''" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

	 echo  "export grid=G212"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh      
	 echo  "export obsvgrid=grid212" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

	 #Adding following 5 "if-blocks"  for restart capability:
         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GenEnsProd.completed ] ; then " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GenEnsProd_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "   export err=\$?; err_chk" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo " if [ -s \$output_base/stat/GenEnsProd_SREF_CCPA*.nc ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  cp \$output_base/stat/GenEnsProd_SREF_CCPA*.nc $COMOUTrestart" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GenEnsProd.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo " fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "else" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  mkdir -p \$output_base/stat" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo "  if [ -s $COMOUTrestart/GenEnsProd_SREF_CCPA*.nc ] ; then " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "    cp $COMOUTrestart/GenEnsProd_SREF_CCPA*.nc \$output_base/stat" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo "  fi" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.EnsembleStat.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstSREF_obsCCPA_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "   export err=\$?; err_chk" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.EnsembleStat.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_mean.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  [[ -s \$output_base/stat/GenEnsProd_SREF_CCPA_G212_FHR${fhr}_${VDATE}_${vhr}0000V_ens.nc ]] && ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_mean.completed " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo "   export err=\$?; err_chk" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_prob.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  [[ -s \$output_base/stat/GenEnsProd_SREF_CCPA_G212_FHR${fhr}_${VDATE}_${vhr}0000V_ens.nc ]] && ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_prob_G212.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "   export err=\$?; err_chk" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo " [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_prob.completed " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         echo "if [ ! -e $COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_mean_G240.completed ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  export obsvgrid=grid240" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  export grid=G240"  >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  export regrid=OBS" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "  [[ -s \$output_base/stat/GenEnsProd_SREF_CCPA_G212_FHR${fhr}_${VDATE}_${vhr}0000V_ens.nc ]] && ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstSREF_obsCCPA_mean_G240.conf " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "   export err=\$?; err_chk" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
	 echo "  [[ \$? = 0 ]] && >$COMOUTrestart/${domain}.${obsv}.${fhr}.${vhr}.GridStat_mean_G240.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi " >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         echo "if [ -s \$output_base/stat/*.stat ] ; then" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo " cp \$output_base/stat/*.stat $COMOUTsmall" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "fi" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

	 #Mark that all of the  5 METplus processes are completed for next restart run:
         echo "[[ \$? = 0 ]] && >$COMOUTrestart/run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.completed" >> run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh

         chmod +x run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh
         echo "${DATA}/scripts/run_sref_mpi_${domain}.${obsv}.${fhr}.${vhr}.sh" >> run_all_sref_precip_poe

     fi 	 
    fi  # check restart for the sub-job

  done
 done
done

chmod +x  run_all_sref_precip_poe

#***************************************************
# Run POE script to get small stat files
#*************************************************
if [ $run_mpi = yes ] ; then
  mpiexec  -n 28 -ppn 28 --cpu-bind verbose,core cfp ${DATA}/scripts/run_all_sref_precip_poe
else
   ${DATA}/scripts/run_all_sref_precip_poe
fi 
export err=$?; err_chk

#***********************************************
# Gather small stat files to forma big stat file
# **********************************************
if [ $gather = yes ] && [ -s $COMOUTsmall/*.stat ] ; then
  $USHevs/mesoscale/evs_sref_gather.sh $VERIF_CASE
  export err=$?; err_chk
fi 
