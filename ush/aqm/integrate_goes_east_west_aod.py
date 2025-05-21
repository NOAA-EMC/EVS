import sys
import datetime
import os
import netCDF4 as nc
import numpy as np

if len(sys.argv) < 3:
    print(f"you must set 3 arguments as goes_east_aod_file goes_east_aod_file output_fuse_aod_file")
    sys.exit()
else:
    python_code   = sys.argv[0]
    goes_east_aod = sys.argv[1]
    goes_west_aod = sys.argv[2]
    output_file   = sys.argv[3]

flag_info=False
if flag_info:
    print(f"GOES_EAST Input :{goes_east_aod}")
    print(f"GOES_WEST Input :{goes_west_aod}")
    print(f"MERGED Output   :{output_file}")

goes_east=os.environ['GOES_EAST']
goes_west=os.environ['GOES_WEST']
GOES_EAST=goes_east.upper()
GOES_WEST=goes_west.upper()

if os.path.exists(goes_east_aod) and os.path.exists(goes_west_aod):
    with nc.Dataset(goes_east_aod,"r") as srce, nc.Dataset(goes_west_aod,"r") as srcw, nc.Dataset(output_file,"w") as dst1:
        late=srce.variables["lat"][:,:]
        lone=srce.variables["lon"][:,:]
        aode=srce.variables["AOD"][:,:]

        latw=srcw.variables["lat"][:,:]
        lonw=srcw.variables["lon"][:,:]
        aodw=srcw.variables["AOD"][:,:]

        imax=aode.shape[0]
        jmax=aode.shape[1]

        aodm=np.empty((imax,jmax))
        fill_value_read=srce.variables["AOD"].getncattr("_FillValue")

        aode=np.ma.filled(aode,fill_value_read)
        aodw=np.ma.filled(aodw,fill_value_read)

        ## Join GOES-East and GOES-West AOD
        ## Use arithmetic mean when both satellites have non-filled_value,
        ## use the non-filled_value if only one sattllite has filled_value, and
        ## use filled_value if both satellites have filled_value.

        for i in range(0, imax-1):
            for j in range(0, jmax-1):
                east=aode[i][j]
                west=aodw[i][j]
                if east != fill_value_read and west != fill_value_read:
                    aodm[i][j]=0.5*(east+west)
                elif east != fill_value_read and west == fill_value_read:
                    aodm[i][j]=east
                elif east == fill_value_read and west != fill_value_read:
                    aodm[i][j]=west
                else:
                    aodm[i][j]=fill_value_read
        mask = aodm == fill_value_read
        aodm=np.ma.masked_array(aodm,mask)

        ## Copy global attribtes
        for attr_name in srce.ncattrs():
            if attr_name == "FileOrigins":
                olddesc=srce.getncattr(attr_name)
                newdesc=f"Merged {goes_east_aod} and {goes_west_aod} by {python_code}"
                dst1.setncattr(attr_name,newdesc)
            else:
                dst1.setncattr(attr_name,srce.getncattr(attr_name))
        ## Copy dimensions
        for name, dim in srce.dimensions.items():
            dst1.createDimension(name, len(dim) if not dim.isunlimited() else None)
        ## Copy variables
        for name, var in srce.variables.items():
            if name == "AOD":
                dst1.createVariable(name, var.dtype, var.dimensions,  fill_value = fill_value_read )
            else:
                dst1.createVariable(name, var.dtype, var.dimensions)
            ## Copy variable attribtes
            for attr_name in var.ncattrs():
                if attr_name == "orbital_slot":
                    olddesc=var.getncattr(attr_name)
                    newdesc=olddesc.replace("East","Join-East-West")
                    dst1.variables[name].setncattr(attr_name,newdesc)
                elif attr_name == "platform_ID":
                    olddesc=var.getncattr(attr_name)
                    newdesc=olddesc.replace(GOES_EAST,f"{GOES_EAST}/{GOES_WEST}")
                    dst1.variables[name].setncattr(attr_name,newdesc)
                elif attr_name == "dataset_name":
                    olddesc=var.getncattr(attr_name)
                    newdesc=olddesc.replace(GOES_EAST,f"{GOES_EAST}/{GOES_WEST}")
                    dst1.variables[name].setncattr(attr_name,newdesc)
                elif attr_name != "_FillValue":
                    dst1.variables[name].setncattr(attr_name,var.getncattr(attr_name))
            if name != "AOD":
                dst1.variables[name][:] = srce.variables[name][:]
            else:
                dst1.variables[name][:] = aodm
else:
    if not os.path.exists(goes_east_aod):
        print(f"Can not find {goes_east_aod}")
    if not os.path.exists(goes_west_aod):
        print(f"Can not find {goes_west_aod}")
    print("Skip the generation of fused AOD files")
