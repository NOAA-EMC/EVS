#!/bin/ksh

# For GEFS Headline grid2grid  
# Author: Binbin Zhou, IMSG
# Update log: 9/4/2022, beginning version  
#

set -x 

modnam=$1
verify_list=$2

###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################
if [ $modnam = gefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gefs
   export err=$?; err_chk
elif  [ $modnam = naefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_cmcanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gefs
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_cmce
   export err=$?; err_chk
elif [ $modnam = gfs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfs
   export err=$?; err_chk
fi

tail='/headline'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`
if [ $modnam = gefs ] ; then
  anl=gfsanl
  mbrs=30
elif [ $modnam = cmce ] ; then
  anl=cmcanl
  mbrs=20
elif [ $modnam = ecme ] ; then
  anl=ecmanl
  mbrs=50
elif [ $modnam = naefs ] ; then
  $USHevs/global_ens/evs_gens_atmos_g2g_reset_naefs.sh
  export err=$?; err_chk
  anl=gfsanl
  if [ $gefs_number = 20 ] ; then
    mbrs=40
  elif [ $gefs_number = 30 ] ; then
    mbrs=50
  fi
elif [ $modnam = gfs ] ; then
  anl=gfsanl
  mbrs=1
else
  err_exit "wrong model: $modnam"
fi

if [ $modnam = naefs ] ; then
    metplus_jobs="GenEnsProd EnsembleStat GridStat"
elif [ $modnam = ecme ] ; then
    metplus_jobs="EnsembleStat GridStat"
elif [ $modnam = gefs ] || [ $modnam = cmce ] ; then
    metplus_jobs="GenEnsProd EnsembleStat GridStat"
elif  [ $modnam = gfs ] ; then
    metplus_jobs="GridStat"
fi

vhours="00"
for vhour in ${vhours} ; do
  for metplus_job in $metplus_jobs; do
    >run_all_gens_g2g_poe_${vhour}_${metplus_job}.sh
    for fhr in fhr1 ; do
      >run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      if [ $modnam = naefs ] ; then
        echo  "export modelpath=${WORK}/naefs" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      else
        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      fi
      echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export gdasgrid=grid3" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      if [ $modnam = ecme ] ; then
         echo  "export modeltail='.grib1'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      else
         echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      fi
      echo  "export vbeg=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export vend=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      typeset -a lead_arr
      for lead_chk in 024 048 072 096 120 144 168 192 216 240 264 288 312 336 360 384; do
          fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
          fyyyymmdd=${fcst_time:0:8}
          ihour=${fcst_time:8:2}
          if [ $metplus_job = GenEnsProd ]|| [ $metplus_job = EnsembleStat ] ; then
            if [ $modnam = naefs ] ; then
                chk_path=${WORK}/naefs/$modnam.ens*.${fyyyymmdd}.t${ihour}z.grid3.f${lead_chk}.grib2
            else
                chk_path=$COM_IN/headline.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.f${lead_chk}.grib2
            fi
            nmbrs_lead_check=$(find $chk_path -size +0c 2>/dev/null | wc -l)
            if [ $nmbrs_lead_check -eq $mbrs ]; then
               lead_arr[${#lead_arr[*]}+1]=${lead_chk}
            fi
          elif [ $metplus_job = GridStat ] ; then
            if  [ $modnam = gfs ] ; then
               chk_file=$COM_IN/headline.${fyyyymmdd}/gefs/gfs.t${ihour}z.grid3.f${lead_chk}.grib2
            else
               chk_file=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam}/GenEnsProd_${MODL}_g2g_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
            fi
            if [ -s $chk_file ]; then
              lead_arr[${#lead_arr[*]}+1]=${lead_chk}
            fi
          fi
      done
      lead_str=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
      unset lead_arr
      echo  "export lead='${lead_str}' "  >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ] ; then
        if  [ $modnam = cmce ] ; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        else
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${MODL}_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        fi
      else
        if  [ $modnam = gfs ] ; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${MODL}_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        elif [ $modnam = cmce ] ; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcstGEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        else
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${MODL}_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        fi
      fi
      if [ $metplus_job = GridStat ]; then
          if [ $SENDCOM="YES" ] ; then
              echo "for FILE in \$output_base/stat/${modnam}/grid_stat*.stat ; do" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "  if [ -s \$FILE ]; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "done" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          fi 
      fi
      chmod +x run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
      echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh" >> run_all_gens_g2g_poe_${vhour}_${metplus_job}.sh
    done #fhr1
    chmod 775 run_all_gens_g2g_poe_${vhour}_${metplus_job}.sh
    ${DATA}/run_all_gens_g2g_poe_${vhour}_${metplus_job}.sh
    export err=$?; err_chk
  done # metplus_jobs
done # vhours

if [ $gather = yes ] ; then
 $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 00
 export err=$?; err_chk
fi
