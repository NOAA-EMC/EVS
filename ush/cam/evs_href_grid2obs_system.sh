#!/bin/ksh
#*************************************************************************
#  Purpose: Generate href grid2obs ecnt poe and sub-jobs files
#  Last update: 
#               01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#               10/30/2024, by Binbin Zhou Lynker@EMC/NCEP
##*************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
cd $DATA/scripts
>run_all_href_system_poe.sh

export obsv=prepbufr

for dom in CONUS Alaska ; do

   if [ $dom = CONUS ] ; then

      export domain=CONUS

      for valid_at in 00 03 06 09 12 15 18 21 ; do

        if [ $valid_at = 00 ] || [ $valid_at = 06 ] || [ $valid_at = 12 ] || [ $valid_at = 18 ] ; then
	    fhrs='06 12 18 24 30 36 42 48'
	elif [ $valid_at = 03 ] || [ $valid_at = 09 ] || [ $valid_at = 15 ] || [ $valid_at = 21 ] ; then
	    fhrs='03 09 15 21 27 33 39 45'
	fi

       for fhr in $fhrs ; do
     	
	 #**********************
	 # Build sub-jobs
	 #**********************     
         >run_href_${domain}.${valid_at}.${fhr}_system.sh

        #########################################################################################
	# Restart: check if this CONUS task has been completed in the previous run 
	#          if not, do this task, and mark it is completed after it is done
	#          otherwise, skip this task 
	#########################################################################################
       if [ ! -e  $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}_system.completed ] ; then

        ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
	iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

        if [ $ihr = 00 ] || [ $ihr = 12 ] ; then
	  if [ $fhr -ge 45 ] ; then
             mbrs=7
          elif [ $fhr -eq 42 ] || [ $fhr -eq 39 ] ; then
	     mbrs=8
	  else
	     mbrs=10
	  fi
        elif [ $ihr = 06 ] || [ $ihr = 18 ] ; then
	  if [ $fhr -ge 45 ] ; then
	     mbrs=4
	  elif [ $fhr -le 42 ] || [ $fhr -ge 33 ] ; then
             mbrs=8
          else
             mbrs=10
	  fi
	fi
          
	input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.conus.f${fhr}"
        input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${valid_at}z.G227.nc"

	if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

         if [ $ihr = 00 ] || [ $ihr = 12 ] ; then
            if [ $fhr -ge 45 ] ; then
              mbrs=7
            elif [ $fhr -eq 42 ] || [ $fhr -eq 39 ] ; then
              mbrs=8
            else
              mbrs=10
            fi
         elif [ $ihr = 06 ] || [ $ihr = 18 ] ; then
            if [ $fhr -ge 45 ] ; then
              mbrs=4
            elif [ $fhr -le 42 ] && [ $fhr -ge 33 ] ; then
              mbrs=8
            else
              mbrs=10
            fi
         fi
        
	 echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "set -x " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export regrid=G227" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh 

         echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export obsvhead=$obsv" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export obsvgrid=G227" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export vbeg=$valid_at" >>run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export vend=$valid_at" >>run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export lead='$fhr'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export regrid=G227 " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modelgrid=conus.f" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
 
         echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
        
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
			           ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export valid_at=$valid_at" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

	 ################################################################################################################
	 # Adding following "if blocks"  for restart capability for CONUS: 
	 #  1. check if *.completed files for  EnsembleStat, PointStat 
	 #  2. if any of the 2 not exist, then run its METplus, then mark it completed for restart checking next time
	 #  3. if any one of the 2 exits, copy the stat files from the restart dirctories  
	 #################################################################################################################
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_SFC.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh 

	 echo "if [ ! -e $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_SFC.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh 
	 echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh 
	 echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "else " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

	 echo "if [ ! -e $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_SFC_prob.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "else " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo " [[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_system.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

	 echo "if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
         echo "  cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_system.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         chmod +x run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_system.sh" >> run_all_href_system_poe.sh

        fi

       else
	 #Copy stat files for restart 
         if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/*.stat ] ; then
             cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/*.stat $all_stats
         fi	     
       fi #end check restart in  CONUS completed 

       done

      done

    elif [ $dom = Alaska ] ; then

         export domain=Alaska

      for valid_at in 00 03 06 09 12 15 18 21 ; do

         if [ $valid_at = 00 ] || [ $valid_at = 06 ] || [ $valid_at = 12 ] || [ $valid_at = 18 ] ; then
           fhrs='06 12 18 24 30 36 42 48'
         elif [ $valid_at = 03 ] || [ $valid_at = 09 ] || [ $valid_at = 15 ] || [ $valid_at = 21 ] ; then
           fhrs='03 09 15 21 27 33 39 45'
         fi
   
       for fhr in $fhrs ; do	 

         >run_href_${domain}.${valid_at}.${fhr}_system.sh

       #########################################################################################
       #Restart: check if this Alaska task has been completed in the previous tun
       if [ ! -e  $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}_system.completed ] ; then
       ##########################################################################################
       
        ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
	iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

	input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.ak.f${fhr}"
	input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${valid_at}z.G198.nc"
	                                   
        if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

         if [ $ihr = 06 ] || [ $ihr = 18 ] ; then
            if [ $fhr -ge 45 ] ; then
              mbrs=5
            elif [ $fhr -eq 42 ] || [ $fhr -eq 39 ] ; then
              mbrs=6
            else
              mbrs=8
            fi
         fi

         echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "set -x " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export domain=Alaska" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export obsvgrid=G198" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export vbeg=$valid_at" >>run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export vend=$valid_at" >>run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export lead='$fhr'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modelgrid=ak.f" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo  "export verif_poly='${maskpath}/Alaska_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo  "export valid_at=$valid_at" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

	 ################################################################################################################
	 # Adding following "if blocks"  for restart capability for Alaska:
	 #  1. check if *.completed files for 2  METplus processes EnsembleStat, PointStat
	 #  2. if any of the 2 not exist, then run its METplus, then mark it completed for restart checking next time
	 #            are copied back to the output_base/stat directory
	 #  3. if any one of the 2 exits, copy the stat files from the restart dirctories          
	 #################################################################################################################
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_SFC.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo "if [ ! -e $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_SFC.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.EnsembleStat.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "else " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo "if [ ! -e $COMOUTrestart/system/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_SFC_prob.conf " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "    if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_system.sh         
	 echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh         
	 echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}system.PointStat.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "else " >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
	 echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo " [[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_system.completed" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         echo "if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
	 echo "  cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_system.completed $COMOUTrestart/system" >> run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_system.sh

         chmod +x run_href_${domain}.${valid_at}.${fhr}_system.sh
         echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_system.sh" >> run_all_href_system_poe.sh

	fi 

       else
          if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/*.stat ] ; then
             cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_system/*.stat $all_stats
          fi

       fi # end of check restart in Alaska

       done 

      done 

    fi #end of if dom  

done #end of dom

chmod 775 run_all_href_system_poe.sh
