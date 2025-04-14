#!/bin/ksh
#*************************************************************************
#  Purpose: Generate href grid2obs profile poe and sub-jobs files
#
#  Last update:
#     01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP 
#     10/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#*************************************************************************
set -x 

domain=$1

if [ $domain = all ] ; then
  domains="CONUS Alaska HI PR"
else
  domains=$domain
fi

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
cd $DATA/scripts
>run_all_href_profile_poe.sh


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
        >run_href_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this CONUS task has been completed in the previous run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task 
      #########################################################################################
    if [ ! -e  $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.completed ] ; then      

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.conus.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G227.nc"

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

       echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "set -x" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh 
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvhead=$obsv" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvgrid=G227" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       
       echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh       


       echo  "export lead=$fhr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        
       echo  "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelgrid=conus.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
 
       echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for CONUS:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh	

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh 
	echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo "[[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo "if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed $COMOUTrestart/profile" >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       fi

      else
	if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat ] ; then 
	  cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat $all_stats
        fi	  
      fi

      done

     done

    elif [ $dom = Alaska ] ; then

       export domain=Alaska

      for valid_at in 00 12 ; do 

       for fhr in 06 12 18 24 30 36 42 48 ; do 

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Alaska task has been completed in the previous run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
     if [ ! -e  $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.ak.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G198.nc"

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
        echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "set -x" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=Alaska" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G198" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export domain=Alaska " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export lead=$fhr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=ak.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Alaska_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Alaska:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "[[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo " cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed $COMOUTrestart/profile" >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       fi

      else
        if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat ] ; then
          cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat $all_stats
        fi
      fi

     done
    done


    elif [ $dom = HI ] ; then

       export domain=HI

      for valid_at in 00 12 ; do

       for fhr in 06 12 18 24 30 36 42 48 ; do

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Hawaii task has been completed in the previous run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
     if [ ! -e  $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

      input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.hi.f${fhr}"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G139.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

         if [ $ihr = 00 ] || [ $ihr = 12 ] ; then
           if [ $fhr -ge 42 ] ; then
             mbrs=4
	   else
             mbrs=6
           fi
         fi

        echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "set -x" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=HI" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G139" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export lead=$fhr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=hi.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Hawaii_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Hawaii:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "[[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo " cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed $COMOUTrestart/profile" >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       fi

      else
        if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat ] ; then
          cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat $all_stats
        fi
      fi

      done
     done


    elif [ $dom = PR ] ; then

       export domain=PR

      for valid_at in 00 12 ; do

       for fhr in 06 12 18 24 30 36 42 48 ; do

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh

      #########################################################################################
      # Restart: check if this Puerto Rico task has been completed in the previous run
      #          if not, do this task, and mark it is completed after it is done
      #          otherwise, skip this task
      #########################################################################################
      if [ ! -e  $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.completed ] ; then

       ihr=`$NDATE -$fhr $VDATE$valid_at|cut -c 9-10`
       iday=`$NDATE -$fhr $VDATE$valid_at|cut -c 1-8`

       input_fcst="$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.pr.f${fhr}"
       input_obsv="$WORK/prepbufr.${VDATE}/prepbufr_profile.t${valid_at}z.G200.nc"

       if [ -s $input_fcst ] && [ -s $input_obsv ] ; then
         if [ $ihr = 06 ] || [ $ihr = 18 ] ; then
            if [ $fhr -ge 42 ] ; then
                mbrs=4
            else
                mbrs=6
         fi
       fi

        echo "#!/bin/ksh" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "set -x" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=PR" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export nmbrs=$mbrs" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G200" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export lead=$fhr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=pr.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/PRico_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        ################################################################################################################
        # Adding following "if blocks"  for restart capability for Puerto Rico:
        #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
        #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
        #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
        #            are copied back to the output_base/stat directory
        #################################################################################################################
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/ensemble_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.EnsembleStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/ensemble_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ ! -e $COMOUTrestart/profile/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  export err=\$?; err_chk" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  if [ \$? = 0 ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    cp \$output_base/stat/\${MODEL}/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    if [ $SENDCOM = YES ] ; then" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      [[ ! -d $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile ]] && mkdir -p $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/point_stat*.stat $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "      cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.PointStat.completed $COMOUTrestart/profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "    fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "  fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo "else " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	echo " cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/point_stat*.stat $all_stats" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "[[ \$? = 0 ]] && echo completed >\$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo "if [ $SENDCOM = YES ] ; then " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo " cp \$output_base/stat/\${MODEL}/run_href_${domain}.${valid_at}.${fhr}_profile.completed $COMOUTrestart/profile" >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "fi" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/scripts/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       fi

      else
        if [ -s $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat ] ; then
          cp $COMOUTsmall/run_href_${domain}.${valid_at}.${fhr}_profile/*.stat $all_stats
        fi
      fi

      done
     done

    fi 

 done #end of dom


chmod 775 run_all_href_profile_poe.sh
