#!/bin/ksh
#************************************************************************************
#  Purpose: Generate href snowfall poe and sub-jobs files
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#***********************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs 
#******************************************
export members=10
export write_job_cards=yes
>run_all_href_snowfall_poe.sh

mkdir -p $COMOUTsmall/HREF_SNOW

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
            ihr=`$NDATE -$fhr $VDATE$vhr|cut -c 9-10`
            if [ "$ihr" -eq "00" ] || [ "$ihr" -eq "12" ] ; then
                if [ "$fhr" -ge "45" ] ; then
                    export nmem=7
                    export members=7
                elif [ "$fhr" -ge "39" ] ; then
                    export nmem=8
                    export members=8
                else
                    export nmem=10
                    export members=10
                fi
            elif [ "$ihr" -eq "06" ] || [ "$ihr" -eq "18" ] ; then
                if [ "$fhr" -ge "45" ] ; then
                    export nmem=4
                    export members=4
                elif [ "$fhr" -ge "33" ] ; then
                    export nmem=8
                    export members=8
                else
                    export nmem=10
                    export members=10
                fi
            else
                export nmem=10
                export members=10
            fi

            echo "export nmem=$nmem" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "export regrid=G212" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            
            echo  "export output_base=$WORK/precip/run_href_snow${obsv}" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            
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

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/EnsembleStat_fcstHREF_obsNOHRSC.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstHREFmean_obsNOHRSC_G212.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstHREFmean_obsNOHRSC_NOHRSCgrid.conf " >> run_href_snow${obsv}.${fhr}.${vhr}.sh

            echo "for FILEn in \$output_base/stat/\${MODEL}/ensemble_stat_\${MODEL}_*_${obsv}_FHR0${fhr}_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/HREF_SNOW; fi; done" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "for FILEn in \$output_base/stat/\${MODEL}/grid_stat_\${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/HREF_SNOW; fi; done" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "for FILEn in \$output_base/stat/\${MODEL}/grid_stat_\${MODEL}${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/HREF_SNOW; fi; done" >> run_href_snow${obsv}.${fhr}.${vhr}.sh
            chmod +x run_href_snow${obsv}.${fhr}.${vhr}.sh
            echo "${DATA}/run_href_snow${obsv}.${fhr}.${vhr}.sh" >> run_all_href_snowfall_poe.sh

        done #end of vhr
    done #end of fhr
done  #end of obsv
fi
chmod 775 run_all_href_snowfall_poe.sh
