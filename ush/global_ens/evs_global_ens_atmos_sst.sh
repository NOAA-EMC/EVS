#!/bin/ksh

# Author: Binbin Zhou, Lynker
# Update log: 10/24/2022, beginning version  
#

set -x

modnam=$1
verify=$2

###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam
export err=$?; err_chk
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh ghrsst
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

anl=ghrsst
export vhour='00'

>run_all_gens_sst24h_poe.sh

>run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export output_base=${WORK}/${verify}/run_${modnam}_valid_at_t${vhour}z_${verify}" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export OBTYPE=GHRSST" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export obsvhead=$anl" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export obsvpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
if  [ ${modnam} = ecme ] ; then 
  echo  "export modelgrid=grid4.sst24h.f" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
else
  echo  "export modelgrid=grid3.sst24h.f" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
fi
echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export vbeg=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export vend=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export modeltail='.nc'" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
typeset -a lead_arr
for lead_chk in $leads_chk; do
  fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
  fyyyymmdd=${fcst_time:0:8}
  ihour=${fcst_time:8:2}
  chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.sst24h.f${lead_chk}.nc
  nmbrs_lead_check=$(find $chk_path -size +0c 2>/dev/null | wc -l)
  if [ $nmbrs_lead_check -eq $mbrs ]; then
      lead_arr[${#lead_arr[*]}+1]=${lead_chk}
  fi
done
lead_str=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
unset lead_arr
echo  "export lead='${lead_str}' "  >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcst${MODL}_obsGHRSST.conf " >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh 
[[ $SENDCOM="YES" ]] && echo "cpreq -v  \$output_base/stat/${modnam}/ensemble_stat_*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
chmod +x run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${verify}.sh" >> run_all_gens_sst24h_poe.sh

chmod 775 run_all_gens_sst24h_poe.sh
if [ -s run_all_gens_sst24h_poe.sh ] ; then
    ${DATA}/run_all_gens_sst24h_poe.sh	
    export err=$?; err_chk 
fi

if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 00 00 
  export err=$?; err_chk
fi
