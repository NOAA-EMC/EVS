#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href cape plotting python script
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

model_list='HREF_MEAN'
models='HREF_MEAN'

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
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day HREF_MEAN
  n=$((n+1))
done 

																  
export fcst_init_hour="0,6,12,18"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

export fcst_init_hour="0,6,12,18"
init_time='init00z_06z_12z_18z'
line_type=ctc
verif_case=grid2obs

#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

for valid_time in 00 12 ; do 

 for stats in csi fbias  ; do 

   stat_list=$stats
   VARs='CAPEsfc MLCAPE'
   score_types='lead_average threshold_average'

  for score_type in $score_types ; do
 
    if [ $score_type = lead_average ] ; then   
       thresholds="250  500 1000 2000"
       fcst_leads="06,12,18,24,30,36,42,48"
    elif [ $score_type = threshold_average ] ; then
       thresholds=">=250,>=500,>=1000,>=2000"
       fcst_leads="06 12 18 24 30 36 42 48"
    fi 

   for threshold in $thresholds ; do 

    for fcst_lead in $fcst_leads ; do 

	#thresh and lead are just for file names
	  if [  $score_type = lead_average ] ; then
	      thresh=$threshold
	      lead=all_leads
	  elif [  $score_type = threshold_average ] ; then
	      thresh=all_thresholds
	      lead=$fcst_lead
	 fi

     for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = CAPEsfc ]  ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
       fi 	  

       if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then 
           doms="dom1 dom2 dom3 dom4 dom5 dom6 dom7 dom8"
       fi 

       for dom in $doms ; do 

         if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then
	     if [ $dom = dom1 ] ; then
	         VX_MASK_LIST="CONUS, CONUS_East, CONUS_West"
	     elif [ $dom = dom2 ] ; then
	         VX_MASK_LIST="CONUS_South, CONUS_Central, Alaska"
	     elif [ $dom = dom3 ] ; then
	         VX_MASK_LIST="Appalachia, CPlains, DeepSouth"
	     elif [ $dom = dom4 ] ; then
	         VX_MASK_LIST="GreatBasin, GreatLakes, Mezquital"
	     elif [ $dom = dom5 ] ; then
	         VX_MASK_LIST="MidAtlantic, NorthAtlantic, NPlains"
	     elif [ $dom = dom6 ] ; then
	         VX_MASK_LIST="NRockies, PacificNW, PacificSW"
	     elif [ $dom = dom7 ] ; then
	         VX_MASK_LIST="SRockies, Prairie, Southeast"
	     elif [ $dom = dom8 ] ; then
	         VX_MASK_LIST="Southwest, SPlains"
             fi
        fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

	 #*********************
	 # Build sub-jobs
	 #*********************
         > run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh  

        verif_type=conus_sfc

	if [ $score_type = lead_average ] ; then
           echo "export PLOT_TYPE=lead_average_valid" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        else		
           echo "export PLOT_TYPE=$score_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        fi

        echo "export field=${var}_${level}" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

        echo "export eval_period=TEST" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

         echo "export line_type=$line_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
         echo "export interp=BILIN" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh
         echo "export score_py=$score_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh


	 if [ $score_type = lead_average ] ; then
           thresh_fcst=">=${threshold}"
           thresh_obs=$thresh_fcst
         elif [ $score_type = threshold_average ] ; then
           thresh_fcst=${threshold}
           thresh_obs=$thresh_fcst
         else
           thresh_fcst=' '
           thresh_obs=' '
         fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$valid_time!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

         chmod +x  run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

         echo "${DATA}/run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh

         chmod +x  run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh 
         echo "${DATA}/run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${valid_time}.sh" >> run_all_poe.sh


     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of dom 

 done #end of score_type

 done #end of thresh 

done #end of stats 

done #end of valid_time

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 840 -ppn 84 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir
 	
for score_type in lead_average threshold_average; do

 for valid in 00z 12z ; do

  for var in cape mlcape ; do
   if [ $var = cape ] ; then
       level=l0
       stats="csi fbias"
   elif [ $var = mlcape ] ; then
       level=ml
       stats="csi fbias"
   fi

  if [ $score_type = lead_average ] ; then
     scoretype=fhrmean
     leads="all"
  else 
     scoretype=threshmean
     leads="f6 f12 f18 f24 f30 f36 f42 f48"
  fi 

  for stat in $stats ; do

   for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

    for lead in $leads ; do   
      if [ $lead = f6 ] ; then
	  new_lead=f06
      else 
	  new_lead=$lead
      fi

     if [ $domain = alaska ] ; then
         new_domain=$domain
     else
         new_domain=buk_${domain}
     fi


      if [ $score_type = lead_average ] ; then
   
          for thresh in ge250 ge500 ge1000 ge2000 ; do
	   if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}_${thresh}.png ] ; then
             mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}_${thresh}.png evs.href.${stat}.${var}_${level}.${thresh}.last${past_days}days.${scoretype}_valid_${valid}.${new_domain}.png
           fi
          done
      else
	  if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}_${lead}.png ] ; then   
           mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}_${lead}.png  evs.href.${stat}.${var}_${level}.last${past_days}days.${scoretype}_valid_${valid}.${new_lead}.${new_domain}.png

     	  fi
       fi

      done #lead
    done #domain
   done #stat
  done  #var
 done   #valid 
done    #score_type

tar -cvf evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar *.png

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

if [ $SENDCOM = YES ] && [ -s evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
 $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar
fi
















