#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the sref precip plotting python script
# Last updated: 
#                04/10/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#                10/27/2023, Binbin Zhou Lynker@EMC/NCEP
# ******************************************************************************
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

restart=$COMOUTplots/restart/$past_days/sref_precip_plots
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
  export err=$?; err_chk
  n=$((n+1))
done 


VX_MASK_LIST="CONUS"
																  
export fcst_init_hour="0,3,6,9,12,15,18,21"
export fcst_valid_hours="0,3  6,9  12,15 18,21"
valid_time='valid00z_03z_06z_09z_12z_15z_18z_21z'
init_time='init00_to_21z'

export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}
#For restart:
if [ ! -d $plot_dir ] ; then
 mkdir -p $plot_dir
fi


verif_case=precip
verif_type=ccpa 

#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

VARs=APCP_06
FCST_LEVEL_values=A6

for fcst_valid_hour in $fcst_valid_hours ; do

for stats in  ets fbias fss ; do 

 if [ $stats = ets ] ; then
  stat_list='ets'
  line_tp='ctc'
  score_types='lead_average threshold_average'
  export interp_pnts=''
 elif [ $stats = fbias ] ; then
  stat_list='fbias'
  line_tp='ctc'
  score_types='lead_average threshold_average'
  export interp_pnts=''
elif [ $stats = fss ] ; then
  stat_list='fss'
  score_types='lead_average'
  line_tp='nbrcnt'
  interp_pnts='1,9,25,49,91,121'
 else
  err_exit "$stats is wrong stat"
 fi   

 for score_type in $score_types ; do

  if [ $score_type = lead_average ] ; then
        threshes='>=0.1 >=1 >=5 >=10 >=25 >=50'
        export fcst_leads="24,36,48,60,72,84"
  elif [ $score_type = threshold_average ] ; then
	threshes='>=0.1,>=1,>=5,>=10,>=25,>=50'
	export fcst_leads="24 36 48 60 72 84"
  fi

 
  for fcst_lead in $fcst_leads ; do
      if [ $score_type = lead_average ] ; then
	 lead="all_leads"
      elif [ $score_type = threshold_average ] ; then
	 lead=$fcst_lead
      fi

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

       for thr in $threshes ; do

	if [ $thr = '>=0.1' ] ; then
	  thresh=0.1
        elif [ $thr = '>=1' ] ; then
          thresh=1
        elif [ $thr = '>=5' ] ; then
	  thresh=5
        elif [ $thr = '>=10' ] ; then
          thresh=10
        elif [ $thr = '>=25' ] ; then
          thresh=25
        elif [ $thr = '>=50' ] ; then
          thresh=50
        elif [ $thr = '>=0.1,>=1,>=5,>=10,>=25,>=50' ] ; then
          thresh=all
	fi

         thresh_fcst=$thr
         thresh_obs=$thresh_fcst

	 #*********************
	 # Build sub-jobs
	 #*********************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh  

        #*******************************************************************************************************************
	#  Check if this sub-job has been completed in the previous run for restart
	    if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.completed ] ; then
	#*******************************************************************************************************************

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
         if [ $stats = fss ] ; then
	   echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
	 else
	   echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
	 fi 

         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh


         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/mesoscale/evs_sref_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

         ####################################################################
         #Save for restart:
         ####################################################################
         echo "cp ${plot_dir}/${score_type}*${stats}*.png $restart/." >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh
         echo "[[ $? = 0 ]] && >$restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${thresh}.${fcst_valid_hour}.sh" >> run_all_poe.sh

        else 
      
	 #For restart: copy existing png files from pevious runs
	 cp $restart/${score_type}*${stats}*.png ${plot_dir}/. 
       
	fi 

       done #end of thresh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done # end of fcst_valid_hour
chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
# **************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 100 -ppn 100 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
   export err=$?; err_chk
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for valid in 00z_03z 06z_09z 12z_15z 18z_21z ; do
for stats in  ets fbias fss  ; do
 if [ $stats = ets ] || [ $stats = fbias ] ; then 
   score_types='lead_average threshold_average'
 else
   score_types='lead_average'
 fi   
 for score_type in $score_types ; do

  if [ $score_type = lead_average ] ; then 
    if [ $stats = ets ] || [ $stats = fbias ] || [ $stats = fss ] ; then
      threshes='ge0.1 ge1 ge5 ge10 ge25 ge50'
      scoretype='fhrmean'
    fi
  elif [ $score_type = threshold_average ] ; then
      threshes='f24-36-48-60-72-84'
      scoretype='threshmean'
  fi

  var='apcp_06'
  level='6h'
  new_level='a06'

  for thresh in $threshes ; do

    if [ $score_type = lead_average ] ; then
      if [ $stats = ets ] || [ $stats = fbias ] ; then
       if [ -s ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_${thresh}.png ] ; then
         mv ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_${thresh}.png evs.sref.${stats}.apcp_6a.${thresh}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
       fi
      elif [ $stats = fss ] ; then
       if [ -s ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_width1-3-5-7-9-11_${thresh}.png ] ; then
         mv ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_width1-3-5-7-9-11_${thresh}.png evs.sref.${stats}.apcp_6a.${thresh}.last${past_days}days.${scoretype}_valid_${valid}.buk_conus.png
       fi
      fi
    elif [ $score_type = threshold_average ] ; then
	 for lead in f24 f36 f48 f60 f72 f84 ; do 
	   if [ -s ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_${lead}.png ] ; then
             mv ${score_type}_regional_conus_valid_${valid}_6h_apcp_06_${stats}_${lead}.png evs.sref.${stats}.apcp_6a.last${past_days}days.${scoretype}_valid_${valid}.${lead}.buk_conus.png
	   fi
	 done
    fi	 

  done   # thresh
 done    #score_type
done     #stats
done     #valid

tar -cvf evs.plots.sref.precip.past${past_days}days.v${VDATE}.tar *.png


if [ $SENDCOM = YES ] && [ -s evs.plots.sref.precip.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.sref.precip.past${past_days}days.v${VDATE}.tar  $COMOUTplots/.  
fi


if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.sref.precip.past${past_days}days.v${VDATE}.tar
fi







