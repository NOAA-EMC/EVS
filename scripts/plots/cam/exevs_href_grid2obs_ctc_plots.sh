#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href ctc plotting python script
# Last updated: 
#               07/09/2024, add restart, by Binbin Zhou Lynker@EMC/NCEP
#               05/30/2024, Binbin Zhou Lynker@EMC/NCEP
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

restart=$COMOUT/restart/$past_days/href_ctc_plots
if [ ! -d  $restart ] ; then
  mkdir -p $restart
fi

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
  export err=$?; err_chk
  n=$((n+1))
done 

																  
export fcst_init_hour="0,6,12,18"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
#For restart:
if [ ! -d $plot_dir ] ; then
  mkdir -p $plot_dir
fi

export fcst_init_hour="0,6,12,18"
init_time='init00z_06z_12z_18z'

verif_case=grid2obs
line_type='ctc'

#*****************************************
# Build a POE file to collect sub-jobs
#****************************************
> run_all_poe.sh

for fcst_valid_hour in 00 03 06 09 12 15 18 21 ; do
    
if [ "$fcst_valid_hour" -eq "03" ] || [ "$fcst_valid_hour" -eq "09" ] || [ "$fcst_valid_hour" -eq "15" ] || [ "$fcst_valid_hour" -eq "21" ] ; then
 stats_list="csi_fbias ratio_pod_csi"
else
 stats_list="csi_fbias ets_fbias ratio_pod_csi"
fi
for stats in $stats_list ; do 
 if [ "$fcst_valid_hour" -eq "03" ] || [ "$fcst_valid_hour" -eq "09" ] || [ "$fcst_valid_hour" -eq "15" ] || [ "$fcst_valid_hour" -eq "21" ] ; then
    if [ $stats = csi_fbias ] ; then
       stat_list='csi, fbias'
       VARs='VISsfc HGTcldceil'
       score_types='lead_average threshold_average'
    elif [ $stats = ratio_pod_csi ] ; then
       stat_list='sratio, pod, csi'
       VARs='VISsfc HGTcldceil'
       score_types='performance_diagram'   
    else
     err_exit "$stats is not a valid stat for vhr $fcst_valid_hour"
    fi   
 elif [ "$fcst_valid_hour" -eq "06" ] || [ "$fcst_valid_hour" -eq "18" ] ; then
    if [ $stats = csi_fbias ] ; then
       stat_list='csi, fbias'
       VARs='VISsfc HGTcldceil'
       score_types='lead_average threshold_average'
    elif [ $stats = ets_fbias ] ; then
       stat_list='ets, fbias'
       VARs='TCDC'
       score_types='lead_average threshold_average'
    elif [ $stats = ratio_pod_csi ] ; then
       stat_list='sratio, pod, csi'
       VARs='VISsfc HGTcldceil TCDC'
       score_types='performance_diagram'   
    else
     err_exit "$stats is not a valid stat for vhr $fcst_valid_hour"
    fi   
 else
    if [ $stats = csi_fbias ] ; then
       stat_list='csi, fbias'
       VARs='VISsfc HGTcldceil'
       score_types='lead_average threshold_average'
    elif [ $stats = ets_fbias ] ; then
       stat_list='ets, fbias'
       VARs='TCDC'
       score_types='lead_average threshold_average'
    elif [ $stats = ratio_pod_csi ] ; then
       stat_list='sratio, pod, csi'
       VARs='VISsfc HGTcldceil CAPEsfc TCDC MLCAPE'
       score_types='performance_diagram'   
    else
     err_exit "$stats is not a valid stat for vhr $fcst_valid_hour"
    fi   
 fi
 for score_type in $score_types ; do

  export fcst_leads="6,9,12,15,18,21,24,27,30,33,36,39,42,45,48"

  for fcst_lead in $fcst_leads ; do 

    #just for sub-job names	  
    lead=all_leads

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	
       if [ $VAR = CAPEsfc ] ; then 
	  new_var=cape
       elif [ $VAR = MLCAPE ] ; then
	  new_var=mlcape
       elif [ $VAR = VISsfc ] ; then
	  new_var=vis
       elif [ $VAR = HGTcldceil ] ; then
          new_var=hgtcldceil
       elif [ $VAR = TCDC ] ; then
          new_var=tcdc
       fi

       if [ $VAR = CAPEsfc ] || [ $VAR = VISsfc ] || [ $VAR = HGTcldceil ] || [ $VAR = TCDC ] ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
       fi 	  

       doms="dom1 dom2 dom3 dom4 dom5 dom6 dom7 dom8"

       for dom in $doms ; do 

	 if [ $dom = dom1 ] ; then
            VX_MASK_LIST="CONUS, CONUS_East, CONUS_West"
	    subregions="conus conus_east conus_west"
         elif [ $dom = dom2 ] ; then
	    VX_MASK_LIST="CONUS_South, CONUS_Central, Alaska"
	    subregions="conus_south conus_central alaska"
         elif [ $dom = dom3 ] ; then
	    VX_MASK_LIST="Appalachia, CPlains, DeepSouth"
	    subregions="appalachia cplains deepsouth"
         elif [ $dom = dom4 ] ; then
	    VX_MASK_LIST="GreatBasin, GreatLakes, Mezquital"
	    subregions="greatbasin greatlakes mezquital"
	 elif [ $dom = dom5 ] ; then
	    VX_MASK_LIST="MidAtlantic, NorthAtlantic, NPlains"
	    subregions="midatlantic northatlantic nplains"
	 elif [ $dom = dom6 ] ; then
            VX_MASK_LIST="NRockies, PacificNW, PacificSW" 
	    subregions="nrockies pacificnw pacificsw"
	 elif [ $dom = dom7 ] ; then
            VX_MASK_LIST="SRockies, Prairie, Southeast"
	    subregions="srockies prairie southeast"
	 elif [ $dom = dom8 ] ; then
            VX_MASK_LIST="Southwest, SPlains"
	    subregions="southwest splains"
	 fi

      for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

	 #**********************
	 # Build sub-jobs
	 # *********************
         > run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh  

       #***********************************************************************************************************************************
       #  Check if this sub-job has been completed in the previous run for restart
       if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.completed ] ; then
       #***********************************************************************************************************************************

        verif_type=conus_sfc

	echo "#!/bin/ksh" >>  run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

	if [ $score_type = lead_average ] ; then
           echo "export PLOT_TYPE=lead_average_valid" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        else            
           echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        fi

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

	 if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then
           thresh_fcst='>=250, >=500, >=1000, >=2000'
	 elif [ $VAR = VISsfc  ] ; then
           thresh_fcst='<805, <1609, <4828, <8045, <16090'
         elif [ $VAR = HGTcldceil  ] ; then
            thresh_fcst='<152, <305, <914, <1524, <3048'
	 elif [ $VAR = TCDC ] ; then
	    #Binbin Note: can not set threshold operands '<' and '>=' together in the threshold list
            #thresh_fcst='<10, >=10, >=50, >=90'		 
            thresh_fcst='>=10, >=50, >=90'		 
         fi	    
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

	 #Save for restart
         echo "for domain in $subregions ; do " >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
	 echo "  if [ -s ${plot_dir}/${score_type}_regional_\${domain}_valid_${fcst_valid_hour}z_${new_var}_*.png ] ; then " >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
	 echo "    cp -v ${plot_dir}/${score_type}_regional_\${domain}_valid_${fcst_valid_hour}z_${new_var}_*.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
	 echo "    >$restart/run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
	 echo "  fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
	 echo "done" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh" >> run_all_poe.sh

      else
	 #Restart from png files of previous runs
	 for domain in $subregions ; do
	   cp $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${new_var}_*.png ${plot_dir}/.
	 done
      fi

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of dom 

 done #end of score_type

done #end of stats 

done #end of valid 

chmod +x run_all_poe.sh


#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 820 -ppn 82 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for valid in 00z 03z 06z 09z 12z 15z 18z 21z ; do

 for domain in conus conus_east conus_west conus_south conus_central alaska  appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

 if [ $domain = alaska ] ; then
    new_domain=$domain
 else
    new_domain=buk_${domain}
 fi

 for var in vis hgtcldceil tcdc cape mlcape; do
  if [ $var = vis ] ; then
    var_new=$var
    level=l0
  elif [ $var = hgtcldceil ] ; then
    var_new=ceiling
    level=l0
  elif [ $var = tcdc ] ; then
    var_new=cloud
    level=l0
  elif [ $var = cape ] ; then
    var_new=cape
    level=l0
  elif [ $var = mlcape ] ; then
    var_new=mlcape
    level=ml
  fi

  if [ -s performance_diagram_regional_${domain}_valid_${valid}_${var}_*.png ] ; then
    mv performance_diagram_regional_${domain}_valid_${valid}_${var}_*.png evs.href.ctc.${var_new}_${level}.last${past_days}days.perfdiag_valid_${valid}.${new_domain}.png
  fi 

 done
done
done

for valid in 00z 03z 06z 09z 12z 15z 18z 21z ; do

 for score_type in lead_average threshold_average; do

  for var in vis hgtcldceil tcdc ; do
   if [ $var = vis ] ; then
       var_new=$var
       level=l0
       stats="csi_fbias csi fbias"
   elif [ $var = hgtcldceil ] ; then
       var_new=ceiling
       level=l0
       stats="csi_fbias csi fbias"
   elif [ $var = tcdc ] ; then
       var_new=cloud
       level=l0
       stats="ets_fbias ets fbias" 
   fi

  if [ $score_type = lead_average ] ; then
     scoretype=fhrmean
  elif [ $score_type = threshold_average ] ; then
     scoretype=threshmean
  fi 

  for stat in $stats ; do

    for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

     if [ $domain = alaska ] ; then
         new_domain=$domain
     else
         new_domain=buk_${domain}
     fi
    
     if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}*.png ] ; then
         mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stat}*.png evs.href.${stat}.${var_new}_${level}.last${past_days}days.${scoretype}_valid_${valid}.${new_domain}.png
     fi

       done #domain
    done #stat
   done  #var
 done    #score_type
done

tar -cvf evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar *.png

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


if [ $SENDCOM = YES ] && [ -s evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar
fi














