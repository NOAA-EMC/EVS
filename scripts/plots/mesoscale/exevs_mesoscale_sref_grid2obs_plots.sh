#!/bin/ksh
#*************************************************************************************
# Purpose: setup environment, paths, and run the sref grid2obs plotting python script
# Last updated:
#               04/10/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               10/27/2023, Add comments,           Binbin Zhou Lynker@EMC/NCEP
#
# ************************************************************************************
set -x 

export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs

restart=$COMOUTplots/restart/$past_days/sref_grid2obs_plots
if [ ! -d  $restart ] ; then
  mkdir -p $restart
fi

export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='GEFS SREF'
          
models='GEFS, SREF'

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day


#*************************************************************************
# Virtual link the  sref's stat data files of past 90 days
#**************************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/mesoscale/evs_get_sref_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="CONUS"
																  
export fcst_init_hour="0,3,6,9,12,15,18,21"
export fcst_valid_hours="0 6 12 18"
#valid_time='valid00z_06z_12z_18z'
init_time='init00_to_21z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
if [ ! -d $plot_dir ] ; then
 mkdir -p $plot_dir
fi

verif_case=$VERIF_CASE
#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

for fcst_valid_hour in $fcst_valid_hours ; do
 vld=$fcst_valid_hour
 typeset -Z2 vld
 
  

 for stats in  crps rmse_spread me ets_fbias; do 
  if [ $stats = crps ] ; then
   stat_list='crps'
   line_tp='ecnt'
   score_types='lead_average'
   VARs='HGT TMP UGRD VGRD PRMSL TMP2m RH2m DPT2m UGRD10m VGRD10m'
  elif [ $stats = rmse_spread  ] ; then
   stat_list='rmse, spread'
   line_tp='ecnt'
   VARs='HGT TMP UGRD VGRD PRMSL TMP2m RH2m DPT2m UGRD10m VGRD10m'
   score_types='lead_average'
  elif [ $stats = me ] ; then
   stat_list='me'
   line_tp='ecnt'
   VARs='HGT TMP UGRD VGRD PRMSL TMP2m RH2m DPT2m UGRD10m VGRD10m'
   score_types='lead_average'
  elif [ $stats = ets_fbias ] ; then
   stat_list='ets, fbias'
   line_tp='ctc'
   VARs='CAPEsfc DPT2m TCDC'
   score_types='lead_average threshold_average'
  else
   err_exit "$stats is wrong stat"
  fi   

  for score_type in $score_types ; do

   export fcst_leads="vs_lead" 
 
   for lead in $fcst_leads ; do 

    export fcst_lead=" 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87"

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = TMP2m ] || [ $VAR = DPT2m ] || [ $VAR = RH2m ] ; then 
          FCST_LEVEL_values="Z2"
       elif [ $VAR = UGRD10m ] || [ $VAR = VGRD10m ] ; then
          FCST_LEVEL_values="Z10"
       elif [ $VAR = PRMSL ] || [ $VAR = CAPEsfc ] || [ $VAR = TCDC ] ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
	  FCST_LEVEL_values="P850 P500 P250"
       elif [ $VAR = TMP ] ; then
	  FCST_LEVEL_values="P850 P500"
       elif [ $VAR = HGT ] ; then
	  FCST_LEVEL_values="P500 P700"
       fi
      
     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

       if [ $VAR = TMP2m ] ; then
          level_var=2m_tmp
       elif [ $VAR = DPT2m ] ; then
          level_var=2m_dpt
       elif [ $VAR = RH2m ] ; then
          level_var=2m_rh
       elif [ $VAR = UGRD10m ] ; then 
          level_var=10m_ugrd
       elif [ $VAR = VGRD10m ] ; then
          level_var=10m_vgrd
       elif [ $VAR = PRMSL ] ; then
          level_var=prmsl
       elif [ $VAR = CAPEsfc ] ; then 
          level_var=cape
       elif [ $VAR = TCDC ] ; then
          level_var=tcdc
       elif [ $VAR = UGRD ] ; then
          if [ $FCST_LEVEL_value = P850 ] ; then
	    level_var=850mb_ugrd
	  elif [ $FCST_LEVEL_value = P500 ] ; then
            level_var=500mb_ugrd
          elif [ $FCST_LEVEL_value = P250 ] ; then
	    level_var=250mb_ugrd  
          fi
       elif [ $VAR = VGRD ] ; then
	  if [ $FCST_LEVEL_value = P850 ] ; then
	    level_var=850mb_vgrd
	  elif [ $FCST_LEVEL_value = P500 ] ; then
	    level_var=500mb_vgrd
	  elif [ $FCST_LEVEL_value = P250 ] ; then
	    level_var=250mb_vgrd          
          fi
       elif [ $VAR = TMP ] ; then
          if [ $FCST_LEVEL_value = P850 ] ; then
            level_var=850mb_tmp
	  elif [ $FCST_LEVEL_value = P500 ] ; then
            level_var=500mb_tmp
	  fi
	elif [ $VAR = HGT ] ; then
          if [ $FCST_LEVEL_value = P700 ] ; then
            level_var=700mb_hgt
	  elif [ $FCST_LEVEL_value = P500 ] ; then
            level_var=500mb_hgt
          fi
	fi

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

	 #*********************
	 # Build sub-jobs
	 #*********************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh  

	#*******************************************************************************************************************
	#  Check if this sub-job has been completed in the previous run for restart
	 if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.completed ] ; then
	#******************************************************************************************************************* 
   	 
	if [ $VAR = UGRD ] || [ $VAR = VGRD ] || [ $VAR = HGT ] || [ $VAR = TMP ] ; then
	   verif_type=upper_air
        else	   
           verif_type=conus_sfc
        fi

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

	 if [ $VAR = CAPEsfc ] && [ $line_type = ctc ] ; then
          thresh_fcst='>=250, >=500, >=1000, >=2000'
          thresh_obs='>=250, >=500, >=1000, >=2000'
	 elif [ $VAR = DPT2m ] && [ $line_type = ctc ] ; then  
          thresh_fcst='>=277.59, >=283.15, >=288.71, >=294.26'
          thresh_obs='>=277.59, >=283.15, >=288.71, >=294.26'
	 elif [ $VAR = TCDC ] && [ $line_type = ctc ] ; then
	  thresh_fcst='>=10, >=20, >=30, >=40, >=50, >=60, >=70, >=80, >=90'
	  thresh_obs='>=10, >=20, >=30, >=40, >=50, >=60, >=70, >=80, >=90'
	 else
          thresh_fcst=' '
	  thresh_obs=' '
         fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/mesoscale/evs_sref_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

	 #Save for restart:
         echo "cp ${plot_dir}/${score_type}_regional_conus_valid_${vld}z*.png $restart/." >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
	 echo "[[ $? = 0 ]] && >$restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh" >> run_all_poe.sh


       else

	 #For restart
	 cp $restart/${score_type}_regional_conus_valid_${vld}z*.png  ${plot_dir}/.	 
      
       fi	 
      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #end of fcst_valid_hours

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
# **************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 216 -ppn 72 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
   export err=$?; err_chk
else
   ${DATA}/run_all_poe.sh
   export err=$?; err_chk
fi


#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for valid in 00z 06z 12z 18z ; do 

for var in hgt tmp ugrd vgrd prmsl rh dpt tcdc cape ; do
  if [ $var = hgt ] ; then
    levels='500 700'
    stats='crps rmse_spread me'
    score_types='lead_average'
  elif [ $var = ugrd ] || [ $var = vgrd ] ; then
    levels='10 250 500 850'
    stats='crps rmse_spread me'
    score_types='lead_average'
  elif [ $var = tmp ] ; then
    levels='2 500 850'
    stats='crps rmse_spread me'
    score_types='lead_average'
  elif [ $var = rh ] ; then
    levels=2
    stats='crps rmse_spread me'
    score_types='lead_average'
  elif [ $var = dpt ] ; then
    levels=2
    stats='crps rmse_spread me ets_fbias ets fbias'
    score_types='lead_average threshold_average'
  elif [ $var = cape ] || [ $var = tcdc ] ; then
    levels=L0
    stats='ets_fbias ets fbias'
    score_types='lead_average threshold_average'
  elif [ $var = prmsl ] ; then
    levels=L0
    stats='crps rmse_spread me'
    score_types='lead_average'
  fi

  for level in $levels ; do 
    if [ $level = 500 ] || [ $level = 700 ] || [ $level = 850 ] || [ $level = 250 ] ; then
	unit=mb
	var_level=${var}_p${level}
    elif [ $level = 2 ] || [ $level = 10 ] ; then
	unit=m
	var_level=${var}_${level}m
    elif [ $level = L0 ] ; then
	unit='non'
	var_level=${var}_l0
    fi

   for stat in $stats ; do
    for score_type in $score_types ; do
      if [ $score_type = lead_average ] ; then
	 scoretype=fhrmean
	 if [ $stat = ets_fbias ] ; then
	    if [ $var = dpt ] ; then
	       end='_ge277.59ge283.15ge288.71ge294.26.png'
	    elif [ $var = cape ] ; then
	       end='_ge250ge500ge1000ge2000.png'
	    elif [ $var = tcdc ] ; then
	       end='_ge10ge20ge30ge40ge50ge60ge70ge80ge90.png'
	    fi
	 else
	   end='.png'
	 fi

      
         if [ $unit = mb ] || [ $unit = m ] ; then
	   if [ -s ${score_type}_regional_conus_valid_${valid}_${level}${unit}_${var}_${stat}${end} ] ; then 
             mv ${score_type}_regional_conus_valid_${valid}_${level}${unit}_${var}_${stat}${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
	   fi
         else
           if [ -s ${score_type}_regional_conus_valid_${valid}_${var}_${stat}${end} ] ; then
             mv ${score_type}_regional_conus_valid_${valid}_${var}_${stat}${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
	   fi 
         fi
               
      else

         scoretype=threshmean
         if [ $stat = ets ] || [ $stat = fbias ] ; then
	   end='f6_to_f87.png'

           if [ $unit = m ] ; then
	    if [ -s ${score_type}_regional_conus_valid_${valid}_${level}${unit}_${var}_${stat}_${end} ] ; then	   
	      mv ${score_type}_regional_conus_valid_${valid}_${level}${unit}_${var}_${stat}_${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
	    fi
	   else
	    if [ -s ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${end} ]; then
              mv ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
	    fi
           fi
         fi
      fi	 

      done #score_type
    done #var
   done  #stat
done     #vars
done     #valid

tar -cvf evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar *.png


if [ $SENDCOM = YES ] && [ -s evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar  $COMOUTplots/.  
fi

if [ $SENDDBN = YES ] ; then
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar
fi







