#!/bin/ksh

# Author: Binbin Zhou, Lynker
# Update log: 10/24/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################

>run_all_gens_sst24h_poe.sh

modnam=$1
verify=$2

tail='/atmos'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh ghrsst
anl=ghrsst
export cyc='00'


if [ $verify = sst24h ] ; then 

      MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

      if [ $modnam = gefs ] ; then
        mbrs=30
      elif [ $modnam = cmce ] ; then
        mbrs=20
      elif [ $modnam = ecme ] ; then
        mbrs=50
      else
        echo "wrong model: $modnam"
      fi 
        
        >run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo  "export output_base=${WORK}/${verify}/run_${modnam}_valid_at_t${cyc}z_${verify}" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo  "export OBTYPE=GHRSST" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo  "export obsvhead=$anl" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export obsvpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
     
	if  [ ${modnam} = ecme ] ; then 
          echo  "export modelgrid=grid4.sst24h.f" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
	else
	  echo  "export modelgrid=grid3.sst24h.f" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
	fi

        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export vend=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${cyc}z_${verify}.sh


        echo  "export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo  "export modeltail='.nc'" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh


        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcst${MODL}_obsGHRSST.conf " >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        chmod +x run_${modnam}_valid_at_t${cyc}z_${verify}.sh

        echo "${DATA}/run_${modnam}_valid_at_t${cyc}z_${verify}.sh" >> run_all_gens_sst24h_poe.sh

   chmod 775 run_all_gens_sst24h_poe.sh

   
fi   




if [ -s run_all_gens_sst24h_poe.sh ] ; then
    ${DATA}/run_all_gens_sst24h_poe.sh	 
fi


if [ $gather = yes ] ; then

  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 00 00 

fi
 
 
