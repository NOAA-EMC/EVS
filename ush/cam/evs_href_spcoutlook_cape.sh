#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


############################################################

cd $SPCoutlookMask

files=`ls *_00Z.nc`
set -A file $files
len=${#file[@]}

verif_poly_00Z=$SPCoutlookMask/${file[0]}

for (( i=1; i<$len; i++ )); do
  mask="${file[$i]}"
  export verif_poly_00Z="$verif_poly_00Z, $SPCoutlookMask/${mask}"
done


files=`ls *_12Z.nc`
set -A file $files
len=${#file[@]}

verif_poly_12Z=$SPCoutlookMask/${file[0]}
for (( i=1; i<$len; i++ )); do
  mask="${file[$i]}"
  export verif_poly_12Z="$verif_poly_12Z, $SPCoutlookMask/${mask}"
done

cd $WORK

>run_all_href_spcoutlook_poe.sh

obsv='prepbufr'

for prod in mean ; do

 PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

 model=HREF${prod}

 for dom in CONUS ; do

   for valid in 0 12 ; do

    export domain=$dom

     >run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid}_spcoutlook.sh     
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid}_spcoutlook" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export domain=CONUS" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export obsvgrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export modelgrid=conus.${prod}" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export vbeg=$valid" >>run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export vend=$valid" >>run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export lead='6,12,18,24,30,36,42,48'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       if [ $valid = 0 ] ; then
         echo "export verif_poly='$verif_poly_00Z'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       elif [ $valid = 12 ] ; then 
	 echo "export verif_poly='$verif_poly_12Z'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       fi

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SPCoutlook.conf " >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       #echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SFC.conf " >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       chmod +x run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo "run_href_${model}.${dom}.${valid}_spcoutlook.sh" >> run_all_href_spcoutlook_poe.sh

    done # end of valid

  done #end of dom loop

done #end of prod loop

chmod 775 run_all_href_spcoutlook_poe.sh
