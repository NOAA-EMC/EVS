#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href snowfall plotting python script
# Last updated: 10/30/2023, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

cd $DATA

export machine=${machine:-"WCOSS2"}
export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs


export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF_SNOW'
models='HREF_SNOW'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central'

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************
# Virtual link the href's stat data files of past 31/90 days
#*************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 

export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}

verif_case=precip
verif_type=ccpa

#***************************************
# Build a POE file to collect sub=jobs
# **************************************
> run_all_poe.sh

for VX_MASK_LIST in $VX_MASK_LISTs ; do
 	
for stats in ets_fbias ratio_pod_csi fss ; do 
 if [ $stats = ets_fbias ] ; then
    stat_list='ets, fbias'
    line_tp='ctc'
    VARs='WEASD'
    interp_pnts=''
    score_types='threshold_average '
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='WEASD'
    interp_pnts=''
    score_types='performance_diagram'
 elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='WEASD'    
    interp_pnts='1,9,25,49,91,121'
    score_types='threshold_average' 
 else
  err_exit "$stats is not a valid stat"
 fi   

 for score_type in $score_types ; do

  for VAR in $VARs ; do

     for FCST_LEVEL_value in A06 A24 ; do
 
	 OBS_LEVEL_value=$FCST_LEVEL_value

    	 if [ $FCST_LEVEL_value  = A06 ] ; then
            export fcst_leads='6,12,18,24,30,36,42,48'
            export fcst_valid_hour='0,6,12,18'
         elif [ $FCST_LEVEL_value = A24 ] ; then
            export fcst_leads='24,30,36,42,48'
            export fcst_valid_hour='0,12'
         fi


      for lead in $fcst_leads ; do

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

       for line_type in $line_tp ; do 

	 #*****************************
	 # Build sub-jobs
	 # ****************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh  

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

	 if [ $stats = fss ] ; then
	   
	   echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         else	   
           echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
	 fi

         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
 
         thresh_fcst='>=0.0254, >=0.1016, >=0.2032, >=0.3048'
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #end of vx_mask_list
chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 30 -ppn 30 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for stats in ets fbias fss ; do
  score_type='threshold_average' 
  scoretype='threshmean'

  for var in weasd ; do
   for level in 06h 24h ; do
    if [ $stats = fss ] ; then 
       if [ $level = 06h ] ; then
        valid=valid_00z_06z_12z_18z
        lead=width1-3-5-7-9-11_f6-12-18-24-30-36-42-48
       elif [ $level = 24h ] ; then
        valid=valid_00z_12z
        lead=width1-3-5-7-9-11_f24-30-36-42-48
       fi	
    else	    
      if [ $level = 06h ] ; then
	valid=valid_00z_06z_12z_18z
        lead=f6-12-18-24-30-36-42-48
      elif [ $level = 24h ] ; then
        valid=valid_00z_12z
        lead=f24-30-36-42-48
      fi
    fi

   for domain in conus conus_east conus_west conus_south conus_central  ; do
     if [ -s ${score_type}_regional_${domain}_${valid}_${level}_${var}_${stats}_${lead}.png ] ; then
       mv ${score_type}_regional_${domain}_${valid}_${level}_${var}_${stats}_${lead}.png  evs.href.${stats}.${var}_${level}.last${past_days}days.${scoretype}_valid_all_times.buk_${domain}.png
     fi
   done

  done
 done
done


score_type='performance_diagram'  
scoretype='perfdiag'

for var in weasd ; do
 for level in 06h 24h ; do
    if [ $level = 06h ] ; then
        valid=valid_00z_06z_12z_18z
        lead=f6-12-18-24-30-36-42-48__ge0.0254ge0.1016ge0.2032ge0.3048
    elif [ $level = 24h ] ; then
        valid=valid_00z_12z
        lead=f24-30-36-42-48__ge0.0254ge0.1016ge0.2032ge0.3048
    fi

   for domain in conus conus_east conus_west conus_south conus_central  ; do
      if [ -s ${score_type}_regional_${domain}_${valid}_${level}_${var}_${lead}.png ] ; then
         mv ${score_type}_regional_${domain}_${valid}_${level}_${var}_${lead}.png  evs.href.ctc.${var}_${level}.last${past_days}days.${scoretype}_valid_all_times.buk_${domain}.png
      fi 
   done
 done
done


tar -cvf evs.plots.href.snowfall.past${past_days}days.v${VDATE}.tar *.png

# Cat the plotting log files
log_dir="$DATA/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi


if [ $SENDCOM = YES ] && [ -s evs.plots.href.snowfall.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.snowfall.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.snowfall.past${past_days}days.v${VDATE}.tar
fi





