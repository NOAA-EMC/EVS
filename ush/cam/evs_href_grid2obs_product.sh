#!/bin/ksh
#***************************************************************************************
#  Purpose: Generate href grid2obs product joe and sub-jobs files by directly using href 
#           operational ensemble mean and probability product files   
#  Last update: 
#              01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#              10/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#***************************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
cd $DATA/scripts
>run_all_href_product_poe.sh

obsv='prepbufr'

for prod in mean prob ; do

 PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

 model=HREF${prod}

 for dom in CONUS Alaska ; do

    export domain=$dom

   if [ $domain = CONUS ] ; then


    for valid_run in 00 03 06 09 12 15 18 21 ; do
      if [ $valid_run = 00 ] || [ $valid_run = 06 ] || [ $valid_run = 12 ] || [ $valid_run = 18 ] ; then
        fhrs="06 12 18 24 30 36 42 48"
      elif [ $valid_run = 03 ] || [ $valid_run = 09 ] || [ $valid_run = 15 ] || [ $valid_run = 21 ] ; then
        fhrs="03 09 15 21 27 33 39 45" 
      fi

     for fhr in $fhrs ; do

     # Build sub-jobs
     # **********************
     >run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
     ######################################################################################################
     #Restart: check if this CONUS task has been completed in the previous run
     # if not, run this task, and then mark its completion, 
     # otherwise, skip this task
     # ###################################################################################################  
     if [ ! -e  $COMOUTrestart/product/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed ] ; then
	
      ihr=`$NDATE -$fhr $VDATE$valid_run|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_run|cut -c 1-8`
  
      input_fcst="$COMINhref/href.${iday}/ensprod/href.t${ihr}z.conus.${prod}.f${fhr}.grib2"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${valid_run}z.G227.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

       echo  "#!/bin/ksh" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "set -x" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh       
       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh     
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid_run}.${fhr}_product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=CONUS" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvgrid=G227" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=conus.prob" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       else
         echo  "export modelgrid=conus.${prod}" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       fi 

       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export vbeg=$valid_run" >>run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export vend=$valid_run" >>run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export lead=$fhr" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
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
                                 ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SFC.conf " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export err=\$?; err_chk" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh 

       echo " if [ \$? = 0 ] ; then" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  echo completed >\$output_base/stat/\${MODEL}/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  cp -v \$output_base/stat/\${MODEL}/*.stat $all_stats" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  " if [ $SENDCOM = YES ] ; then " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "    mkdir -p $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "   cp -v \$output_base/stat/\${MODEL}/*.stat  $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       #Mark this CONUS task is completed
       echo "    cp -v \$output_base/stat/\${MODEL}/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed $COMOUTrestart/product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  fi" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "fi" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       chmod +x run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "${DATA}/scripts/run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh" >> run_all_href_product_poe.sh

      fi

     else
       #Copy stat files from restart
       if [ -s $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product/*.stat ] ; then
	    cp $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product/*.stat $all_stats
       fi
     fi 

     done # end of fhr
    done # end of valid_run

   elif [ $domain = Alaska ] ; then

    for valid_run in 00 03 06 09 12 15 18 21 ; do
      if [ $valid_run = 00 ] || [ $valid_run = 06 ] || [ $valid_run = 12 ] || [ $valid_run = 18 ] ; then
        fhrs="06 12 18 24 30 36 42 48"
      elif [ $valid_run = 03 ] || [ $valid_run = 09 ] || [ $valid_run = 15 ] || [ $valid_run = 21 ] ; then
        fhrs="03 09 15 21 27 33 39 45"
      fi

    for fhr in $fhrs ; do

     >run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
     #######################################################################
     #Restart check: 
     # check if this Alaska task has been completed in the previous run
     # if not, run this task, and then mark its completion,
     # otherwise, skip this task
     ########################################################################
     if [ ! -e  $COMOUTrestart/product/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_run|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_run|cut -c 1-8`

      input_fcst="$COMINhref/href.${iday}/ensprod/href.t${ihr}z.ak.${prod}.f${fhr}.grib2"
      input_obsv="$WORK/prepbufr.${VDATE}/prepbufr.t${valid_run}z.G198.nc"

      if [ -s $input_fcst ] && [ -s $input_obsv ] ; then

       echo  "#!/bin/ksh" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh	      
       echo  "set -x" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh	      
       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=NONE" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid_run}.${fhr}_product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=Alaska" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh  
       echo  "export obsvgrid=G198" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=ak.prob" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       else
         echo  "export modelgrid=ak.${prod}" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       fi
       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export vbeg=$valid_run" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export vend=$valid_run" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export lead=$fhr" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=NONE" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

 
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SFC.conf " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export err=\$?; err_chk" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo " if [ \$? = 0 ] ; then" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  echo completed >\$output_base/stat/\${MODEL}/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  cp \$output_base/stat/\${MODEL}/*.stat $all_stats" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  if [ $SENDCOM = YES ] ; then " >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "    mkdir -p $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "    cp -v \$output_base/stat/\${MODEL}/*.stat  $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "    cp -v \$output_base/stat/\${MODEL}/run_href_${model}.${dom}.${valid_run}.${fhr}_product.completed $COMOUTrestart/product" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "  fi" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "fi" >> run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh

       chmod +x run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "${DATA}/scripts/run_href_${model}.${dom}.${valid_run}.${fhr}.product.sh" >> run_all_href_product_poe.sh

      fi 

     else
       #Copy stat files from restart
       if [ -s $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product/*.stat ] ; then
	 cp $COMOUTsmall/run_href_${model}.${dom}.${valid_run}.${fhr}.product/*.stat $all_stats
       fi

     fi #end if check restart

     done #end of fhr 
    done # end of valid_run 

   else

    err_exit "$dom is not a valid domain"

   fi   

  done #end of dom loop

done #end of prod loop

chmod 775 run_all_href_product_poe.sh
