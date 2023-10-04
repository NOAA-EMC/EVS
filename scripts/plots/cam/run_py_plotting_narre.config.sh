#!/bin/sh

VX_MASK_LIST="G130 G214"
#VX_MASK_LIST="G130"

#line_type='ctc'
#line_type='sl1l2'

fcst_init_hour="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
fcst_valid_hour="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
fcst_lead="1,2,3,4,5,6,7,8,9,10,11,12"

for grid in $VX_MASK_LIST ; do

 for score_type in performance_diagram  threshold_average time_series valid_hour_average lead_average ; do
 #for score_type in threshold_average ; do

 #for var in HGTcldceil ; do 
  for var in VISsfc HGTcldceil ; do 
 
   for line_type in ctc sl1l2 ; do 
   #for line_type in ctc ; do 

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
export ush_dir="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/EVS/ploting/verif_plotting.v2/ush"
export prune_dir="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/EVS/ploting/data"
export save_dir="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/EVS/ploting/out"
export output_base_dir="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/com/plot_stat/regional/stat_archive/"
export log_metplus="${save_dir}/logs/NARRE_verif_plotting_job_`date '+%Y%m%d-%H%M%S'`_$$.out"
export log_level="INFO"
export met_ver="10.0"
export model="NARRE_MEAN"

export eval_period="TEST"
if [ $score_type = valid_hour_average ] ; then
  export date_type="INIT"
  export init_beg=20220416
  export init_end=20220426
else
  export date_type="VALID"
  export valid_beg=20220416
  export valid_end=20220426
fi

export var_name=$var
export fcts_level=$FCST_LEVEL_value
export obs_level=$OBS_LEVEL_value


export line_type=$line_type
export interp='NEAREST'
export score_py=$score_type

     sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  py_plotting_narre.config > run_py.${var}_${line_type}.${score_type}.${grid}.sh


     chmod +x run_py.${var}_${line_type}.${score_type}.${grid}.sh

     sh run_py.${var}_${line_type}.${score_type}.${grid}.sh
 
    done

  done

 done

done

  

