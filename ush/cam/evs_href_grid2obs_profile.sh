#!/bin/ksh
#*************************************************************************
#  Purpose: Generate href grid2obs profile poe and sub-jobs files
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#*************************************************************************
set -x 

domain=$1

if [ $domain = all ] ; then
  domains="CONUS Alaska HI PR"
else
  domains=$domain
fi

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_href_profile_poe.sh


export obsv=prepbufr

for dom in $domains ; do

   if [ $dom = CONUS ] ; then

       export domain=CONUS

     for valid_at in 00 12 ; do


      for fhr in fhr1 fhr2 ; do

	#****************************
	# Build sub-jobs
	#****************************
        >run_href_${domain}.${valid_at}.${fhr}_profile.sh

       
       echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh 
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvhead=$obsv" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvgrid=G227" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       
       echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh       

       if [ $valid_at = 00 ] || [ $valid_at = 06 ] || [ $valid_at = 12 ] || [ $valid_at = 18 ] ; then

         if [ $fhr = fhr1 ] ; then
           echo  "export lead=' 6,12,18,24'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
         elif [ $fhr = fhr2 ] ; then
           echo  "export lead='30,36,42,48'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
         fi 
       fi
        
       echo  "export domain=CONUS" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modelgrid=conus.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
 
       echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

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
                                   ${maskpath}/Bukovsky_G227_SRockies.nc'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh 

	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh 

	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh
	
	echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

       chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
       echo "${DATA}/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

      done

     done

    elif [ $dom = Alaska ] ; then

       export domain=Alaska

      for valid_at in 00 12 ; do 

       for fhr in fhr1 ; do 

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=Alaska" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G198" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export domain=Alaska " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        if [ $valid_at = 00 ] || [ $valid_at = 12 ] ; then
	  #Alaska run cycles are 06Z and 18Z
          echo  "export lead=' 6,18,30,42'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        fi

        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=ak.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Alaska_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       done
      done


    elif [ $dom = HI ] ; then

       export domain=HI

      for valid_at in 00 12 ; do

       for fhr in fhr1 ; do

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=HI" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G139" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        if [ $valid_at = 00 ] || [ $valid_at = 12 ] ; then
          #Hawaii run only has 00Z cycle, and validaded at 00Z and 12Z Raobs (sounding)
          echo  "export lead='12, 24, 36, 48 '" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        fi

        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=hi.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/Hawaii_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       done
      done


    elif [ $dom = PR ] ; then

       export domain=PR

      for valid_at in 00 12 ; do

       for fhr in fhr1 ; do

         >run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo "export regrid=NONE" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export obsv=prepbufr_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "export domain=PR" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh


        echo  "export output_base=$WORK/grid2obs/run_href_${domain}.${valid_at}.${fhr}_profile" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export OBTYPE='PREPBUFR'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "export obsvhead=$obsv " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvgrid=G200" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export obsvpath=$WORK" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export vbeg=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export vend=${valid_at}" >>run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export valid_increment=10800" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
	#Puerto Rico run only has 06Z and 18Z run , and validated at 00Z and 12Z Raobs (sounding)
        if [ $valid_at = 00 ] || [ $valid_at = 12 ] ; then
          echo  "export lead='6, 18, 30, 42'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        fi

        echo  "export model=href"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export MODEL=HREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export regrid=NONE " >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelhead=href" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelpath=$COMHREF" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modelgrid=pr.f" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export modeltail=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export extradir='verf_g2g/'" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "export verif_grid=''" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo  "export verif_poly='${maskpath}/PRico_HREF.nc'"  >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstHREF_obsPREPBUFR_PROFILE.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF_obsPREPBUFR_PROFILE_prob.conf " >>  run_href_${domain}.${valid_at}.${fhr}_profile.sh

	echo  "for FILEn in \$output_base/stat/\${MODEL}/*.stat; do if [ -f \"\$FILEn\" ]; then cp -v \$FILEn $COMOUTsmall; fi; done" >> run_href_${domain}.${valid_at}.${fhr}_profile.sh

	chmod +x run_href_${domain}.${valid_at}.${fhr}_profile.sh
        echo "${DATA}/run_href_${domain}.${valid_at}.${fhr}_profile.sh" >> run_all_href_profile_poe.sh

       done
      done

    fi 

 done #end of dom


chmod 775 run_all_href_profile_poe.sh
