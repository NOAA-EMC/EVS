#!/bin/ksh
#*************************************************************************
#  Purpose: Generate refs grid2obs profile poe and sub-jobs files
#  Last update: 05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#*************************************************************************
set -x 

domain=$1
nmbrs=14

if [ $domain = all ] ; then
  domains="CONUS Alaska HI PR"
else
  domains=$domain
fi

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_refs_profile_poe.sh


export obsv=prepbufr

typeset -Z2 hh
for dom in $domains ; do

   if [ $dom = CONUS ] ; then

       export domain=CONUS

       
     for valid_at in 00 12 ; do

      for fhr in 06 12 18 24 30 36 42 48 ; do
     
     
	#****************************
	# Build sub-jobs
	#****************************
        >run_refs_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this CONUS task has been completed in the precious run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task 
      #########################################################################################
    if [ ! -e  $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed ] ; then      

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINrefs/refs.${iday}/verf_g2g/refs.*.t${ihr}z.conus.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G227.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then      

       echo "export regrid=NONE" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export obsv=prepbufr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export domain=CONUS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

       echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}.${fhr}_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh 
       echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvhead=$obsv" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvgrid=G227" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

       
       echo  "export vbeg=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export vend=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh       


       echo  "export lead=$fhr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        
       echo  "export domain=CONUS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export model=refs"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export regrid=NONE " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelgrid=conus.f" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
 
       echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

       echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc,
                                   ${maskpath}/Bukovsky_G227_CONUS_East.nc,
                                   ${maskpath}/Bukovsky_G227_CONUS_West.nc,
                                   ${maskpath}/Bukovsky_G227_CONUS_South.nc,
                                   ${maskpath}/Bukovsky_G227_CONUS_Central.nc,
                                   ${maskpath}/Bukovsky_G227_Appalachia.nc,
                                   ${maskpath}/Bukovsky_G227_CPlains.nc,
                                   ${maskpath}/Bukovsky_G227_DeepSouth.nc,
                                   ${maskpath}/Bukovsky_G227_GreatBasin.nc,
                                   ${maskpath}/Bukovsky_G227_GreatLakes.nc,
                                   ${maskpath}/Bukovsky_G227_Mezquital.nc,
                                   ${maskpath}/Bukovsky_G227_MidAtlantic.nc,
                                   ${maskpath}/Bukovsky_G227_NorthAtlantic.nc,
                                   ${maskpath}/Bukovsky_G227_NPlains.nc,
                                   ${maskpath}/Bukovsky_G227_NRockies.nc,
                                   ${maskpath}/Bukovsky_G227_PacificNW.nc,
                                   ${maskpath}/Bukovsky_G227_PacificSW.nc,
                                   ${maskpath}/Bukovsky_G227_Prairie.nc,
                                   ${maskpath}/Bukovsky_G227_Southeast.nc,
                                   ${maskpath}/Bukovsky_G227_Southwest.nc,
                                   ${maskpath}/Bukovsky_G227_SPlains.nc,
                                   ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for CONUS:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################
	
	echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh 
        echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*CONUS*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/profile; fi; done"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  [[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  cp $COMOUTrestart/profile/GenEnsProd*CONUS*.nc \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh 
        echo "   >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_PROFILE_prob.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "   >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
	echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

	echo "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh

	#Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
	echo "[[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_refs_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/run_refs_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_refs_profile_poe.sh

       fi

      fi

      done

     done

    elif [ $dom = Alaska ] ; then

       export domain=Alaska

      for valid_at in 00 12 ; do 

       for fhr in 06 12 18 24 30 36 42 48 ; do 

         >run_refs_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Alaska task has been completed in the precious run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
     if [ ! -e  $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINrefs/refs.${iday}/verf_g2g/refs.*.t${ihr}z.ak.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G198.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

        echo "export regrid=NONE" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=Alaska" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}.${fhr}_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G198" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export domain=Alaska " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export lead=$fhr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export model=refs"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=ak.f" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Alaska_HREF.nc'"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh


        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Alaska:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*Alaska*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/profile; fi; done"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  [[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "else " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  cp $COMOUTrestart/profile/GenEnsProd*Alaska*.nc \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "   >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_PROFILE_prob.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "   >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
        echo "[[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh


	chmod +x run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_refs_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_refs_profile_poe.sh

       fi 	
      fi

     done
    done


    elif [ $dom = HI ] ; then

       export domain=HI

      for valid_at in 00 12 ; do

       for fhr in 06 12 18 24 30 36 42 48 ; do

         >run_refs_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Hawaii task has been completed in the precious run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
     if [ ! -e  $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINrefs/refs.${iday}/verf_g2g/refs.*.t${ihr}z.hi.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G139.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

        echo "export regrid=NONE" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=HI" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}.${fhr}_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G139" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export lead=$fhr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export model=refs"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=hi.f" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Hawaii_HREF.nc'"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Hawaii:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*_HI_*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/profile; fi; done" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  [[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "else " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  cp $COMOUTrestart/profile/GenEnsProd*_HI_*.nc \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "   >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_PROFILE_prob.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
        echo "[[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        chmod +x run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_refs_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_refs_profile_poe.sh

       fi	
      fi

      done
     done


    elif [ $dom = PR ] ; then

       export domain=PR

      for valid_at in 00 12 ; do

       for fhr in 06 12 18 24 30 36 42 48 ; do

         >run_refs_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Puerto Rico task has been completed in the precious run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
      if [ ! -e  $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

       ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
       iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

       input_fcst="$COMINrefs/refs.${iday}/verf_g2g/refs.*.t${ihr}z.pr.f${fhr}"
       input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G200.nc"

       if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

        echo "export regrid=NONE" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=PR" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}.${fhr}_profile" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "export obsvhead=$obsv " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G200" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export lead=$fhr" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export model=refs"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=pr.f" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/PRico_HREF.nc'"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Puerto Rico:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*_PR_*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/profile; fi; done" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  [[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "else " >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  cp $COMOUTrestart/profile/GenEnsProd*_PR_*.nc \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_PROFILE.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_PROFILE_prob.conf " >>  run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done"  >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
        echo "[[ \$? = 0 ]] && >$COMOUTrestart/profile/run_refs_${domain}.${valid_at}.${fhr}_profile.completed" >> run_refs_${domain}.${valid_at}.${fhr}_profile.sh

        chmod +x run_refs_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_refs_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_refs_profile_poe.sh
       
       fi	
      fi

      done
     done

    fi 

 done #end of dom


chmod 775 run_all_refs_profile_poe.sh
