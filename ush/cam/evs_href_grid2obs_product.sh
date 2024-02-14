#!/bin/ksh
#***************************************************************************************
#  Purpose: Generate href grid2obs product joe and sub-jobs files by directly using href 
#           operational ensemble mean and probability product files   
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#***************************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_href_product_poe.sh

obsv='prepbufr'

for prod in mean prob ; do

 PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

 model=HREF${prod}

 for dom in CONUS Alaska ; do

    export domain=$dom

   if [ $domain = CONUS ] ; then


    for valid_run in run1 run2 run3 run4 ; do

     
     #***********************
     # Build sub-jobs
     # **********************
     >run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid_run}_product.sh     
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid_run}_product.sh

       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid_run}_product" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=CONUS" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvgrid=G227" >> run_href_${model}.${dom}.${valid_run}_product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=conus.prob" >> run_href_${model}.${dom}.${valid_run}_product.sh
       else
         echo  "export modelgrid=conus.${prod}" >> run_href_${model}.${dom}.${valid_run}_product.sh
       fi 

       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid_run}_product.sh

       if [ $valid_run = run1 ] ; then 
         echo  "export vbeg=0" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='1,2,3,4,5,6,7,8'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run2 ] ; then
         echo  "export vbeg=0" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='9,10,11,12,13,14,15,16'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run3 ] ; then
         echo  "export vbeg=0" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='17,18,19,20,21,22,23,24'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run4 ] ; then
         echo  "export vbeg=0" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=21" >>run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=10800" >> run_href_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='27,30,33,36,39,42,45,48'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       fi 

       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid_run}_product.sh

       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid_run}_product.sh
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
                                 ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_href_${model}.${dom}.${valid_run}_product.sh


         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SFC.conf " >> run_href_${model}.${dom}.${valid_run}_product.sh

  	 echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_${model}.${dom}.${valid_run}_product.sh

       chmod +x run_href_${model}.${dom}.${valid_run}_product.sh
       echo "${DATA}/run_href_${model}.${dom}.${valid_run}_product.sh" >> run_all_href_product_poe.sh

    done # end of valid_run

   elif [ $domain = Alaska ] ; then

     for valid_run in run1 run2 run3 run4 ; do

     >run_href_${model}.${dom}.${valid_run}_product.sh

       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=NONE" >> run_href_${model}.${dom}.${valid_run}_product.sh

       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid_run}_product" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=Alaska" >> run_href_${model}.${dom}.${valid_run}_product.sh  
       echo  "export obsvgrid=G198" >> run_href_${model}.${dom}.${valid_run}_product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=ak.prob" >> run_href_${model}.${dom}.${valid_run}_product.sh
       else
         echo  "export modelgrid=ak.${prod}" >> run_href_${model}.${dom}.${valid_run}_product.sh
       fi
       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid_run}_product.sh

        if [ $valid_run = run1 ] ; then
           echo  "export vbeg=00" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=11" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16'" >> run_href_${model}.${dom}.${valid_run}_product.sh
        elif [ $valid_run = run2 ] ; then
           echo  "export vbeg=00" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=12" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='17,18,19,20,21,22,23,24,27,30,33,36,39,42,45,48'" >> run_href_${model}.${dom}.${valid_run}_product.sh

        elif [ $valid_run = run3 ] ; then
           echo  "export vbeg=12" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=23" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16'" >> run_href_${model}.${dom}.${valid_run}_product.sh
        elif [ $valid_run = run4 ] ; then
           echo  "export vbeg=13" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=23" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='17,18,19,20,21,22,23,24,27,30,33,36,39,42,45,48'" >> run_href_${model}.${dom}.${valid_run}_product.sh

        else
           err_exit "$valid_run is not a valid valid_run setting"
        fi

       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=NONE" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid_run}_product.sh

 
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SFC.conf " >> run_href_${model}.${dom}.${valid_run}_product.sh
       echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_${model}.${dom}.${valid_run}_product.sh
       chmod +x run_href_${model}.${dom}.${valid_run}_product.sh
       echo "${DATA}/run_href_${model}.${dom}.${valid_run}_product.sh" >> run_all_href_product_poe.sh

    done # end of valid_run 

   else

    err_exit "$dom is not a valid domain"

   fi   

  done #end of dom loop

done #end of prod loop

chmod 775 run_all_href_product_poe.sh
