#!/bin/ksh
#################################################################
# Script Name: verf_g2g_reflt.sh.sms $vday $vcyc
# Purpose:   To run grid-to-grid verification on reflectivity
#
# Log History:  Julia Zhu -- 2010.04.28 
################################################################
set -x

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export PRECIP_CONF=$PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS


$USHevs/mesoscale/evs_sref_precip.sh 


exit 
