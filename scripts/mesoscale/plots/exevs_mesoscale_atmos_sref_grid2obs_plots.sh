#!/bin/ksh

set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs


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
export fcst_valid_hour="0,6,12,18"
valid_time='valid00z_06z_12z_18z'
init_time='init00_to_21z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=$VERIF_CASE

> run_all_poe.sh

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
  echo $stats is wrong stat
  exit
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

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

	if [ $VAR = UGRD ] || [ $VAR = VGRD ] || [ $VAR = HGT ] || [ $VAR = TMP ] ; then
	   verif_type=upper_air
        else	   
           verif_type=conus_sfc
        fi

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/mesoscale/evs_sref_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 54 -ppn 54 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
   ${DATA}/run_all_poe.sh
fi


cd $plot_dir

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
	unit=''
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
            mv ${score_type}_regional_conus_valid_00z_06z_12z_18z_${level}${unit}_${var}_${stat}${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_00z_06z_12z_18z.conus_glb.png
         else
           mv ${score_type}_regional_conus_valid_00z_06z_12z_18z_${var}_${stat}${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_00z_06z_12z_18z.conus_glb.png
 
         fi
               
      else

         scoretype=threshmean
         if [ $stat = ets ] || [ $stat = fbias ] ; then
	   end='f6_to_f87.png'

           if [ $unit = m ] ; then
	    	   
	     mv ${score_type}_regional_conus_valid_00z_06z_12z_18z_${level}${unit}_${var}_${stat}_${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_00z_06z_12z_18z.conus_glb.png
	   else
             mv ${score_type}_regional_conus_valid_00z_06z_12z_18z_${var}_${stat}_${end}  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}_valid_00z_06z_12z_18z.conus_glb.png
           fi
         fi
      fi	 

      done #score_type
    done #var
   done  #stat
done     #vars


tar -cvf evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar *.png

cp  evs.plots.sref.grid2obs.past${past_days}days.v${VDATE}.tar  $COMOUT/$STEP/$COMPONENT/$RUN.$VDATE/.  









