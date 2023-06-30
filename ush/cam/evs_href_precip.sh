#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


############################################################


>run_all_href_precip_poe.sh


for obsvtype in ccpa mrms ; do

 for acc in 01h  03h 24h  ; do

   obsv=$obsvtype$acc

  for prod in mean pmmn avrg lpmm prob eas system ; do

	  
     PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

     >run_href_precip_${prod}.${obsv}.sh

     if [ $acc = 24h ] ; then
	if [ $obsvtype = ccpa ] ; then
	     echo  "export vbeg=12" >>run_href_precip_${prod}.${obsv}.sh
	     echo  "export vend=12" >>run_href_precip_${prod}.${obsv}.sh
	     echo  "export valid_increment=3600" >> run_href_precip_${prod}.${obsv}.sh
             echo  "export lead='24, 30, 36, 42, 48'" >> run_href_precip_${prod}.${obsv}.sh
	elif [ $obsvtype = mrms ] ; then
             echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
             echo  "export vend=18" >>run_href_precip_${prod}.${obsv}.sh
             echo  "export valid_increment=21600" >> run_href_precip_${prod}.${obsv}.sh
             echo  "export lead='24, 30, 36, 42, 48'" >> run_href_precip_${prod}.${obsv}.sh
        fi
     else 
                # acc=01h, 03h 
	if [ $prod = system ] ; then 
             # Since HREF members are every 3fhr stored in verf_g2g directory 
             echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
             echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
             echo  "export valid_increment=10800" >> run_href_precip_${prod}.${obsv}.sh
             echo  "export lead='3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'" >> run_href_precip_${prod}.${obsv}.sh
        else
            if [ $acc = 01h ] ; then
               echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
               echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
	       echo  "export valid_increment=3600" >> run_href_precip_${prod}.${obsv}.sh
               echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'" >> run_href_precip_${prod}.${obsv}.sh
            elif [ $acc = 03h ] ; then
               echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
	       echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
	       echo  "export valid_increment=10800" >> run_href_precip_${prod}.${obsv}.sh
	       echo  "export lead='27,30,33,36,39,42,45,48'" >> run_href_precip_${prod}.${obsv}.sh
            fi
	fi 	
    fi

      if [ $prod = system ] ; then
         echo "export MODEL=HREF" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export model=HREF" >> run_href_precip_${prod}.${obsv}.sh
         export MODEL=HREF
      else
         echo "export MODEL=HREF_${PROD}" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export model=HREF_${PROD}" >> run_href_precip_${prod}.${obsv}.sh
	 export MODEL=HREF_${PROD}
      fi

      mkdir -p  ${COMOUTsmall}/${MODEL}

      echo  "export output_base=$WORK/precip/run_href_precip_${prod}.${obsv}" >> run_href_precip_${prod}.${obsv}.sh

      echo  "export obsv=${obsv}" >> run_href_precip_${prod}.${obsv}.sh
      echo  "export obsvpath=$WORK" >> run_href_precip_${prod}.${obsv}.sh
      echo  "export OBTYPE=${obsv}" >> run_href_precip_${prod}.${obsv}.sh 

   if [ $obsv = ccpa01h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A01" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
       echo  "export thresh='ge0.254, ge6.35, ge12.7'" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then    
       echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2'" >> run_href_precip_${prod}.${obsv}.sh
     else
       echo  "export thresh='ge0.254, ge2.54, ge6.35, ge12.7, ge25.4, ge50.8'" >> run_href_precip_${prod}.${obsv}.sh
     fi

   elif [ $obsv = mrms01h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP_01" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A01" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
          echo  "export thresh='ge0.254, ge6.35, ge12.7'" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then
          echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2'" >> run_href_precip_${prod}.${obsv}.sh
     else
          echo  "export thresh='ge0.254, ge2.54, ge6.35, ge12.7, ge25.4, ge50.8'" >> run_href_precip_${prod}.${obsv}.sh
     fi

   elif [ $obsv = ccpa03h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A03" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
       echo  "export thresh=' ge0.254, ge6.35, ge12.7 '" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then
       echo  "export thresh=' ge12.7, ge25.4, ge50.8, ge76.2, ge127 '" >> run_href_precip_${prod}.${obsv}.sh
     else
       echo  "export thresh=' ge2.54, ge6.35, ge12.7, ge25.4, ge76.2 '" >> run_href_precip_${prod}.${obsv}.sh
     fi

   elif [ $obsv = mrms03h ] ; then
     echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export name_obsv=APCP_03" >> run_href_precip_${prod}.${obsv}.sh
     echo  "export level=A03" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
        echo  "export thresh=' ge0.254, ge6.35, ge12.7 '" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then
        echo  "export thresh=' ge12.7, ge25.4, ge50.8, ge76.2, ge127 '" >> run_href_precip_${prod}.${obsv}.sh
     else
        echo  "export thresh=' ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2 '" >> run_href_precip_${prod}.${obsv}.sh
     fi


   elif [ $obsv = ccpa24h ] ; then

     if [ $prod = system ] || [ $prod = prob ] || [ $prod = eas ] ; then
       echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     else
       echo  "export name=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     fi

     echo  "export level=A24" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
        echo  "export thresh='ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2'" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then
        echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127, ge203'" >> run_href_precip_${prod}.${obsv}.sh
     else
	echo  "export thresh='ge12.7, ge25.4, ge50.8'" >> run_href_precip_${prod}.${obsv}.sh
     fi


   elif [ $obsv = mrms24h ] ; then

     if [ $prod = system ] || [ $prod = prob ] || [ $prod = eas ] ; then
         echo  "export name=APCP" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     else
         echo  "export name=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
         echo  "export name_obsv=APCP_24" >> run_href_precip_${prod}.${obsv}.sh
     fi

     echo  "export level=A24" >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = eas ] ; then
        echo  "export thresh='ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2'" >> run_href_precip_${prod}.${obsv}.sh
     elif [ $prod = prob ] ; then
        echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127, ge203'" >> run_href_precip_${prod}.${obsv}.sh
     else
        echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127'" >> run_href_precip_${prod}.${obsv}.sh
     fi 

   fi


   
   if [ $obsv = ccpa01h ]  ; then
 
       echo  "export obsvtail=grib2" >> run_href_precip_${prod}.${obsv}.sh

       if [ $prod = prob ] || [ $prod = eas ] ; then
          echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
       elif [ $prod = system ] ; then
          echo  "export modelgrid=conus" >> run_href_precip_${prod}.${obsv}.sh
       else
          echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
       fi

       #echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=3600" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'" >> run_href_precip_${prod}.${obsv}.sh

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

    elif [ $obsv = mrms01h ]  ; then

       echo  "export obsvtail=nc" >> run_href_precip_${prod}.${obsv}.sh

      if [ $prod = prob ] || [ $prod = eas ] ; then
         echo  "export modelgrid=ak.${prod}" >> run_href_precip_${prod}.${obsv}.sh
      elif [ $prod = system ] ; then
         echo  "export modelgrid=ak" >> run_href_precip_${prod}.${obsv}.sh
      else
         echo  "export modelgrid=ak.${prod}" >> run_href_precip_${prod}.${obsv}.sh
      fi

       #echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=3600" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'" >> run_href_precip_${prod}.${obsv}.sh

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
    elif [ $obsv = ccpa03h ]  ; then
 
       echo  "export obsvtail=grib2" >> run_href_precip_${prod}.${obsv}.sh

       if [ $prod = prob ] || [ $prod = eas ] ; then
          echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
       elif [ $prod = system ] ; then
          echo  "export modelgrid=conus" >> run_href_precip_${prod}.${obsv}.sh
       else
          echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
       fi

       #echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=10800" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='24,27,30,33,36,39,42,45,48'" >> run_href_precip_${prod}.${obsv}.sh

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

    elif [ $obsv = mrms03h ]  ; then

      if [ $prod = prob ] || [ $prod = eas ] ; then
         echo  "export modelgrid=ak.${prod}" >> run_href_precip_${prod}.${obsv}.sh
      elif [ $prod = system ] ; then
         echo  "export modelgrid=ak" >> run_href_precip_${prod}.${obsv}.sh
      else
         echo  "export modelgrid=ak.${prod}" >> run_href_precip_${prod}.${obsv}.sh
      fi

       #echo  "export vbeg=0" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=21" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=10800" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='24,27,30,33,36,39,42,45,48'" >> run_href_precip_${prod}.${obsv}.sh

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

       echo  "export obsvtail=nc" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export vbeg=12" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=12" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=21600" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='24, 30, 36, 42, 48'" >> run_href_precip_${prod}.${obsv}.sh

      if [ $prod = prob ] || [ $prod = eas ] ; then
       echo  "export modelhead=href" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir='ensprod/'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail='.grib2'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=conus.${prod}" >> run_href_precip_${prod}.${obsv}.sh
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
       echo  "export modelgrid=G227.24h" >> run_href_precip_${prod}.${obsv}.sh
      fi


    elif [ $obsv = mrms24h ] ; then

       echo  "export obsvtail=nc" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export vbeg=00" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export vend=18" >>run_href_precip_${prod}.${obsv}.sh
       #echo  "export valid_increment=21600" >> run_href_precip_${prod}.${obsv}.sh
       #echo  "export lead='24, 30, 36, 42, 48'" >> run_href_precip_${prod}.${obsv}.sh

      if [ $prod = prob ] || [ $prod = eas ] ; then
       echo  "export modelhead=href" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir='ensprod/'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail='.grib2'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=ak.${prod}" >> run_href_precip_${prod}.${obsv}.sh
      elif [ $prod = system ] ; then
       echo  "export modelpath=$COMHREF" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir='verf_g2g/'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail=''" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=ak" >> run_href_precip_${prod}.${obsv}.sh
      else  # mean pmmn avrg lpmm (only these 24hr mean need to derived)
       echo  "export modelhead=href${prod}" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelpath=$WORK" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export extradir=''" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modeltail='.nc'" >> run_href_precip_${prod}.${obsv}.sh
       echo  "export modelgrid=G255.24h" >> run_href_precip_${prod}.${obsv}.sh
      fi



     else

      echo "Wrong obsv: $obsv"
      exit

     fi 
      
     echo  "export verif_grid='' " >> run_href_precip_${prod}.${obsv}.sh

     if [ $prod = prob ] || [ $prod = eas ] ; then

	 if [ $obsvtype = ccpa ] ; then
           echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc, ${maskpath}/Bukovsky_G227_CONUS_East.nc, ${maskpath}/Bukovsky_G227_CONUS_West.nc, ${maskpath}/Bukovsky_G227_CONUS_South.nc, ${maskpath}/Bukovsky_G227_CONUS_Central.nc' " >> run_href_precip_${prod}.${obsv}.sh

           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFprob_obsCCPA_G227.conf " >> run_href_precip_${prod}.${obsv}.sh

         else
	   echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_href_precip_${prod}.${obsv}.sh
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFprob_obsMRMS_G255.conf " >> run_href_precip_${prod}.${obsv}.sh
	 fi

       elif [ $prod = system ] ; then

	 if [ $obsvtype = ccpa ] ; then
           echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc, ${maskpath}/Bukovsky_G227_CONUS_East.nc, ${maskpath}/Bukovsky_G227_CONUS_West.nc, ${maskpath}/Bukovsky_G227_CONUS_South.nc, ${maskpath}/Bukovsky_G227_CONUS_Central.nc' " >> run_href_precip_${prod}.${obsv}.sh
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstHREF_obsCCPA_G227.conf " >> run_href_precip_${prod}.${obsv}.sh
         else
	   echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_href_precip_${prod}.${obsv}.sh
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstHREF_obsMRMS_G255.conf " >> run_href_precip_${prod}.${obsv}.sh
	 fi

       else
        
         if [ $obsvtype = ccpa ] ; then

	   echo  "export verif_poly='${maskpath}/Bukovsky_G212_CONUS.nc, ${maskpath}/Bukovsky_G212_CONUS_East.nc, ${maskpath}/Bukovsky_G212_CONUS_West.nc, ${maskpath}/Bukovsky_G212_CONUS_South.nc, ${maskpath}/Bukovsky_G212_CONUS_Central.nc' " >> run_href_precip_${prod}.${obsv}.sh	 
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFmean_obsCCPA_G212.conf " >> run_href_precip_${prod}.${obsv}.sh
	   echo  "export verif_poly='${maskpath}/Bukovsky_G240_CONUS.nc, ${maskpath}/Bukovsky_G240_CONUS_East.nc, ${maskpath}/Bukovsky_G240_CONUS_West.nc, ${maskpath}/Bukovsky_G240_CONUS_South.nc, ${maskpath}/Bukovsky_G240_CONUS_Central.nc' " >> run_href_precip_${prod}.${obsv}.sh
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFmean_obsCCPA_G240.conf " >> run_href_precip_${prod}.${obsv}.sh

          else
           echo  "export verif_poly='${maskpath}/Alaska_G216.nc' " >> run_href_precip_${prod}.${obsv}.sh
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFmean_obsMRMS_G216.conf " >> run_href_precip_${prod}.${obsv}.sh
	   echo  "export verif_poly='${maskpath}/Alaska_G091.nc' " >> run_href_precip_${prod}.${obsv}.sh
	   echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstHREFmean_obsMRMS_G91.conf " >> run_href_precip_${prod}.${obsv}.sh

          fi

       fi

       echo "cp \$output_base/stat/${MODEL}/*.stat $COMOUTsmall/${MODEL}" >> run_href_precip_${prod}.${obsv}.sh
       chmod +x run_href_precip_${prod}.${obsv}.sh
       echo "${DATA}/run_href_precip_${prod}.${obsv}.sh" >> run_all_href_precip_poe.sh

    done #end of prod

 done  #end of obsv

done # end of domain 

exit
