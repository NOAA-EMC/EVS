#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 

modnam=$1
verify=$2

###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE

#Check input if obs and fcst input data files availabble 
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh prepbufr
export err=$?; err_chk
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $models
export err=$?; err_chk

MODNAM=`echo $modnam | tr '[a-z]' '[A-Z]'`
if [ $modnam = gefs ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
     validhours="00 06 12 18"
     fhrs="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084"
elif [ $modnam = cmce ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20'
     validhours="00 12"
     fhrs="012 024 036 048 060 072 084"
elif [ $modnam = ecme ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50'
     validhours="00 12"
     fhrs="012 024 036 048 060 072 084"
else
     err_exit "wrong model: $modnam"
fi

tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

>run_all_gens_cnv_poe.sh
for vhour in $validhours; do
  for fhr in $fhrs ; do
    fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
    fyyyymmdd=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    >run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export output_base=$WORK/grid2obs/run_${modnam}_t${vhour}z_${fhr}_cnv" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export modelpath=$COM_IN" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrhead=gfs" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrgrid=prepbufr.f00.nc" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrpath=$COM_IN" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export model=$modnam"  >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export MODEL=$MODNAM" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export vbeg=$vhour" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export vend=$vhour" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export valid_increment=21600" >>  run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export lead=$fhr " >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export modelhead=$modnam" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    if [ $modnam = ecme ] ; then
      echo  "export modeltail='.grib1'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
      echo  "export modelgrid=grid4.f" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    else
      echo  "export modeltail='.grib2'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
      echo  "export modelgrid=grid3.f" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    fi
    echo  "export extradir='atmos/'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    export mbr
    for mbr in $mbrs ; do
      if [ $modnam = ecme ] ; then
        chk_file=$COM_IN/tmos.${fyyyymmdd}/$modnam/$modnam.ens${mbr}.t${ihour}z.grid4.f${fhr}.grib1
      else
        chk_file=$COM_IN/tmos.${fyyyymmdd}/$modnam/$modnam.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2
      fi
      if [ -s $chk_file ]; then
        echo "export mbr=$mbr" >>  run_${modnam}_t${vhour}z_${fhr}_cnv.sh
        echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_CNV.conf">> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
        echo "export err=\$?; err_chk" >>  run_${modnam}_t${vhour}z_${fhr}_cnv.sh
      fi
    done
    echo "cd \$output_base/stat/${modnam}" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo "$USHevs/global_ens/evs_global_ens_average_cnv.sh $modnam $fhr" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo "export err=\$?; err_chk" >>  run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    [[ $SENDCOM="YES" ]] && echo  "cpreq -v  \$output_base/stat/${modnam}/*PREPBUFR_CONUS*.stat $COMOUTsmall" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    chmod +x run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo "${DATA}/run_${modnam}_t${vhour}z_${fhr}_cnv.sh" >> run_all_gens_cnv_poe.sh
 done # end of fhrs
done # end of validhours

chmod 775 run_all_gens_cnv_poe.sh
if [ $run_mpi = yes ] ; then
  mpiexec -n 14 -ppn 14 --cpu-bind verbose,depth cfp ${DATA}/run_all_gens_cnv_poe.sh
  export err=$?; err_chk
else
    ${DATA}/run_all_gens_cnv_poe.sh
    export err=$?; err_chk
fi

if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME cnv 00 18
  export err=$?; err_chk
fi
