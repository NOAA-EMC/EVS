#!/bin/bash
for file in lead_average.py  performance_diagram.py roc_curve.py stat_by_level.py threshold_average.py time_series.py valid_hour_average.py ; do
  sed -e "s!b=True!visible=True!g" $file > a
  mv a $file
done
