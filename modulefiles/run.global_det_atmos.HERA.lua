help([[
Load environment to run EVS global_det on Hera
]])

load(pathJoin("hpss", hpss_ver))

prepend_path("MODULEPATH", "/scratch2/NCEPDEV/nwprod/hpc-stack/libs/hpc-stack/modulefiles/stack")
load(pathJoin("hpc", hpc_ver))
load(pathJoin("hpc-intel", hpc_intel_ver))
load(pathJoin("hpc-impi", impi_ver))
load(pathJoin("hdf5", os.getenv("hdf5_ver")))
load(pathJoin("netcdf", os.getenv("netcdf_ver")))
load(pathJoin("nco", os.getenv("nco_ver")))
load(pathJoin("prod_util", os.getenv("prod_util_ver")))
load(pathJoin("grib_util", os.getenv("grib_util_ver")))
load(pathJoin("wgrib2", os.getenv("wgrib2_ver")))
load(pathJoin("cdo", os.getenv("cdo_ver")))
prepend_path("MODULEPATH", "/contrib/anaconda/modulefiles")
load(pathJoin("anaconda", os.getenv("anaconda_ver")))
prepend_path("MODULEPATH", "/contrib/met/modulefiles")
load(pathJoin("met", os.getenv("met_ver")))
prepend_path("MODULEPATH", "/contrib/METplus/modulefiles")
load(pathJoin("metplus", os.getenv("metplus_ver")))
