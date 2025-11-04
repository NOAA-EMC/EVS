#!/bin/ksh
#*************************************************************************************************
# Purpose:  Run headline prep job 
#             1. Further retrieve 500hPa Height from stored GEFS and CMCE analysis and member files
#                to form even smaller grib2 files 
#             2. Stored the even smaller grib files in prep/global_ens/headline.YYYYMMDD
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#******************************************************************************************
#
set -x

export WORK=$DATA

cd $WORK

export vday=$INITDATE

export run_mpi=${run_mpi:-'yes'}

#**************************************************************
export gefs_number=30

#get ensemble member data sequentially (non-mpi) or mpi run
#*************************************************************
$USHevs/${COMPONENT}/evs_get_gens_headline_data.sh
export err=$?; err_chk
