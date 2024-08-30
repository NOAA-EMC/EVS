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


    for valid_run in run1 run2 run3 run4 ; do
     # Build sub-jobs
     # **********************
     >run_refs_${model}.${dom}.${valid_run}_product.sh
     ######################################################################################################
     #Restart: check if this CONUS task has been completed in the precious run
     # if not, run this task, and then mark its completion, 
     # otherwise, skip this task
     # ###################################################################################################  
     if [ ! -e  $COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}_product.completed ] ; then
	    
       echo  "export model=REFS${prod} " >>  run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=$dom " >> run_refs_${model}.${dom}.${valid_run}_product.sh     
       echo  "export regrid=G227" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export output_base=${WORK}/grid2obs/run_refs_${model}.${dom}.${valid_run}_product" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=CONUS" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvgrid=G227" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=conus.prob" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       else
         echo  "export modelgrid=conus.${prod}" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       fi 

       echo  "export obsvhead=$obsv" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvpath=$WORK" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       if [ $valid_run = run1 ] ; then 
         echo  "export vbeg=0" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='1,2,3,4,5,6,7,8'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run2 ] ; then
         echo  "export vbeg=0" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='9,10,11,12,13,14,15,16'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run3 ] ; then
         echo  "export vbeg=0" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=23" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='17,18,19,20,21,22,23,24'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       elif [ $valid_run = run4 ] ; then
         echo  "export vbeg=0" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export vend=21" >>run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export valid_increment=10800" >> run_refs_${model}.${dom}.${valid_run}_product.sh
         echo  "export lead='27,30,33,36,39,42,45,48'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       fi 

       echo  "export MODEL=REFS_${PROD}" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=G227" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelhead=$model" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelpath=$COMREFS" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modeltail='.grib2'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export extradir='ensprod/'" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       echo  "export verif_grid=''" >> run_refs_${model}.${dom}.${valid_run}_product.sh
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
                                 ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS${prod}_obsPREPBUFR_SFC.conf " >> run_refs_${model}.${dom}.${valid_run}_product.sh

       echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       #Mark this CONUS task is completed
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}_product.completed" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       chmod +x run_refs_${model}.${dom}.${valid_run}_product.sh
       echo "${DATA}/run_refs_${model}.${dom}.${valid_run}_product.sh" >> run_all_refs_product_poe.sh

      fi 

    done # end of valid_run

   elif [ $domain = Alaska ] ; then

     for valid_run in run1 run2 run3 run4 ; do

     >run_refs_${model}.${dom}.${valid_run}_product.sh
     #######################################################################
     #Restart check: 
     # check if this Alaska task has been completed in the precious run
     # if not, run this task, and then mark its completion,
     # otherwise, skip this task
     ########################################################################
     if [ ! -e  $COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}_product.completed ] ; then

       echo  "export model=REFS${prod} " >>  run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=$dom " >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=NONE" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       echo  "export output_base=${WORK}/grid2obs/run_refs_${model}.${dom}.${valid_run}_product" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export domain=Alaska" >> run_refs_${model}.${dom}.${valid_run}_product.sh  
       echo  "export obsvgrid=G198" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       if [ $prod = sclr ] ; then
         echo  "export modelgrid=ak.prob" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       else
         echo  "export modelgrid=ak.${prod}" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       fi
       echo  "export verif_grid=''" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvhead=$obsv" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export obsvpath=$WORK" >> run_refs_${model}.${dom}.${valid_run}_product.sh

        if [ $valid_run = run1 ] ; then
           echo  "export vbeg=00" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=23" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='1,2,3,4,5,6,7,8'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
        elif [ $valid_run = run2 ] ; then
           echo  "export vbeg=00" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=23" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='9,10,11,12,13,14,15,16'" >> run_refs_${model}.${dom}.${valid_run}_product.sh

        elif [ $valid_run = run3 ] ; then
           echo  "export vbeg=00" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=23" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='17,18,19,20,21,22,23,24'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
        elif [ $valid_run = run4 ] ; then
           echo  "export vbeg=00" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export vend=21" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export valid_increment=3600" >> run_refs_${model}.${dom}.${valid_run}_product.sh
           echo  "export lead='27,30,33,36,39,42,45,48'" >> run_refs_${model}.${dom}.${valid_run}_product.sh

        else
           err_exit "$valid_run is not a valid valid_run setting"
        fi

       echo  "export MODEL=REFS_${PROD}" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export regrid=NONE" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelhead=$model" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modelpath=$COMREFS" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export modeltail='.grib2'" >> run_refs_${model}.${dom}.${valid_run}_product.sh
       echo  "export extradir='ensprod/'" >> run_refs_${model}.${dom}.${valid_run}_product.sh

 
       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS${prod}_obsPREPBUFR_SFC.conf " >> run_refs_${model}.${dom}.${valid_run}_product.sh

       echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       #Mark this Alaska task is completed
       echo "[[ \$? = 0 ]] && >$COMOUTrestart/product/run_refs_${model}.${dom}.${valid_run}_product.completed" >> run_refs_${model}.${dom}.${valid_run}_product.sh

       chmod +x run_refs_${model}.${dom}.${valid_run}_product.sh
       echo "${DATA}/run_refs_${model}.${dom}.${valid_run}_product.sh" >> run_all_refs_product_poe.sh

      fi #end if check restart

    done # end of valid_run 

   else

    err_exit "$dom is not a valid domain"

   fi   

  done #end of dom loop

done #end of prod loop

chmod 775 run_all_refs_product_poe.sh