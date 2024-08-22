#!/bin/ksh
#*************************************************************************
#  Purpose: Generate refs grid2obs ecnt poe and sub-jobs files
#  Last update: 
#               05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
##*************************************************************************
set -x 

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_refs_system_poe.sh

export obsv=prepbufr
export nmbrs=14

for dom in CONUS Alaska ; do

   if [ $dom = CONUS ] ; then

      export domain=CONUS

      for valid_at in 1fhr 2fhr 3fhr 4fhr  5fhr 6fhr 7fhr 8fhr ; do
 
	 #**********************
	 # Build sub-jobs
	 #**********************     
         >run_refs_${domain}.${valid_at}_system.sh

        #########################################################################################
	# Restart: check if this CONUS task has been completed in the precious run 
	#          if not, do this task, and mark it is completed after it is done
	#          otherwise, skip this task 
	#########################################################################################
	if [ ! -e  $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.completed ] ; then
 
	 echo "set -x " >> run_refs_${domain}.${valid_at}_system.sh
         echo "export regrid=G227" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export obsv=prepbufr" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export domain=CONUS" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}_system" >> run_refs_${domain}.${valid_at}_system.sh 

         echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export obsvhead=$obsv" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export obsvgrid=G227" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export vbeg=00" >>run_refs_${domain}.${valid_at}_system.sh
         echo  "export vend=21" >>run_refs_${domain}.${valid_at}_system.sh
         echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}_system.sh

         if [ $valid_at = 1fhr ] ; then 
           echo  "export lead='3,6'" >> run_refs_${domain}.${valid_at}_system.sh
	 elif [ $valid_at = 2fhr ] ; then
	   echo  "export lead='9,12'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 3fhr ] ; then
	   echo  "export lead='15,18'" >> run_refs_${domain}.${valid_at}_system.sh	 
         elif [ $valid_at = 4fhr ] ; then
	   echo  "export lead='21,24'" >> run_refs_${domain}.${valid_at}_system.sh	 
         elif [ $valid_at = 5fhr ] ; then
           echo  "export lead='27,30'" >> run_refs_${domain}.${valid_at}_system.sh
	 elif [ $valid_at = 6fhr ] ; then
           echo  "export lead='33,36'" >> run_refs_${domain}.${valid_at}_system.sh
	 elif [ $valid_at = 7fhr ] ; then
           echo  "export lead='39,42'" >> run_refs_${domain}.${valid_at}_system.sh
	 elif [ $valid_at = 8fhr ] ; then
           echo  "export lead='45,48'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = test ] ; then
           echo  "export vbeg=18" >>run_refs_${domain}.${valid_at}_system.sh
           echo  "export vend=18" >>run_refs_${domain}.${valid_at}_system.sh
           echo  "export lead='12'" >> run_refs_${domain}.${valid_at}_system.sh
         fi

         echo  "export domain=CONUS" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export model=refs"  >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export regrid=G227 " >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}_system.sh
         #echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modelgrid=conus.f" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}_system.sh
 
         echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}_system.sh
        
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
			           ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export valid_at=$valid_at" >> run_refs_${domain}.${valid_at}_system.sh

	 ################################################################################################################
	 # Adding following "if blocks"  for restart capability for CONUS: 
	 #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat 
	 #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
	 #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
	 #            are copied back to the output_base/stat directory
	 #################################################################################################################
	 echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  export modelpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh
         echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_SFC.conf " >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*CONUS*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/system; fi; done" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  [[ \$? = 0 ]] &&  >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "else " >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}_system.sh
	 echo " cp $COMOUTrestart/system/GenEnsProd*CONUS*.nc \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}_system.sh
         echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

	 echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  export modelpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_SFC.conf " >> run_refs_${domain}.${valid_at}_system.sh
         echo "  >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

	 echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}_system.sh
	 echo " ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_SFC_prob.conf " >> run_refs_${domain}.${valid_at}_system.sh
         echo " >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.PointStat.completed" >> run_refs_${domain}.${valid_at}_system.sh
         echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

	 echo "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done"  >> run_refs_${domain}.${valid_at}_system.sh

         #Mark that all of the 3 METplus processes for this task have been  completed for next restart run:
         echo "[[ \$? = 0 ]] && >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.completed" >> run_refs_${domain}.${valid_at}_system.sh

         chmod +x run_refs_${domain}.${valid_at}_system.sh
         echo "${DATA}/run_refs_${domain}.${valid_at}_system.sh" >> run_all_refs_system_poe.sh

       fi #end if check CONUS completed 

      done

    elif [ $dom = Alaska ] ; then

         export domain=Alaska

      for valid_at in 1fhr 2fhr 3fhr 4fhr  5fhr 6fhr 7fhr 8fhr ; do 

         >run_refs_${domain}.${valid_at}_system.sh

       #########################################################################################
       #Restart: check if this Alaska task has been completed in the precious tun
       if [ ! -e  $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.completed ] ; then
       ##########################################################################################
         echo "export regrid=NONE" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export obsv=prepbufr" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export domain=Alaska" >> run_refs_${domain}.${valid_at}_system.sh
         echo "export nmbrs=$nmbrs" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export output_base=$WORK/grid2obs/run_refs_${domain}.${valid_at}_system" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export OBTYPE='PREPBUFR'" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export obsvhead=$obsv " >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export obsvgrid=G198" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export obsvpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export vbeg=00" >>run_refs_${domain}.${valid_at}_system.sh
         echo  "export vend=21" >>run_refs_${domain}.${valid_at}_system.sh
         echo  "export valid_increment=10800" >> run_refs_${domain}.${valid_at}_system.sh

         if [ $valid_at = 1fhr ] ; then 
           echo  "export lead='3,6'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 2fhr ] ; then
           echo  "export lead='9,12'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 3fhr ] ; then
           echo  "export lead='15,18'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 4fhr ] ; then
           echo  "export lead='21,24'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 5fhr ] ; then
           echo  "export lead='27,30'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 6fhr ] ; then
           echo  "export lead='33,36'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 7fhr ] ; then
           echo  "export lead='39,42'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = 8fhr ] ; then
           echo  "export lead='45,48'" >> run_refs_${domain}.${valid_at}_system.sh
         elif [ $valid_at = test ] ; then
           echo  "export vbeg=18" >>run_refs_${domain}.${valid_at}_system.sh
           echo  "export vend=18" >>run_refs_${domain}.${valid_at}_system.sh
           echo  "export lead='12'" >> run_refs_${domain}.${valid_at}_system.sh
         fi

         echo  "export model=refs"  >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export MODEL=REFS" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export regrid=NONE " >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modelhead=refs" >> run_refs_${domain}.${valid_at}_system.sh
         #echo  "export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modelgrid=ak.f" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export modeltail=''" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export extradir='verf_g2g/'" >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export verif_grid=''" >> run_refs_${domain}.${valid_at}_system.sh
         echo  "export verif_poly='${maskpath}/Alaska_HREF.nc'"  >> run_refs_${domain}.${valid_at}_system.sh

         echo  "export valid_at=$valid_at" >> run_refs_${domain}.${valid_at}_system.sh

	 ################################################################################################################
	 # Adding following "if blocks"  for restart capability for Alaska:
	 #  1. check if *.completed files for 3  METplus processes GenEnsProd, EnsembleStat, PointStat
	 #  2. if any of the 3 not exist, then run its METplus, then mark it completed for restart checking next time
	 #  3. if any one of the 3 exits, skip it. But for GenEnsProd, all of the nc files generated from previous run
	 #            are copied back to the output_base/stat directory
	 #################################################################################################################
	 echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.GenEnsProd.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "   export modelpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh
         echo "   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstREFS_obsPREPBUFR_SFC.conf " >> run_refs_${domain}.${valid_at}_system.sh
         echo "  for FILEn in \$output_base/stat/\${MODEL}/GenEnsProd*CONUS*.nc; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTrestart/system; fi; done"  >> run_refs_${domain}.${valid_at}_system.sh
	 echo "   [[ \$? = 0 ]] &&  >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.GenEnsProd.completed" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "else " >> run_refs_${domain}.${valid_at}_system.sh
	 echo "   mkdir -p \$output_base/stat/\${MODEL}" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "   cp $COMOUTrestart/system/GenEnsProd*Alaska*.nc \$output_base/stat/REFS" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

         echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.EnsembleStat.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  export modelpath=$WORK" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstREFS_obsPREPBUFR_SFC.conf " >> run_refs_${domain}.${valid_at}_system.sh
         echo "  >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.EnsembleStat.completed" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

	 echo "if [ ! -e $COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.PointStat.completed ] ; then" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  export modelpath=$COMREFS" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstREFS_obsPREPBUFR_SFC_prob.conf " >> run_refs_${domain}.${valid_at}_system.sh
         echo "  >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.PointStat.completed" >> run_refs_${domain}.${valid_at}_system.sh
	 echo "fi" >> run_refs_${domain}.${valid_at}_system.sh

	 echo "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done"  >> run_refs_${domain}.${valid_at}_system.sh

	 #Mark that all of the 3 METplus processes are completed for next restart run:
	 echo "[[ \$? = 0 ]] && >$COMOUTrestart/system/run_refs_${domain}.${valid_at}_system.completed" >> run_refs_${domain}.${valid_at}_system.sh

         chmod +x run_refs_${domain}.${valid_at}_system.sh
         echo "${DATA}/run_refs_${domain}.${valid_at}_system.sh" >> run_all_refs_system_poe.sh

       fi # end checking if completed

      done

    fi 

done #end of dom

chmod 775 run_all_refs_system_poe.sh
