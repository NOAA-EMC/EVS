#!/bin/bash
source /u/ho-chun.huang/versions/run.ver
#
declare revfile=( aqm_check_settings.py aqm_create_output_dirs.py aqm_get_data_files.py aqm_plots_grid2obs_create_job_scripts.py aqm_plots_lead_average.py aqm_plots_performance_diagram.py aqm_plots_production_tof72.py aqm_plots.py aqm_plots_specs.py aqm_plots_threshold_average.py aqm_plots_time_series.py aqm_plots_valid_hour_average.py aqm_util.py )

for i in "${revfile[@]}"; do
    mv ${i}.bak ${i}
done

exit
