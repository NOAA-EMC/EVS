#!/bin/sh

MAILTO="mallory.row@noaa.gov"

case "$COMPONENT" in
    aigefs | global_chem | global_det | global_ens | rtofs | subseasonal | wafs)
        MAILTO+=",alicia.bentley@noaa.gov"
        ;;&
    analyses | aqm | cam | glwu | nwps)
        MAILTO+=",andrew.benjamin@noaa.gov"
        ;;&
    aigefs | global_ens)
        MAILTO+=",lichuan.chen@noaa.gov"
        ;;&
    analyses | glwu| nwps | rtofs)
        MAILTO+=",samira.ardani@noaa.gov"
        ;;&
    aqm | global_chem)
        MAILTO+=",ho-chun.huang@noaa.gov"
        ;;&
    cam)
        MAILTO+=",marcel.caron@noaa.gov"
        ;;&
    global_det)
        MAILTO+=",qi.shi@noaa.gov"
        ;;&
    subseasonal)
        MAILTO+=",shannon.shields@noaa.gov"
        ;;&
    wafs)
        MAILTO+=",yali.mao@noaa.gov"
        ;;&
esac

if [[ ${COMPONENT} = cam && ${RUN} = chem ]]; then
     MAILTO=${MAILTO//marcel.caron/ho-chun.huang}
fi

echo "Setting MAILTO to ${MAILTO}"
export MAILTO
