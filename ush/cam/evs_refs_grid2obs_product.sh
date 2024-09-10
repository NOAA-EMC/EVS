#!/bin/ksh
#***************************************************************************************
#  Purpose: Generate refs grid2obs product joe and sub-jobs files by directly using refs 
#           operational ensemble mean and probability product files   
#  Last update: 
#              05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#***************************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_refs_product_poe.sh

obsv='prepbufr'

for prod in mean prob ; do

 PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

 model=REFS${prod}

 for dom in CONUS Alaska ; do

    export domain=$dom

   if [ $domain = CONUS ] ; then


    for valid_run in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 1 22 23 ; do

     if [ $valid_run = 00 ] || [ $valid_run = 06 ] || [ $valid_run = 12 ] || [ $valid_run = 18 ] ; then
       fhrs="06 12 18 24 30 36 42 48"
     elif [ $valid_run = 01 ] || [ $valid_run = 07 ] || [ $valid_run = 13 ] || [ $valid_run = 19 ] ; then
       fhrs="01 07 13 19" 
     elif [ $valid_run = 02 ] || [ $valid_run = 08 ] || [ $valid_run = 14 ] || [ $valid_run = 20 ] ; then
       fhrs="02 08 14 20"
     elif [ $valid_run = 03 ] || [ $valid_run = 09 ] || [ $valid_run = 15 ] || [ $valid_run = 21 ] ; then
       fhr="03 09 15 21 27 33 39 45" 
     elif [ $valid_run = 04 ] || [ $valid_run = 10 ] || [ $valid_run = 16 ] || [ $valid_run = 22 ] ; then  
       fhrs="04 10 16 22"
     elif [ $valid_run = 05 ] || [ $valid_run = 11 ] || [ $valid_run = 17 ] || [ $valid_run = 23 ] ; then
       fhrs="05 11 17 23"
     fi

     for fhr in $fhrs ; do

     # Build sub-jobs
     # **********************
     >run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
     ######################################################################################################
     #Restart: check if this CONUS task has been completed in the precious run
     # if not, run this task, and then mark its completion, 
     # otherwise, skip this task
     # ###################################################################################################  
     if [ ! -e  $COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}.${fhr}_product.completed ] ; then
	
      ihr=`$NDATE -$fhr $VDATE$valid_run|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_run|cut -c 1-8`
  
      if [ -s $COMINrefs/refs.${iday}/ensprod/refs.t${ihr}z.conus.${prod}.f${fhr}.grib2 ] ; then

       echo  "export model=REFS${prod} " >>  run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=$dom " >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh     
       echo  "export regrid=G227" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export output_base=${WORK}/grid2obs/run_refs_${model}.${dom}.${valid_run}.${fhr}_product" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=CONUS" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvgrid=G227" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=conus.prob" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       else
         echo  "export modelgrid=conus.${prod}" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       fi 

       echo  "export obsvhead=$obsv" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvpath=$WORK" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export vbeg=$valid_run" >>run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export vend=$valid_run" >>run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export lead=$fhr" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export MODEL=REFS_${PROD}" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=G227" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelhead=$model" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelpath=$COMREFS" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modeltail='.grib2'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export extradir='ensprod/'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export verif_grid=''" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
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
                                 ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS${prod}_obsPREPBUFR_SFC.conf " >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       #Mark this CONUS task is completed
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}.${fhr}_product.completed" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       chmod +x run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "${DATA}/run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh" >> run_all_refs_product_poe.sh
      fi

     fi 

     done # end of fhr
    done # end of valid_run

   elif [ $domain = Alaska ] ; then

    for valid_run in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 1 22 23 ; do
     if [ $valid_run = 00 ] || [ $valid_run = 06 ] || [ $valid_run = 12 ] || [ $valid_run = 18 ] ; then
       fhrs="06 12 18 24 30 36 42 48"
     elif [ $valid_run = 01 ] || [ $valid_run = 07 ] || [ $valid_run = 13 ] || [ $valid_run = 19 ] ; then
       fhrs="01 07 13 19"
     elif [ $valid_run = 02 ] || [ $valid_run = 08 ] || [ $valid_run = 14 ] || [ $valid_run = 20 ] ; then
       fhrs="02 08 14 20"
     elif [ $valid_run = 03 ] || [ $valid_run = 09 ] || [ $valid_run = 15 ] || [ $valid_run = 21 ] ; then
       fhr="03 09 15 21 27 33 39 45"
    elif [ $valid_run = 04 ] || [ $valid_run = 10 ] || [ $valid_run = 16 ] || [ $valid_run = 22 ] ; then
       fhrs="04 10 16 22"
    elif [ $valid_run = 05 ] || [ $valid_run = 11 ] || [ $valid_run = 17 ] || [ $valid_run = 23 ] ; then
       fhrs="05 11 17 23"
    fi

    for fhr in $fhrs ; do

     >run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
     #######################################################################
     #Restart check: 
     # check if this Alaska task has been completed in the precious run
     # if not, run this task, and then mark its completion,
     # otherwise, skip this task
     ########################################################################
     if [ ! -e  $COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}.${fhr}_product.completed ] ; then

      ihr=`$NDATE -$fhr $VDATE$valid_run|cut -c 9-10`
      iday=`$NDATE -$fhr $VDATE$valid_run|cut -c 1-8`

      if [ -s $COMINrefs/refs.${iday}/ensprod/refs.t${ihr}z.ak.${prod}.f${fhr}.grib2 ] ; then

       echo  "export model=REFS${prod} " >>  run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=$dom " >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=NONE" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export output_base=${WORK}/grid2obs/run_refs_${model}.${dom}.${valid_run}.${fhr}_product" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export domain=Alaska" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh  
       echo  "export obsvgrid=G198" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=ak.prob" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       else
         echo  "export modelgrid=ak.${prod}" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       fi
       echo  "export verif_grid=''" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvhead=$obsv" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export obsvpath=$WORK" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export vbeg=$valid_run" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export vend=$valid_run" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export lead=$fhr" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "export MODEL=REFS_${PROD}" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export regrid=NONE" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelhead=$model" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modelpath=$COMREFS" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export modeltail='.grib2'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo  "export extradir='ensprod/'" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

 
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS${prod}_obsPREPBUFR_SFC.conf " >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       #Mark this Alaska task is completed
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}.${fhr}_product.completed" >> run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh

       chmod +x run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh
       echo "${DATA}/run_refs_${model}.${dom}.${valid_run}.${fhr}.product.sh" >> run_all_refs_product_poe.sh

      fi 

     fi #end if check restart

     done #end of fhr 
    done # end of valid_run 

   else

    err_exit "$dom is not a valid domain"

   fi   

  done #end of dom loop

done #end of prod loop

chmod 775 run_all_refs_product_poe.sh
