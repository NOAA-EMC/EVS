#!/bin/ksh
#************************************************************************************
#  Purpose: Generate href snowfall poe and sub-jobs files
#  Last update: 
#     01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#     05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#***********************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs 
#******************************************
export write_job_cards=yes
cd $DATA/scripts
>run_all_href_snowfall_poe.sh

mkdir -p $COMOUTsmall/HREF_SNOW
mkdir -p $all_stats/HREF_SNOW

#NOHRSC data missing alert
if [ ! -s $COMSNOW/${VDATE}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${VDATE}12_grid184.grb2 ] ; then 
  if [ $SENDMAIL = YES ] ; then
   export subject="NOHRSC Data Missing for EVS ${COMPONENT}"
   echo "WARNING:  No NOHRSC data available for ${VDATE}" > mailmsg
   echo Missing file is  $COMSNOW/${VDATE}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${VDATE}12_grid184.grb2  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $MAILTO
  fi
  echo "WARNING:  No NOHRSC data $COMSNOW/${VDATE}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${VDATE}12_grid184.grb2 available for ${VDATE}! Terminate snowfall verification"
  export write_job_cards=no
  export verif_snowfall=no
fi

if [ "$write_job_cards" = "yes" ] ; then
for obsv in 6h 24h  ; do

    #*****************************
    # Build sub-jobs
    # ****************************
    if [ $obsv = 6h ] ; then
        export fhrs="06 12 18 24 30 36 42 48"
        export vhrs="00 06 12 18"
    elif [ $obsv = 24h ] ; then
        export fhrs="24 30 36 42 48"
        export vhrs="00 12"
    fi

    for fhr in $fhrs; do

        for vhr in $vhrs; do
            >run_href_snow${obsv}.${fhr}.${vhr}.sh

          ####################################################################################
          # Restart check:
          #       check if this sub-task has been completed in the previous run
          #       if not, do this sub-task, and mark it is completed after it is done
          #       if yes, skip this task
          #####################################################################################
         if [ ! -e  $COMOUTrestart/snow/run_href_snow${obsv}.${fhr}.${vhr}.completed ] ; then

	    ihr=`$NDATE -$fhr $VDATE$vhr|cut -c 9-10`
	    iday=`$NDATE -$fhr $VDATE$vhr|cut -c 1-8`

	    input_fcst=$COMINhref/href.${iday}/verf_g2g/href.*.t${ihr}z.conus.f${fhr}
            input_obsv=$DCOMINsnow/${VDATE}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_${obsv}_${VDATE}${vhr}_grid184.grb2

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


	    echo "#!/bin/ksh" >> run_href_snow${obsv}.${fhr}.${vhr}.sh  
	    echo "set -x" >> run_href_snow${obsv}.${fhr}.${vhr}.sh  
            echo "export mbrs=$mbrs" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "export regrid=G212" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            
            echo  "export output_base=$WORK/precip/run_href_snow${obsv}.${fhr}.${vhr}" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            
            echo  "export obsv=${obsv}" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export obsvpath=$COMSNOW" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export obsvgrid=grid184" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export OBTYPE=NOHRSC" >> run_href_snow${obsv}.${fhr}.${vhr}.sh 

            echo  "export name=WEASD" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export name_obsv=ASNOW" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            if [ $obsv = 6h ] ; then
               echo  "export level=A06" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export thresh='ge0.0254, ge0.0508, ge0.1016, ge0.2032'" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vbeg=$vhr" >>run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vend=$vhr" >>run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export valid_increment=21600" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export lead='$fhr'" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            elif [ $obsv = 24h ] ; then
               echo  "export level=A24" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export thresh='ge0.0254, ge0.1016, ge0.2032, ge0.3048'" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vbeg=$vhr" >>run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vend=$vhr" >>run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export valid_increment=43200" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export lead='$fhr'" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            fi

            echo  "export MODEL=HREF_SNOW" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export regrid=FCST" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modelpath=$COMHREF" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modelgrid=conus" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modeltail=''" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export extradir='verf_g2g/'" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            echo  "export verif_grid='' " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export verif_poly='${maskpath}/Bukovsky_NOHRSC_CONUS.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_East.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_West.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_South.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_Central.nc' " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GenEnsProd_fcstHREF_obsNOHRSC.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "  export err=\$?; err_chk" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/EnsembleStat_fcstHREF_obsNOHRSC.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "  export err=\$?; err_chk" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstHREFmean_obsNOHRSC_G212.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "  export err=\$?; err_chk" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstHREFmean_obsNOHRSC_NOHRSCgrid.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo  "  export err=\$?; err_chk" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

	    #Mark job is completed
            echo "for FILEn in \$output_base/stat/\${MODEL}/*_stat_\${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $all_stats/HREF_SNOW; fi; done" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo " [[ \$? = 0 ]] && echo completed >\$output_base/stat/HREF_SNOW/run_href_snow${obsv}.${fhr}.${vhr}.completed" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            #Send restart files to COMOUT 
	    echo "if [ $SENDCOM = YES ] && [ \$? = 0 ] ; then" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
	    echo " if [ -s $all_stats/HREF_SNOW/*_stat_\${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat ] ; then"  >> run_href_snow${obsv}.${fhr}.${vhr}.sh
	    echo "   cp $all_stats/HREF_SNOW/*_stat_\${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat $COMOUTsmall/HREF_SNOW" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
	    echo "   cp \$output_base/stat/HREF_SNOW/run_href_snow${obsv}.${fhr}.${vhr}.completed $COMOUTrestart/snow" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo " fi" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "fi" >> run_href_snow${obsv}.${fhr}.${vhr}.sh

	    chmod +x run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "${DATA}/scripts/run_href_snow${obsv}.${fhr}.${vhr}.sh" >> run_all_href_snowfall_poe.sh
         
	   fi   
	  else
	    if [ -s $COMOUTsmall/HREF_SNOW/*_stat_HREF_SNOW_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat ] ; then
	      [[ ! -d $all_stats/HREF_SNOW ]] && mkdir -p $all_stats/HREF_SNOW
	      cp $COMOUTsmall/HREF_SNOW/*_stat_HREF_SNOW_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat $all_stats/HREF_SNOW
            fi 	      
	  fi #end if check restart

        done #end of vhr
    done #end of fhr
done  #end of obsv
fi
chmod 775 run_all_href_snowfall_poe.sh
