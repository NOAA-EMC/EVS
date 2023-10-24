#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'
############################################################


model_list=$1

models=$model_list

#Check input if obs and fcst input data files availabble 
#echo EVSIN=$EVSIN 
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh prepbufr
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $models

>run_all_gens_cnv_poe.sh

tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN



for modnam in $models ; do

   export model=$modnam
   MODNAM=`echo $model | tr '[a-z]' '[A-Z]'`
   if [ $modnam = gefs ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
     vbeg=00
     vend=18
     valid_increment=21600
     fhrs="0 6 12 18 24 30 36 42 48 54 60 66 72 78 84" 
   elif [ $modnam = cmce ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20'
     vbeg=00
     vend=12
     valid_increment=43200
     hrs="12 24 36 48 60 72 84"
   elif [ $modnam = ecme ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50'
     vbeg=00
     vend=12
     valid_increment=43200
   else
     echo "wrong model"
   fi


for fhr in $fhrs ; do

  >run_${modnam}_${fhr}_cnv.sh

    echo  "export output_base=$WORK/grid2obs/run_${modnam}_${fhr}_cnv" >> run_${modnam}_${fhr}_cnv.sh

    echo  "export modelpath=$COM_IN" >> run_${modnam}_${fhr}_cnv.sh


    echo  "export prepbufrhead=gfs" >> run_${modnam}_${fhr}_cnv.sh
    echo  "export prepbufrgrid=prepbufr.f00.nc" >> run_${modnam}_${fhr}_cnv.sh
    echo  "export prepbufrpath=$COM_IN" >> run_${modnam}_${fhr}_cnv.sh
    echo  "export model=$modnam"  >> run_${modnam}_${fhr}_cnv.sh
    echo  "export MODEL=$MODNAM" >> run_${modnam}_${fhr}_cnv.sh
 
    echo  "export vbeg=$vbeg" >> run_${modnam}_${fhr}_cnv.sh
    echo  "export vend=$vend" >> run_${modnam}_${fhr}_cnv.sh
    echo  "export valid_increment=$valid_increment" >>  run_${modnam}_${fhr}_cnv.sh


    echo  "export lead=$fhr " >> run_${modnam}_${fhr}_cnv.sh
 
    echo  "export modelhead=$modnam" >> run_${modnam}_${fhr}_cnv.sh

    if [ $modnam = ecme ] ; then
     echo  "export modeltail='.grib1'" >> run_${modnam}_${fhr}_cnv.sh
     echo  "export modelgrid=grid4.f" >> run_${modnam}_${fhr}_cnv.sh
    else
     echo  "export modeltail='.grib2'" >> run_${modnam}_${fhr}_cnv.sh
     echo  "export modelgrid=grid3.f" >> run_${modnam}_${fhr}_cnv.sh
    fi 
    echo  "export extradir='atmos/'" >> run_${modnam}_${fhr}_cnv.sh

    #echo  "export members=$mbrs" >> run_${modnam}_${fhr}_cnv.sh


    export mbr
     for mbr in $mbrs ; do
       echo "export mbr=$mbr" >>  run_${modnam}_${fhr}_cnv.sh
       echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_CNV.conf">> run_${modnam}_${fhr}_cnv.sh
    done

    echo "cd \$output_base/stat/${modnam}" >> run_${modnam}_${fhr}_cnv.sh
    echo "$USHevs/global_ens/evs_global_ens_average_cnv.sh $modnam $fhr" >> run_${modnam}_${fhr}_cnv.sh

    [[ $SENDCOM="YES" ]] && echo  "cp \$output_base/stat/${modnam}/*PREPBUFR_CONUS*.stat $COMOUTsmall" >> run_${modnam}_${fhr}_cnv.sh 

    chmod +x run_${modnam}_${fhr}_cnv.sh

    echo "${DATA}/run_${modnam}_${fhr}_cnv.sh" >> run_all_gens_cnv_poe.sh 

  done # end of fhr 
done #end of model

chmod 775 run_all_gens_cnv_poe.sh

if [ $run_mpi = yes ] ; then
  mpiexec -n 14 -ppn 14 --cpu-bind verbose,depth cfp ${DATA}/run_all_gens_cnv_poe.sh

else
    ${DATA}/run_all_gens_cnv_poe.sh
fi 

if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME cnv 00 18
fi



