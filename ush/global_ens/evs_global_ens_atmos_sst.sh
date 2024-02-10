#!/bin/ksh
#*************************************************************************************************
# Purpose: run Global ensemble SST verification by METPlus
# Input parameters:
#   (1) modnam: ensemble system names
#   (2) verify: verifican case (sst)
# Execution steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into sub-task files
#   (3) Put all sub-task script files into one poe script file 
#   (4) If $run_mpi is yes, run the poe script  in paraalel
#        otherwise run the poe script in sequence
# Note on METplus verification:
#   (1) For EnsembleStat, the input forecast files are ensemble member files from EVS prep directory
#       
# Last update: 11/16/2023, by Binbin Zhou (Lynker@NCPE/EMC)
#              11/12/2023  by Mallory Row (SAIC@NCEP/EMC)
#       
#********************************************************************************************************
#

set -x

modnam=$1
verify=$2

###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

#********************************************************
#Check input if obs and fcst input data files availabble
#*******************************************************
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

#*************************
#Get sub-string of $EVSIN
#*************************
tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN


anl=ghrsst
export vhour='00'
#****************************************
#Build a poe script to collect sub-tasks
#****************************************
>run_all_gens_sst24h_poe.sh

#****************************
# Build sub-task scripts
#****************************
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
if [ $SENDCOM="YES" ] ; then
    echo "for FILE in \$output_base/stat/${modnam}/ensemble_stat_*.stat ; do" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
    echo "  if [ -s \$FILE ]; then" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
    echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
    echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
    echo "done" >> run_${modnam}_valid_at_t${vhour}z_${verify}.sh
fi 
chmod +x run_${modnam}_valid_at_t${vhour}z_${verify}.sh
echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${verify}.sh" >> run_all_gens_sst24h_poe.sh

#********************************
#Run poe script in sequence
#********************************
chmod 775 run_all_gens_sst24h_poe.sh
if [ -s run_all_gens_sst24h_poe.sh ] ; then
    ${DATA}/run_all_gens_sst24h_poe.sh	
    export err=$?; err_chk 
fi

#*******************************************************
# Collect small stat files to form a final big stst file
#*******************************************************
if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 00 00 
  export err=$?; err_chk
fi
