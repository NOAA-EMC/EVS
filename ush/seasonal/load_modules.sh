#!/bin/ksh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC VERIFICATION SYSTEM
##
## CONTRIBUTORS: Shannon Shields, Shannon.Shields@noaa.gov, NCEP/EMC-VPPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: load_modules.sh"

## Check versions are supported in evs
if [[ "$MET_version" =~ ^(10.1.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in evs"
    exit 1
fi
if [[ "$METplus_version" =~ ^(4.1.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in evs"
    exit 1
fi

## Load
if [ $machine = WCOSS_C ]; then
    module purge
    export HPC_OPT=/apps/ops/para/libs
    module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304/
    module load craype/2.7.10
    if [ $MET_version = 10.1.1 ]; then
        module load met/10.1.1
        export HOMEMET="/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1"
        export HOMEMET_bin_exec="exec"
	export PATH=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/bin:${PATH}
	export MET_BASE=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/share/met
	export MET_ROOT=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 4.1.1 ]; then
        module load metplus/4.1.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    #module load alps
    module load envvar/1.0
    module load PrgEnv-intel/8.1.0
    #module load xt-lsfhpc/9.1.3
    #module load cfp-intel-sandybridge/1.1.0
    module load cfp/2.0.4
    #module load hpss/4.1.0.3
    module load prod_util/2.0.12
    module load grib_util/1.2.3
    module load wgrib2/2.0.8
    #module load nco-gnu-sandybridge/4.4.4
    module load nco/4.7.9
    #module unload python/3.6.3
    #module unuse /usrx/local/prod/modulefiles
    #module use /usrx/local/dev/modulefiles
    #module load NetCDF-intel-sandybridge/4.5.0
    module load intel
    module load gsl
    module load cray-mpich/8.1.9
    module load cray-pals/1.1.3
    module load netcdf/4.7.4
    module load python/3.8.6
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module load intel/18.0.5.274
    module use /contrib/anaconda/modulefiles
    module load anaconda/latest
    if [ $MET_version = 10.1.1 ]; then
        module use /contrib/met/modulefiles
        module load met/10.1.1
        export HOMEMET="/contrib/met/10.1.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 4.1.1 ]; then
        module use /contrib/METplus/modulefiles
        module load metplus/4.1.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load impi/2018.4.274
    module load hpss/hpss
    module load netcdf/4.6.1
    module load nco/4.9.1
    module use /scratch2/NCEPDEV/nwprod/NCEPLIBS/modulefiles
    module load prod_util/1.1.0
    module load grib_util/1.1.1
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    module load slurm/19.05.3-2
    module load contrib
    module load intel/2020
    module load intelpython3/2020
    if [ $MET_version = 9.1 ]; then
        module load met/9.1
        export HOMEMET="/apps/contrib/MET/9.1"
        export HOMEMET_bin_exec="bin"
    else
        "ERROR: $MET_version is not supported on $machine"
        exit 1
    fi
    if [ $METplus_version = 3.1 ]; then
        module use /apps/contrib/modulefiles
        module load metplus/3.1
        export HOMEMETplus="${METPLUS_PATH}"
    else
        "ERROR: $METplus_version is not supported on $machine"
        exit 1
    fi
    module load impi/2020
    module load netcdf/4.7.2
    module load nco/4.9.3
    module use /apps/contrib/NCEPLIBS/orion/modulefiles
    module use /apps/contrib/NCEPLIBS/lib/modulefiles
    module load grib_util/1.2.0
    module load prod_util/1.2.0
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
if [ $machine != "ORION" ]; then
    export RM=`which rm`
    export CUT=`which cut`
    export TR=`which tr`
    export NCAP2=`which ncap2`
    export CONVERT=`which convert`
    export NCDUMP=`which ncdump`
    export HTAR=`which htar`
fi
if [ $machine = "ORION" ]; then
    export RM=`which rm | sed 's/rm is //g'`
    export CUT=`which cut | sed 's/cut is //g'`
    export TR=`which tr | sed 's/tr is //g'`
    export NCAP2=`which ncap2 | sed 's/ncap2 is //g'`
    export CONVERT=`which convert | sed 's/convert is //g'`
    export NCDUMP=`which ncdump | sed 's/ncdump is //g'`
    export HTAR="/null/htar"
fi
echo "Using HOMEMET=${HOMEMET}"
echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: load_modules.sh"

module list
