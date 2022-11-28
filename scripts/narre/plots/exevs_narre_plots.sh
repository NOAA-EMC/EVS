#!/bin/sh

set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/NARRE_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs


export eval_period='TEST'
#export past_days=0

export init_end=$VDATE
export valid_end=$VDATE

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
  sh $USHevs/narre/evs_get_narre_stat_file_link.sh $day
  n=$((n+1))
done 

VX_MASK_LIST="G130 G214"

fcst_init_hour="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
fcst_valid_hour="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
fcst_lead="1,2,3,4,5,6,7,8,9,10,11,12"



for grid in $VX_MASK_LIST ; do

 for score_type in performance_diagram  threshold_average time_series valid_hour_average lead_average ; do
 #for score_type in threshold_average ; do
  export PLOT_TYPE=$score_type

 #for var in HGTcldceil ; do 
  for var in VISsfc HGTcldceil ; do 
 
   #for line_type in ctc sl1l2 ; do 
   for line_type in ctc ; do 

     if [ $var = VISsfc  ] || [ $var = HGTcldceil ] || [ $var = TCDC ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L0"
     elif [ $var = TMP2m ] || [ $var = RH2m ] || [ $var = DPT2m ] ; then
      FCST_LEVEL_value="Z2"
      OBS_LEVEL_value="Z2"
     elif [ $var = UGRD10m ] || [ $var = VGRD10m ] ; then
      FCST_LEVEL_value="Z10"
      OBS_LEVEL_value="Z10"
     elif [ $var = CAPEsfc ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L100000-0"
     elif [ $var = PRMSL ] ; then
      FCST_LEVEL_value="Z0"
      OBS_LEVEL_value="Z0"
     fi

     if [ $line_type = ctc ] ; then
       if [ $score_type = performance_diagram ] ; then
         stat_list="sratio, pod, csi"
       else
         stat_list="csi"
       fi
     elif [ $line_type = sl1l2 ] ; then
       stat_list="rmse, bias"
     fi

     if [ $var = VISsfc  ] ; then
      thresh="<=800,<=1600,<=4800,<=8000,<=16000"
     elif [ $var = HGTcldceil ] ; then
      thresh="<=152,<=305,<=916,<=1524,<=3048"
     fi

export vx_mask_list=$grid
export verif_case='grid2obs'
export verif_type='conus_sfc'

export log_level="INFO"
export met_ver="10.0"
export model="NARRE_MEAN"

export eval_period="TEST"
if [ $score_type = valid_hour_average ] ; then
  export date_type="INIT"
else
  export date_type="VALID"
fi

export var_name=$var
export fcts_level=$FCST_LEVEL_value
export obs_level=$OBS_LEVEL_value


export line_type=$line_type
export interp='NEAREST'
export score_py=$score_type

     sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/narre/evs_narre_plots.sh > run_py.${var}_${line_type}.${score_type}.${grid}.sh

     chmod +x run_py.${var}_${line_type}.${score_type}.${grid}.sh

     sh run_py.${var}_${line_type}.${score_type}.${grid}.sh
 
    done

  done

 done

done


set -x 

plot_dir=$DATA/out/ceil_vis/${valid_beg}-${valid_end}
cd $plot_dir
  
tar -cvf plots_narre_grid2obs_v${VDATE}.tar *.png

cp plots_narre_grid2obs_v${VDATE}.tar  $COMOUT/.  

cd $DATA




