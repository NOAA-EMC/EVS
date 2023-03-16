#!/bin/ksh
#
# Note: Since both CAPEsfc and MDCALE's fcst var are same 'CAPE', the output png file name are same with 'cape'. 
# Then can not separate them. So have to use 2 scripts to plot CAPEsfc and MLCAPE, respectively  


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

n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  sh $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day HREF_MEAN
  n=$((n+1))
done 


VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska,  Appalachia, CPlains, DeepSouth, GreatBasin, GreatLakes, Mezquital, MidAtlantic, NorthAtlantic, NPlains, NRockies, PacificNW, PacificSW, Prairie, Southeast, Southwest, SPlains, SRockies"
#VX_MASK_LIST="CONUS"
																  
export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21,24"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21"
valid_time='valid00z_03z_06z_09z_12z_15z_18z_21z'
init_time='init00z_06z_12z_18z'

verif_case=grid2obs

> run_all_poe.sh

for stats in csi fbias ratio_pod_csi; do 
 if [ $stats = csi ] ; then
    stat_list='csi'
    line_tp='ctc'
    VARs='MLCAPE'
    score_types='threshold_average'
 elif [ $stats = fbias ] ; then
    stat_list='fbias'
    line_tp='ctc'
    VARs='MLCAPE'
    score_types='threshold_average'
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='MLCAPE'
    score_types='performance_diagram'   
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in $score_types ; do

  export fcst_leads="6,9,12,15,18,21,24,27,30,33,36,39,42,45,48"

  for lead in $fcst_leads ; do 

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_values="ML"

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      
        if [ $VAR = MLCAPE ] ; then 
          level=mid		
        fi

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

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

         thresh_fcst='>=250, >=500, >=1000, >=2000'
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "sh run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 24 -ppn 24 --cpu-bind verbose,depth cfp run_all_poe.sh
else
 sh run_all_poe.sh
fi


cd $plot_dir

for stats in csi fbias ratio_pod_csi ; do
  if [ $stats = ratio_pod_csi ] ; then
    score_types='performance_diagram'
  else
    score_types='threshold_average' 
  fi 

  for score_type in $score_types ; do

      files=`ls ${score_type}*`

     if [ $score_type = threshold_average ] ; then
	 scoretype=thresholdmean
	 if [ $stats = csi ] ; then 
            thresh=_csi_f6_to_f48.png
	    index0=26
	    stat_new='csi'
         else
	    thresh=_fbias_f6_to_f48.png
            index0=26
            stat_new='fbias'	
         fi	    
     else
	 scoretype=perfdiag
	 thresh=_f6_to_f48_ge250ge500ge1000ge2000.png
	 index0=28
	 stat_new='ctc'
     fi

     for file in $files ; do     
	echo file=$file
	x1=${file%%valid*}
	x2=${file%%cape*}
	index1=${#x1}
	echo $index1
	index2=${#x2}
	length1=$((index1-index0))
	length1=$((length1-1))
	length2=$((index2-index1))
        domain=${file:${index0}:${length1}}
	valid=${file:${index1}:${length2}}
	echo domain=$domain
	echo valid=$valid

         mv ${score_type}_regional${domain}_${valid}cape$thresh evs.href.${stat_new}.mlcape.last${past_days}days.${scoretype}.${valid}.buk${domain}.png
     done
  done
done

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/href/grid2obs

tar -cvf plots.href.grid2obs.mlcape.v${VDATE}.past${past_days}days.tar *.png

cp plots.href.grid2obs.mlcape.v${VDATE}.past${past_days}days.tar  $COMOUT/.  
















































