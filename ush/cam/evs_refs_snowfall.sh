#!/bin/ksh
#************************************************************************************
#  Purpose: Generate refs snowfall poe and sub-jobs files
#  Last update: 
#     05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#***********************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs 
#******************************************
export write_job_cards=yes
>run_all_refs_snowfall_poe.sh

mkdir -p $COMOUTsmall/REFS_SNOW

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
            >run_refs_snow${obsv}.${fhr}.${vhr}.sh

           export nmem=14
           export members=14

            echo "export nmem=$nmem" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo "export regrid=G212" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            
            echo  "export output_base=$WORK/precip/run_refs_snow${obsv}" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            
            echo  "export obsv=${obsv}" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export obsvpath=$COMSNOW" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export obsvgrid=grid184" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export OBTYPE=NOHRSC" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh 

            echo  "export name=WEASD" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export name_obsv=ASNOW" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            if [ $obsv = 6h ] ; then
               echo  "export level=A06" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export thresh='ge0.0254, ge0.0508, ge0.1016, ge0.2032'" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vbeg=$vhr" >>run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vend=$vhr" >>run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export valid_increment=21600" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export lead='$fhr'" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            elif [ $obsv = 24h ] ; then
               echo  "export level=A24" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export thresh='ge0.0254, ge0.1016, ge0.2032, ge0.3048'" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vbeg=$vhr" >>run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export vend=$vhr" >>run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export valid_increment=43200" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
               echo  "export lead='$fhr'" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            fi

            echo  "export MODEL=REFS_SNOW" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export regrid=FCST" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modelpath=$COMREFS" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modelgrid=conus" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export modeltail=''" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export extradir='verf_g2g/'" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh


            echo  "export verif_grid='' " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo  "export verif_poly='${maskpath}/Bukovsky_NOHRSC_CONUS.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_East.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_West.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_South.nc, ${maskpath}/Bukovsky_NOHRSC_CONUS_Central.nc' " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GenEnsProd_fcstREFS_obsNOHRSC.conf " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/EnsembleStat_fcstREFS_obsNOHRSC.conf " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstREFSmean_obsNOHRSC_G212.conf " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${SNOWFALL_CONF}/GridStat_fcstREFSmean_obsNOHRSC_NOHRSCgrid.conf " >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

            echo "for FILEn in \$output_base/stat/\${MODEL}/ensemble_stat_\${MODEL}_*_${obsv}_FHR0${fhr}_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/REFS_SNOW; fi; done" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo "for FILEn in \$output_base/stat/\${MODEL}/grid_stat_\${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/REFS_SNOW; fi; done" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo "for FILEn in \$output_base/stat/\${MODEL}/grid_stat_\${MODEL}${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/REFS_SNOW; fi; done" >> run_refs_snow${obsv}.${fhr}.${vhr}.sh

	    chmod +x run_refs_snow${obsv}.${fhr}.${vhr}.sh
            echo "${DATA}/run_refs_snow${obsv}.${fhr}.${vhr}.sh" >> run_all_refs_snowfall_poe.sh

        done #end of vhr
    done #end of fhr
done  #end of obsv
fi
chmod 775 run_all_refs_snowfall_poe.sh
