#!/bin/ksh

# Script: evs_global_ens_snow_ice.sh
# Purpose: run Global ensembles (GEFS, CMCE, EC and NAES)  snow and sea ice verification for upper fields 
#            end 24hr APCP by setting several METPlus environment variables and running METplus conf files 
# Input parameters:
#   (1) model_list: either gefs or cmce or ecme or naefs or all
#   (2) verify_list: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into  procedure files           
#   (3) Put all MPI procedure files into one MPI script file run_all_gens_sea_ice_poe.sh
#   (4) If $run_mpi is yes, run the MPI script  in paraalel
#        otherwise run the MPI script in sequence
# Note: total number of parallels = grid2grid (models x validhours) + precip (models)
#   The maximum (4 models) = 4 + 2 + 2 + 2 + 4 = 14,  in this case 14 nodes should be set in its ecf,   
#
# Author: Binbin Zhou, IMSG
# Update log: 2/4/2022, beginning version  
#

set -x

modnam=$1
verify=$2

###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh osi_saf
export err=$?; err_chk
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam
export err=$?; err_chk

MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`
if [ $modnam = gefs ] ; then
  mbrs=30
elif [ $modnam = cmce ] ; then
  mbrs=20
elif [ $modnam = ecme ] ; then
  mbrs=50
else
  err_exit "wrong model: $modnam"
fi

tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

anl=osi_saf
export vhour='00'
for metplus_job in GenEnsProd EnsembleStat GridStat; do
    >run_all_gens_sea_ice_${metplus_job}_poe.sh
    for average in 24 ; do
        past=`$NDATE -$average ${vday}01`
        export vday1=${past:0:8}
        export period=multi.${vday1}00to${vday}00_G004
        if [ $average = 24 ] ; then
            leads_chk="024 048 072 096 120 144 168 192 216 240 264 288 312 336 360 384"
        elif [ $average = 168 ] ; then
            leads_chk="168 192 216 240 264 288 312 336 360 384"
        fi
        >run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export average=$average" >>  run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export period=$period"  >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export output_base=${WORK}/${verify}/run_${modnam}_valid_at_t${vhour}z_${verify}_${average}" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export OBTYPE=OSI_SAF" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export obsvhead=$anl" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export obsvgrid=$period" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export obsvpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export modelgrid=grid3.icec_${average}h.f" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export vbeg=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export vend=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export modeltail='.nc'" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        typeset -a lead_arr
        for lead_chk in $leads_chk; do
            fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
            fyyyymmdd=${fcst_time:0:8}
            ihour=${fcst_time:8:2}
            if [ $metplus_job = GenEnsProd ]|| [ $metplus_job = EnsembleStat ] ; then
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.icec_${average}h.f${lead_chk}.nc
                nmbrs_lead_check=$(find $chk_path -size +0c 2>/dev/null | wc -l)
                if [ $nmbrs_lead_check -eq $mbrs ]; then
                   lead_arr[${#lead_arr[*]}+1]=${lead_chk}
                fi
            elif [ $metplus_job = GridStat ] ; then
                chk_file=${WORK}/${verify}/run_${modnam}_valid_at_t${vhour}z_${verify}_${average}/stat/$modnam/GenEnsProd_${MODL}_ICEC${average}h_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
                if [ -s $chk_file ]; then
                    lead_arr[${#lead_arr[*]}+1]=${lead_chk}
                fi
            fi
        done
        lead_str=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        unset lead_arr
        echo  "export lead='${lead_str}' "  >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        if [ $metplus_job = GridStat ] ; then
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${MODL}_obsOSI_SAF_mean.conf " >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        else
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${MODL}_obsOSI_SAF.conf " >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        fi
        if [ $metplus_job = EnsembleStat ]; then
          [[ $SENDCOM="YES" ]] && echo "cpreq -v \$output_base/stat/${modnam}/ensemble_stat_*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        elif [ $metplus_job = GridStat ]; then
          [[ $SENDCOM="YES" ]] && echo "cpreq -v \$output_base/stat/${modnam}/grid_stat_*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        fi
        chmod +x run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh
        echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${verify}_${average}_${metplus_job}.sh" >> run_all_gens_sea_ice_${metplus_job}_poe.sh
        chmod 775 run_all_gens_sea_ice_${metplus_job}_poe.sh
        if [ -s run_all_gens_sea_ice_${metplus_job}_poe.sh ] ; then
            ${DATA}/run_all_gens_sea_ice_${metplus_job}_poe.sh
            export err=$?; err_chk
        fi 
    done
done

if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 00 00
  export err=$?; err_chk
fi
