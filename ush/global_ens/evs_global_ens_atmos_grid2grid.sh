#!/bin/ksh

# Script: evs_global_ens_grid2grid.sh
# Purpose: run Global ensembles (GEFS, CMCE, EC and NAES)  grid2grid verification for upper fields 
#            end 24hr APCP by setting several METPlus environment variables and running METplus conf files 
# Input parameters:
#   (1) model_list: either gefs or cmce or ecme or naefs or all
#   (2) verify_list: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into  procedure files           
#   (3) Put all MPI procedure files into one MPI script file run_all_gens_g2g_poe.sh
#   (4) If $run_mpi is yes, run the MPI script  in paraalel
#        otherwise run the MPI script in sequence
# Note: total number of parallels = grid2grid (models x cycles) + precip (models)
#   The maximum (4 models) = 4 + 2 + 2 + 2 + 4 = 14,  in this case 14 nodes should be set in its ecf,   
#
# Author: Binbin Zhou, IMSG
# Update log: 2/4/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################

>run_all_gens_g2g_poe.sh

model_list=$1
verify_list=$2

#Check input if obs and fcst input data files availabble
if [ $model_list = gefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gfsanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gefs
elif  [ $model_list = cmce ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmcanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmce
elif  [ $model_list = ecme ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh ecmanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh ecme
elif  [ $model_list = naefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gfsanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmcanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gefs_bc
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmce_bc
fi



tail='/atmos'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN


models=$model_list

if [ $verify_list = all ] ; then
  verifys="upper precip" 
else
  verifys=$verify_list
fi 

for  verify in $verifys ; do  

 if [ $verify = upper ] ; then 

    for modnam in $models ; do 

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
        anl=gfsanl
	if [ $gefs_number = 20 ] ; then
            mbrs=40
	elif [ $gefs_number = 30 ] ; then
            mbrs=50
	fi
      else
        echo "wrong model: $modnam"
      fi 

      if [ $modnam = gefs ] ; then
        cycs="00 06 12 18"
      else
        cycs="00 12"
      fi

      for cyc in ${cycs} ; do

       for fhr in fhr1 ; do

        >run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

            echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${cyc}z_${fhr}" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        if [ $modnam = naefs ] ; then
          echo  "export modelpath=${WORK}/naefs" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        else
          echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        fi

        echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdasgrid=grid3" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
     
	if [ ${modnam} = ecme ] ; then
		echo  "export modelgrid=grid4.f" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
	else	
                echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
	fi

        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export vend=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        if [ $modnam = gefs ] ; then
          echo  "export lead='0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72,78, 84,90, 96,102, 108,114, 120,126, 132,138, 144,150, 156,162, 168,174, 180,186, 192,198,204,210, 216,222, 228,234, 240,246, 252,258, 264,270, 276,282, 288,294, 300,306, 312,318, 324,330, 336,342, 348,354, 360,366, 372,378, 384'  " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

         elif [ $modnam = cmce ] || [ $modnam = naefs ] ; then
	  echo  "export lead='0, 12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
 
         elif [  $modnam = ecme ] ; then
          echo  "export lead='0, 12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360' "  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        fi

        if [ $modnam = ecme ] ; then
           echo  "export modeltail='.grib1'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        else
           echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        fi
 
        echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        #echo  "export climpath=$CLIMO/era_interim" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh


        if [ $modnam = naefs ] ; then 

          #echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstNAEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstNAEFSbc_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

	  #echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstNAEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstNAEFSbc_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

	  #echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstNAEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstNAEFSbc_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        elif [ $modnam = ecme ] ; then

	 
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstECME_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstECME_obsModelAnalysis_climoERA5_SFC.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstECME_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstECME_obsModelAnalysis_climoERA5_SFC.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsModelAnalysis_climoERA5_mean_SFC.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        elif [ $modnam = gefs ] || [ $modnam = cmce ] ; then

          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        else

          echo "wrong model"
        exit

        fi

        [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        chmod +x run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo "${DATA}/run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh" >> run_all_gens_g2g_poe.sh


      done #end of fhr 

     done #end of cycle

   done #end if modnam 

   chmod 775 run_all_gens_g2g_poe.sh

 fi #end of if verify=upper  

 if [ $verify = precip ] ; then

   export COMOUTsmall_precip=$COMOUT/$RUN.$VDATE/$MODELNAME/precip
   mkdir -p $COMOUTsmall_precip

   for modnam in $models ; do

     export model=$modnam
     MODNAM=`echo $model | tr '[a-z]' '[A-Z]'`
     if [ $modnam = gefs ] ; then
       mbrs=30
     elif [ $modnam = cmce ] ; then
       mbrs=20
     elif [ $modnam = naefs ] ; then
       $USHevs/global_ens/evs_gens_atmos_precip_create_naefs.sh
       if [ $gefs_number = 20 ] ; then
          mbrs=20
       elif [ $gefs_number = 30 ] ; then
	  mbrs=30
       fi
     elif [ $modnam = ecme ] ; then
       mbrs=50
     else
       echo "wrong model"
     fi

    if [ ${modnam} = gefs ] ; then
      apcps="24h 06h"
    else
      apcps="24h"
    fi

    for apcp in $apcps ; do
       if [ $apcp = 24h ] ; then
         cycles='12'
       else
         cycles='00 06 12 18'
       fi
     for cyc in $cycles ; do
     
       >run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       echo  "export output_base=$WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       if [ $modnam = naefs ] ; then
         export modelpath=${WORK}/naefs_precip
         echo  "export modelpath=${WORK}/naefs_precip" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       else
         export modelpath=$COM_IN
         echo  "export modelpath=$COM_IN" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       fi

       if [ $apcp = 24h ] ; then
         echo  "export lead='24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export ccpagrid=grid3.24h.f00.nc" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         if [ ${modnam} = ecme ] ; then
	         echo  "export modelgrid=grid4.24h.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         else
		 echo  "export modelgrid=grid3.24h.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
	 fi

	 if [ $modnam = naefs ] ; then
	    echo  "export modeltail='.grib2'" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
	 else
            echo  "export modeltail='.nc'" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
	 fi

         echo  "export valid_increment=21600" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export climpath_apcp24_prob=$CLIMO/ccpa" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

        elif [ $apcp = 06h ] ; then  
         echo  "export vbeg=$cyc" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export vend=$cyc" >>  run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export valid_increment=21600" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh 
	 echo  "export lead='24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export ccpagrid=grid3.06h.f00.grib2" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
	 echo  "export modelgrid=grid3.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "export modeltail='.grib2'" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       fi

       echo  "export ccpahead=ccpa" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       echo  "export ccpapath=$COM_IN" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       echo  "export model=$modnam"  >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       echo  "export MODEL=$MODNAM" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       echo  "export modelhead=$modnam" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       echo  "export extradir='atmos/'" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       echo  "export members=$mbrs" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       if [ $modnam = ecme ] ; then

	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstECME_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh      
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstECME_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsCCPA${apcp}_climoEMC_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsCCPA${apcp}_mean.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       elif [ $modnam = gefs ] || [ $modnam = cmce ] ; then
	       
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsCCPA${apcp}_mean.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         if [ $apcp = 24h ] ; then
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsCCPA${apcp}_climoEMC_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         elif [ $apcp = 06h ] ; then
           echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsCCPA${apcp}_prob.conf" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         fi

       elif  [ $modnam = naefs ] ; then
	       
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstNAEFS_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstNAEFS_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstNAEFS_obsCCPA${apcp}_climoEMC_prob.conf  " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstNAEFS_obsCCPA${apcp}_mean.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
         
       fi

       [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall_precip" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       if [ $apcp = 24h ] ; then
         mkdir -p $COMOUT/$RUN.$VDATE/apcp24_mean/$MODELNAME
         [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/GenEnsProd*APCP24*.nc  $COMOUT/$RUN.$VDATE/apcp24_mean/$MODELNAME" >> run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh
       fi	

       chmod +x run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh

       echo "${DATA}/run_${modnam}_ccpa${apcp}_valid_at_t${cyc}z.sh" >> run_all_gens_g2g_poe.sh

      done #end of cyc

     done  #end of loop apcp(24h)

   done #end of loop modnam

   chmod 775 run_all_gens_g2g_poe.sh

 fi #end of if verify = precip 

done # end of verify  



if [ -s run_all_gens_g2g_poe.sh ] ; then
 if [ $run_mpi = yes ] ; then

    export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH

    if [ ${models} = gefs ] ; then
      if [ $verify_list = all ] ; then
       ####mpiexec  -n 9 -ppn 9 --cpu-bind core --depth=2 cfp run_all_gens_g2g_poe.sh
         mpiexec -np 9 -ppn 9 --cpu-bind verbose,depth cfp ${DATA}/run_all_gens_g2g_poe.sh 
      elif [ $verify_list = upper ] ; then
        mpiexec  -n 4 -ppn 4 --cpu-bind core --depth=2 cfp ${DATA}/run_all_gens_g2g_poe.sh
      elif [ $verify_list = precip ] ; then
        mpiexec  -n 5 -ppn 5 --cpu-bind core --depth=2 cfp ${DATA}/run_all_gens_g2g_poe.sh
      fi
    else
      if [ $verify_list = all ] ; then
	 mpiexec  -n 3 -ppn 3 --cpu-bind core --depth=2 cfp ${DATA}/run_all_gens_g2g_poe.sh
      elif [ $verify_list = upper ] ; then
	 mpiexec  -n 2 -ppn 2 --cpu-bind core --depth=2 cfp ${DATA}/run_all_gens_g2g_poe.sh
      elif [ $verify_list = precip ] ; then
	 mpiexec  -n 1 -ppn 1 --cpu-bind core --depth=2 cfp ${DATA}/run_all_gens_g2g_poe.sh
      fi
    fi

 else
   ${DATA}/run_all_gens_g2g_poe.sh	 
 fi

fi


if [ $gather = yes ] ; then

  if [ ${models} = gefs ] ; then
    if [ $verify = upper ] ; then
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME  grid2grid 00 18
    elif [ $verify = precip ] ; then      
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME  precip 00 18
    fi
  else
    if [ $verify = upper ] ; then
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 12
    elif [ $verify = precip ] ; then
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME precip 00 12
    fi 
  fi 

fi
 
 
