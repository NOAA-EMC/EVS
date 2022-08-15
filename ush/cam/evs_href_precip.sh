#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


############################################################


>run_all_href_precip_poe.sh


#for precip in ccpa01h03h ccpa24h apcp24h ; do
#  $USHverf/cam/stats/evs_preppare_href.sh  $precip
#done


for obsv in ccpa01h ccpa03h ccpa24h  ; do

 #for prod in mean pmmn avrg lpmm prob sclr eas ; do
 for prod in mean pmmn avrg lpmm prob system; do

     PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

     >run_href_precip_${prod}.${obsv}.sh

      echo "export regrid=G212" >> run_href_precip_${prod}.${obsv}.sh

      if [ $prod = system ] ; then
         echo "export MODEL=HREF" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export model=HREF" >> run_href_precip_${prod}.${obsv}.sh
      else
         echo "export MODEL=HREF_${PROD}" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export model=HREF_${PROD}" >> run_href_precip_${prod}.${obsv}.sh
      fi

      echo  "export output_base=$WORK/precip/run_href_precip_${prod}.${obsv}" >> run_href_precip_${prod}.${obsv}.sh

      echo  "export obsv=${obsv}" >> run_href_precip_${prod}.${obsv}.sh
      echo  "export obsvpath=$WORK" >> run_href_precip_${prod}.${obsv}.sh
      echo  "export OBTYPE=${obsv}" >> run_href_precip_${prod}.${obsv}.sh 

   if [ $obsv = ccpa01h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A01" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export thresh='ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2'" >> run_href_precip_${prod}.${obsv}.sh
   elif [ $obsv = ccpa03h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A03" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export thresh=' ge12.7, ge25.4, ge50.8, ge76.2, ge127 '" >> run_href_precip_${prod}.${obsv}.sh
   elif [ $obsv = ccpa24h ] ; then
     if [ $prod = system ] || [ $prod = prob ] ; then
       echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     else
       echo  "export name=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     fi
     echo  "export level=A24" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127, ge203'" >> run_href_precip_${prod}.${obsv}.sh
   fi

   if [ $obsv = ccpa01h ] || [ $obsv = ccpa03h ]  ; then
 
        if [ $prod = prob ] ; then
          echo  "export modelgrid=conus.prob" >> run_href_precip_${prod}.${obsv}.sh
        elif [ $prod = system ] ; then
          echo  "export modelgrid=conus" >> run_href_precip_${prod}.${obsv}.sh
        else
          echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
        fi

       echo  "export obsvgrid=G227" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export obsvtail=grib2" >> run_href_precip_${prod}.${obsv}.sh

       if [ $obsv = ccpa01h ] ; then 
         echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
         echo  "export vend=23" >>run_href_precip_${prod}.${obsv}.sh

         echo  "export valid_increment=3600" >> run_href_precip_${prod}.${obsv}.sh
          if [ $prod = system ] ; then #for syetem verif, single href members only output at every 3hr
             echo  "export lead='3,6,9,12,15,18,21,24'" >> run_href_precip_${prod}.${obsv}.sh
          else
             echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24'" >> run_href_precip_${prod}.${obsv}.sh
          fi
        elif [ $obsv = ccpa03h ] ; then
         echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
         echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
         echo  "export valid_increment=10800" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export lead='24,27,30,33,36,39,42,45,48'" >> run_href_precip_${prod}.${obsv}.sh
       fi    

       if [ $prod = system ] ; then
         echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export modeltail=''" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export extradir='verf_g2g/'" >> run_href_precip_${prod}.${obsv}.sh
       else
         echo  "export modelhead=href" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export modeltail='.grib2'" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export extradir='ensprod/'" >> run_href_precip_${prod}.${obsv}.sh
       fi


    elif [ $obsv = ccpa24h ] ; then

       echo  "export obsvgrid=G227" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export obsvtail=nc" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export vbeg=12" >>run_href_precip_${prod}.${obsv}.sh
       echo  "export vend=12" >>run_href_precip_${prod}.${obsv}.sh
       echo  "export valid_increment=21600" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export lead='24, 30, 36, 42, 48'" >> run_href_precip_${prod}.${obsv}.sh

      if [ $prod = prob ] ; then
       echo  "export modelhead=href" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir='ensprod/'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail='.grib2'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=conus.prob" >> run_href_precip_${prod}.${obsv}.sh
      elif [ $prod = system ] ; then
       echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir='verf_g2g/'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail=''" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=conus" >> run_href_precip_${prod}.${obsv}.sh
      else  # mean pmmn avrg lpmm (only these 24hr mean need to derived)
       echo  "export modelhead=href${prod}" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelpath=$WORK" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir=''" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail='.nc'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=conus.24h" >> run_href_precip_${prod}.${obsv}.sh
      fi

     else

      exit

     fi 
      
      echo  "export regrid=NONE" >> run_href_precip_${prod}.${obsv}.sh 
      echo  "export verif_grid='' " >> run_href_precip_${prod}.${obsv}.sh
      echo  "export verif_poly='${maskpath}/Bukovsky_G212_CONUS.nc, ${maskpath}/Bukovsky_G212_CONUS_East.nc, ${maskpath}/Bukovsky_G212_CONUS_West.nc, ${maskpath}/Bukovsky_G212_CONUS_South.nc, ${maskpath}/Bukovsky_G212_CONUS_Central.nc' " >> run_href_precip_${prod}.${obsv}.sh


       if [ $prod = prob ] ; then

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFprob_obsCCPA.conf " >> run_href_precip_${prod}.${obsv}.sh

       elif [ $prod = system ] ; then

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstHREF_obsCCPA.conf " >> run_href_precip_${prod}.${obsv}.sh

       else

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFmean_obsCCPA.conf " >> run_href_precip_${prod}.${obsv}.sh

       fi

       echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_precip_${prod}.${obsv}.sh
       chmod +x run_href_precip_${prod}.${obsv}.sh
       echo "run_href_precip_${prod}.${obsv}.sh" >> run_all_href_precip_poe.sh

    done #end of prod

 done  #end of obsv

exit
