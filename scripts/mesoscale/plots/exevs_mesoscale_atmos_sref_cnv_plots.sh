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


verif_case=grid2obs
verif_type=conus_sfc

> run_all_poe.sh

for stats in  ets  fbias; do 

 if [ $stats = ets ] ; then	
  stat_list='ets'
 elif [ $stats = fbias ] ; then
  stat_list='fbias'
 fi

  line_tp='ctc'
  VARs='VISsfc HGTcldceil'
  score_types='lead_average threshold_average'

 for score_type in $score_types ; do

  export fcst_leads="vs_lead" 
 
  for lead in $fcst_leads ; do 

    export fcst_lead=" 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87"

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_values="L0"

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

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


	 if [ $VAR = VISsfc  ] ; then
            thresh_fcst='<805, <1609, <4828, <8045, <16090'
         elif [ $VAR = HGTcldceil  ] ; then
            thresh_fcst='<152, <305, <914, <1524, <3048'
	 fi

	 thresh_obs=$thresh_fcst

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
   mpiexec -np 8 -ppn 8 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
 ${DATA}/run_all_poe.sh
fi


cd $plot_dir

for var in hgt vis ; do 
 for stat in ets fbias  ; do
   for score_type in  lead_average threshold_average ; do
     if [ $var = hgt ] ; then
	 if [ $score_type = lead_average ] ; then
	   end=lt152lt305lt914lt1524lt3048.png
	   scoretype=fhrmean
	 elif [ $score_type = threshold_average ] ; then
	   end=f6_to_f87.png
	   scoretype=threshmean
	 fi
     elif [ $var = vis ] ; then
	 if [ $score_type = lead_average ] ; then
	   end=lt805lt1609lt4828lt8045lt16090.png
	   scoretype=fhrmean
	 elif [  $score_type = threshold_average ] ; then
           end=f6_to_f87.png
	   scoretype=threshmean
         fi
      fi

      mv ${score_type}_regional_conus_valid_00z_06z_12z_18z_${var}_${stat}_${end}  evs.sref.${stat}.${var}.last${past_days}days.${scoretype}_valid_00z_06z_12z_18z.buk_conus.png

  done    #score_type
 done     #stat
done     #var


tar -cvf evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar *.png

cp evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar  $COMOUT/$STEP/$COMPONENT/$RUN.$VDATE/.  





