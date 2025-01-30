#!/bin/bash
source /u/ho-chun.huang/versions/run.ver
#
declare revfile=( aqm_check_settings.py aqm_create_output_dirs.py aqm_get_data_files.py aqm_plots_grid2obs_create_job_scripts.py aqm_plots_lead_average.py aqm_plots_performance_diagram.py aqm_plots_production_tof72.py aqm_plots.py aqm_plots_specs.py aqm_plots_threshold_average.py aqm_plots_time_series.py aqm_plots_valid_hour_average.py aqm_util.py )

old_ver='mallory.row'
new_ver='ho-chun.huang'
old_ver='Data Missing for EVS global_det'
new_ver='Data Missing for EVS global_ens_chem'
old_ver='\/global_ens\/'
new_ver='\/aqm\/'
for i in "${revfile[@]}"; do
   echo ${i}
   if [ "${i}" == $0 ]; then continue; fi
   if [ "${i}" == "xtest1" ]; then continue; fi
   if [ -d ${i} ]; then continue; fi
   ## mv ${i}.bak ${i}
   if [ -e xtest1 ]; then /bin/rm -f xtest1; fi
   grep "${old_ver}" ${i} > xtest1
   if [ -s xtest1 ]; then
      mv ${i} ${i}.bak
      sed -e "s!${old_ver}!${new_ver}!g" ${i}.bak > ${i}
      ## awk '!/SHELL=\/bin\/bash/' ${i}.bak > ${i}
      ## echo "diff ${i} ${i}.bak"
      chmod u+x ${i}
      diff ${i} ${i}.bak
   fi
done
/bin/rm xtest1 tlist
##
## delete a block of line
##
## old_beg="if cdate_beg == cdate_end:$"
## old_end="   figure_date = header_date$"
## sed "/${old_beg}/,/${old_end}/d" ${i}.bak > ${i}

exit
