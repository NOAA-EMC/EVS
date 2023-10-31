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

met_v=`echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g"`
export eval_period='TEST'

export interp_pnts='' 

export init_end=$VDATE
export valid_end=$VDATE

model_list='ECME CMCE GEFS'
models='ECME, CMCE, GEFS'

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
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"

export fcst_init_hour="0,12"
export fcst_valid_hour="12"
valid_time='valid12z'
init_time='init00z_12z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir

verif_case=grid2obs
verif_type=upper_air

> run_all_poe.sh

for stats in rmse_spread me ; do 

if [ $stats = me ] ; then
  stat_list='me'
  line_tp='ecnt'
elif [ $stats = mae ] ; then
  stat_list='mae'
  line_tp='ecnt'
elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
else
  echo $stats is wrong stat
  exit
fi   

 for score_type in stat_by_level ; do

  export fcst_leads="0 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
 
  for lead in $fcst_leads ; do 

    export fcst_lead=$lead

    for VAR in HGT TMP UGRD VGRD RH ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = HGT ] || [ $VAR = UGRD ] || [ $VAR = VGRD ]; then
          FCST_LEVEL_value="P1000,P925,P850,P700,P500,P300,P250,P200,P100,P50,P10"
       elif [ $VAR = TMP ] || [ $VAR = RH ] ; then
          FCST_LEVEL_value="P1000,P925,P850,P700,P500,P250,P200,P100,P50,P10"
       fi


	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh  

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

	 thresh=' '
         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh!g" -e "s!thresh_obs!$thresh!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh 
         echo " ${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh

if [ $run_mpi = yes ] ; then
   mpiexec -np 320 -ppn 64 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

# Cat the plotting log file
log_file=$DATA/logs/GENS_verif_plotting_job.out
if [ -s $log_file ]; then
    echo "Start: $log_file"
    cat $log_file
    echo "End: $log_file"
fi

cd $plot_dir

for stats in rmse_spread me ; do
    if [ $stats = rmse_spread ]; then
        evs_graphic_stats="rmse_sprd"
    else
        evs_graphic_stats=$stats
    fi
    for domain in g003 nhem shem tropics conus ; do
        if [ $domain = g003 ] ; then
            domain_new=glb
        elif [ $domain = conus ]; then
            domain_new="buk_conus"
        else
            domain_new=$domain
        fi
        for var in hgt tmp ugrd vgrd rh ; do
            leads="0 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
            for lead in $leads ; do
                lead_new=$(printf "%03d" "${lead}")
                mv stat_by_level_regional_${domain}_valid_12z_${var}_${stats}_f${lead}.png  evs.global_ens.${evs_graphic_stats}.${var}_all.last${past_days}days.vertprof_valid12z_f${lead_new}.g003_${domain_new}.png
            done #lead
        done #var
    done  #domain
done     #stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    cp evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar  $COMOUT/.
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi


