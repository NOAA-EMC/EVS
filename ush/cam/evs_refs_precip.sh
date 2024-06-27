#!/bin/ksh
#************************************************************************************
#  Purpose: Generate refs precip poe and sub-jobs files
#           including 4 mean (mean, pmmn, lpmm and average), probability (prob, eas)
#           and system (ecnt line type)
#  Last update: 
#      05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#***********************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs 
#******************************************
>run_all_refs_precip_poe.sh


for obsvtype in ccpa mrms ; do

   for acc in 01h  03h 24h  ; do

      obsv=$obsvtype$acc

      for prod in mean pmmn avrg lpmm prob eas system ; do

	  
         PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

         #************************************
         # Build sub-jobs
         # ***********************************

         if [ $acc = 24h ] ; then
 	    if [ $obsvtype = ccpa ] ; then
               export fhrs="24 30 36 42 48"
               export vhrs="12"
 	    elif [ $obsvtype = mrms ] ; then
               export fhrs="24 30 36 42 48"
               export vhrs="00 06 12 18"
            fi
         else 
 	    if [ $prod = system ] ; then 
               export fhrs="03 06 09 12 15 18 21 24 27 30 33 36 39 42 45 48"
               export vhrs="00 03 06 09 12 15 18 21"
            else
               if [ $acc = 01h ] ; then
                  export fhrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
                  export vhrs="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
               elif [ $acc = 03h ] ; then
                  export fhrs="27 30 33 36 39 42 45 48"
                  export vhrs="00 03 06 09 12 15 18 21"
               fi
            fi
         fi

	 #Before fhr=48, all 14 members are available
	 export nmem=14
	 export members=14

         for fhr in $fhrs; do

            for vhr in $vhrs; do
               >run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh

 	       echo  "export nmem=$nmem" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               
               if [ $acc = 24h ] ; then
 	              if [ $obsvtype = ccpa ] ; then
 	                 echo  "export vbeg=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                 echo  "export vend=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                 echo  "export valid_increment=3600" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export lead='$fhr'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	              elif [ $obsvtype = mrms ] ; then
                     echo  "export vbeg=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export vend=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export valid_increment=21600" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export lead='$fhr'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
               else 
 	              if [ $prod = system ] ; then 
                     # Since REFS members are every 3fhr stored in verf_g2g directory 
                     echo  "export vbeg=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export vend=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export valid_increment=10800" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export lead='$fhr'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     if [ $acc = 01h ] ; then
                        echo  "export vbeg=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                        echo  "export vend=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                    echo  "export valid_increment=3600" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                        echo  "export lead='$fhr'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     elif [ $acc = 03h ] ; then
                        echo  "export vbeg=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                    echo  "export vend=$vhr" >>run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                    echo  "export valid_increment=10800" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                    echo  "export lead='$fhr'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     fi
 	              fi 	
               fi
 
               if [ $prod = system ] ; then
                  echo "export MODEL=REFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export model=REFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  export MODEL=REFS
               else
                  echo "export MODEL=REFS_${PROD}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export model=REFS_${PROD}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	             export MODEL=REFS_${PROD}
               fi
 
               mkdir -p  ${COMOUTsmall}/${MODEL}
               echo  "export output_base=$WORK/precip/run_refs_precip_${prod}.${obsv}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               echo  "export obsv=${obsv}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               echo  "export obsvpath=$WORK" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               echo  "export OBTYPE=${obsv}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh 
 
               if [ $obsv = ccpa01h ] ; then
                  echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export name_obsv=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export level=A01" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh='ge0.254, ge6.35, ge12.7'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then    
                     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export thresh='ge0.254, ge2.54, ge6.35, ge12.7, ge25.4, ge50.8'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms01h ] ; then
                  echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export name_obsv=APCP_01" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export level=A01" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh='ge0.254, ge6.35, ge12.7'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then
                     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export thresh='ge0.254, ge2.54, ge6.35, ge12.7, ge25.4, ge50.8'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = ccpa03h ] ; then
                  echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export name_obsv=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export level=A03" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh=' ge0.254, ge6.35, ge12.7 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then
                     echo  "export thresh=' ge12.7, ge25.4, ge50.8, ge76.2, ge127 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export thresh=' ge2.54, ge6.35, ge12.7, ge25.4, ge76.2 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms03h ] ; then
                  echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export name_obsv=APCP_03" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  echo  "export level=A03" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh=' ge0.254, ge6.35, ge12.7 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then
                     echo  "export thresh=' ge12.7, ge25.4, ge50.8, ge76.2, ge127 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export thresh=' ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2 '" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = ccpa24h ] ; then
                  if [ $prod = system ] || [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export name_obsv=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export name=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export name_obsv=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  echo  "export level=A24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh='ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then
                     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127, ge203.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
 	                echo  "export thresh='ge12.7, ge25.4, ge50.8'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms24h ] ; then
                  if [ $prod = system ] || [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export name=APCP" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export name_obsv=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export name=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export name_obsv=APCP_24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  echo  "export level=A24" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = eas ] ; then
                     echo  "export thresh='ge2.54, ge6.35, ge12.7, ge25.4, ge50.8, ge76.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = prob ] ; then
                     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127, ge203.2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export thresh='ge12.7, ge25.4, ge50.8, ge76.2, ge127'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi 
 
               fi
       
               if [ $obsv = ccpa01h ]  ; then
                  echo  "export obsvtail=grib2" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelgrid=conus.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelgrid=conus" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelgrid=conus.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  if [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms01h ]  ; then
                  echo  "export obsvtail=nc" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelgrid=ak.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelgrid=ak" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelgrid=ak.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  if [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi

               elif [ $obsv = ccpa03h ]  ; then
                  echo  "export obsvtail=grib2" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelgrid=conus.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelgrid=conus" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelgrid=conus.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  if [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms03h ]  ; then
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelgrid=ak.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelgrid=ak" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelgrid=ak.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
                  if [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = ccpa24h ] ; then
                  echo  "export obsvtail=nc" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=conus.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=conus" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else  # mean pmmn avrg lpmm (only these 24hr mean need to derived)
                     echo  "export modelhead=refs${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$WORK" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.nc'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=G227.24h" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               elif [ $obsv = mrms24h ] ; then
                  echo  "export obsvtail=nc" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  if [ $prod = prob ] || [ $prod = eas ] ; then
                     echo  "export modelhead=refs" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='ensprod/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.grib2'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=ak.${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  elif [ $prod = system ] ; then
                     echo  "export modelpath=$COMREFS" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir='verf_g2g/'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=ak" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else  # mean pmmn avrg lpmm (only these 24hr mean need to derived)
                     echo  "export modelhead=refs${prod}" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelpath=$WORK" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export extradir=''" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modeltail='.nc'" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "export modelgrid=G255.24h" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi
 
               else
                  err_exit "$obsv is not a valid obsv"

               fi 
          
               echo  "export verif_grid='' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               if [ $prod = prob ] || [ $prod = eas ] ; then
 
 	          if [ $obsvtype = ccpa ] ; then
                     echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc, ${maskpath}/Bukovsky_G227_CONUS_East.nc, ${maskpath}/Bukovsky_G227_CONUS_West.nc, ${maskpath}/Bukovsky_G227_CONUS_South.nc, ${maskpath}/Bukovsky_G227_CONUS_Central.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSprob_obsCCPA_G227.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
 	                 echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSprob_obsMRMS_G255.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	          fi
 
               elif [ $prod = system ] ; then
 	          if [ $obsvtype = ccpa ] ; then
                     echo  "export verif_poly='${maskpath}/Bukovsky_G227_CONUS.nc, ${maskpath}/Bukovsky_G227_CONUS_East.nc, ${maskpath}/Bukovsky_G227_CONUS_West.nc, ${maskpath}/Bukovsky_G227_CONUS_South.nc, ${maskpath}/Bukovsky_G227_CONUS_Central.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstREFS_obsCCPA_G227.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
 	                 echo  "export verif_poly='${maskpath}/Alaska_HREF.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/EnsembleStat_fcstREFS_obsMRMS_G255.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	          fi
 
               else
                  if [ $obsvtype = ccpa ] ; then
 	                 echo  "export verif_poly='${maskpath}/Bukovsky_G212_CONUS.nc, ${maskpath}/Bukovsky_G212_CONUS_East.nc, ${maskpath}/Bukovsky_G212_CONUS_West.nc, ${maskpath}/Bukovsky_G212_CONUS_South.nc, ${maskpath}/Bukovsky_G212_CONUS_Central.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh	 
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSmean_obsCCPA_G212.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	                 echo  "export verif_poly='${maskpath}/Bukovsky_G240_CONUS.nc, ${maskpath}/Bukovsky_G240_CONUS_East.nc, ${maskpath}/Bukovsky_G240_CONUS_West.nc, ${maskpath}/Bukovsky_G240_CONUS_South.nc, ${maskpath}/Bukovsky_G240_CONUS_Central.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSmean_obsCCPA_G240.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  else
                     echo  "export verif_poly='${maskpath}/Alaska_G216.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                     echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSmean_obsMRMS_G216.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	             echo  "export verif_poly='${maskpath}/Alaska_G091.nc' " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
 	             echo  "${METPLUS_PATH}/ush/run_metplus.py -c  ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/GridStat_fcstREFSmean_obsMRMS_G91.conf " >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
                  fi

               fi
               if [ $prod = system ] ; then
                  echo "for FILEn in \$output_base/stat/${MODEL}/ensemble_stat_${MODEL}_*_${obsv}_FHR0${fhr}_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/${MODEL}; fi; done" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               else    
                  echo "for FILEn in \$output_base/stat/${MODEL}/grid_stat_${MODEL}_${obsv}_*_${fhr}0000L_${VDATE}_${vhr}0000V.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall/${MODEL}; fi; done" >> run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               fi

               chmod +x run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh
               echo "${DATA}/run_refs_precip_${prod}.${obsv}.f${fhr}.v${vhr}.sh" >> run_all_refs_precip_poe.sh

            done #end of vhr
            
         done #end of fhr

      done #end of prod

   done  #end of obsv

done # end of domain 
export err=$?; err_chk
