def get_date_info_title(date_type, valid_hours, init_hours,
                        start_date, end_date, verif_case):
    """! Get a formalized version of the
         verification date information to
         use in plot title

             Args:
                 date_type   - string of verification date
                               types: VALID or INIT
                 valid_hours - list of valid hours
                 init_hours  - list of initialzation hours
                 start_date  - string of verification
                               start date
                 end_date    - string of verification
                               end date
                 verif_case  - string of verification case
                               name
             Returns:
                 date_title - string of a formalized version
                              of the verification dates
                              to use in plot title
    """
    valid_hours_format = []
    for vh in valid_hours:
        valid_hours_format.append(vh[0:2]+'Z')
    valid_hours_title = ', '.join(valid_hours_format)
    init_hours_format = []
    for ih in init_hours:
        init_hours_format.append(ih[0:2]+'Z')
    init_hours_title = ', '.join(init_hours_format)
    if date_type == 'VALID':
        if verif_case == 'grid2obs':
            date_info_title = (
                date_type.lower()+' '+start_date+'-'+end_date+', '
                +init_hours_title+' cycles'
            )
        else:
            date_info_title = (
                date_type.lower()+' '+start_date+'-'+end_date+' '
                +valid_hours_title
            )
    elif date_type == 'INIT':
        if verif_case == 'grid2obs':
            date_info_title = (
                date_type.lower()+' '+start_date+'-'+end_date+', valid '
                +valid_hours_title
            )
        else:
            date_info_title = (
                date_type.lower()+' '+start_date+'-'+end_date+' '
                +init_hours_title
            )
    return date_info_title

def get_lead_title(lead_hour_str):
    """! Get a formalized version of the
         forecast lead to use in plot title

             Args:
                 lead - string of the forecast lead [hour]

             Returns:
                 lead_title - string of a formalized version
                              of the forecast lead
                              to use in plot title
    """
    lead_hour_float = float(lead_hour_str)
    lead_day_float = lead_hour_float/24.
    if lead_day_float.is_integer():
        lead_day_str = str(int(lead_day_float))
    else:
        lead_day_str = str(lead_day_float)
    lead_title = ('Forecast Day '+lead_day_str+' (Forecast Hour '
                  +lead_hour_str+')')
    return lead_title

def get_vx_mask_title(vx_mask):
    """! Get a formalized version of the
         verification vx_mask to use in plot title

             Args:
                 vx_mask - string of the verification
                          vx_mask abbrevation used for
                          MET

             Returns:
                 vx_mask_title - string of a formalized version
                                of the verification vx_mask
                                to use in plot title
    """
    vx_mask_title_dict = {
        'G002': 'Global',
        'NHX': 'Northern Hemisphere 20N-80N',   
        'SHX': 'Southern Hemisphere 20S-80S',
        'TRO': 'Tropics 20S-20N',
        'PNA': 'Pacific North America',
        'N60': '60N-90N',
        'S60': '60S-90S',
        'NPO': 'Northern Pacific Ocean',
        'SPO': 'Southern Pacific Ocean',
        'NAO': 'Northern Atlantic Ocean',
        'SAO': 'Southern Atlantic Ocean',
        'G003': 'Global',
        'NHM': 'Northern Hemisphere 20N-80N',
        'SHM': 'Southern Hemisphere 20S-80S',
        'TRP': 'Tropics 20S-20N',
        'NH': 'Northern Hemisphere 20N-90N',
        'SH': 'Southern Hemisphere 20S-90S',
        'G004': 'Global',
        'NHEM': 'Northern Hemisphere',
        'SHEM': 'Southern Hemisphere',
        'TROPICS': 'Tropics',
        'G236': 'CONUS - NCEP Grid 236',
        'G223': 'CONUS - NCEP Grid 223',
        'G104': 'NA - NCEP Grid 104',
        'CONUS': 'CONUS',
        'POLAR': 'Polar 60-90 N/S',
        'ARCTIC': 'Arctic',
        'EAST': 'Eastern US',
        'WEST': 'Western US',
        'NWC': 'Northwest Coast',
        'SWC': 'Southwest Coast',
        'NMT': 'Northern Mountain Region',
        'GRB': 'Great Basin',
        'SMT': 'Southern Mountain Region',
        'SWD': 'Southwest Desert',
        'NPL': 'Northern Plains',
        'SPL': 'Southern Plains',
        'MDW': 'Midwest',
        'LMV': 'Lower Mississippi Valley',
        'APL': 'Appalachians',
        'NEC': 'Northeast Coast',
        'SEC': 'Southeast Coast',
        'GMC': 'Gulf of Mexico Coast',
        'HWI': 'Hawaii',
        'NAK': 'Northern Alaska',
        'SAK': 'Southern Alaska',
        'G216': 'Alaska - NCEP Grid 216',
        'G211': 'CONUS - NCEP Grid 211',
        'SEA_ICE': 'Global - Sea Ice',
        'SEA_ICE_FREE': 'Global - Sea Ice Free',
        'SEA_ICE_POLAR': 'Polar - Sea Ice',
        'SEA_ICE_FREE_POLAR': 'Polar - Sea Ice Free'
    }
    if vx_mask in list(vx_mask_title_dict.keys()):
        vx_mask_title = vx_mask_title_dict[vx_mask]
    else:
        vx_mask_title = vx_mask
    return vx_mask_title

def get_var_info_title(var_name, var_level, var_extra, var_thresh):
    """! Get a formalized version of the
         variable information to use in plot title

             Args:
                 var_name   - string of the variable GRIB name
                 var_level  - string of the variable level used
                              in MET
                 var_extra  - string of extra variable information
                              if none it is an empty string
                 var_thresh - string of variable threshold
                              if none it is an empty string

             Returns:
                 var_info_title - string of a formalized version
                                  of the variable information
                                  to use in plot title
    """
    # Build variable name title
    var_name_title_dict = {
        'HGT': 'Geopotential Height',
        'HGT_WV1_0-3': 'Geopotential Height: Waves 0-3',
        'HGT_WV1_4-9': 'Geopotential Height: Waves 4-9',
        'HGT_WV1_10-20': 'Geopotential Height: Waves 10-20',
        'HGT_WV1_0-20': 'Geopotential Height: Waves 0-20',
        'PRES': 'Pressure',
        'TMP': 'Temperature',
        'UGRD': 'Zonal Wind',
        'VGRD': 'Meridional Wind',
        'UGRD_VGRD': 'Vector Wind',
        'PRMSL': 'Pressure Reduced to MSL',
        'O3MR': 'Ozone Mixing Ratio',
        'RH': 'Relative Humidity',
        'SPFH': 'Specific Humidity',
        'HPBL': 'Planetary Boundary Layer Height',
        'WEASD': 'Accum. Snow Depth Water Equiv.',
        'TSOIL': 'Soil Temperature',
        'SOILW': 'Volumetric Soil Moisture Content',
        'CWAT': 'Cloud Water',
        'PWAT': 'Precipitable Water',
        'TOZNE': 'Total Ozone',
        'DPT': 'Dewpoint Temperature',
        'TCDC': 'Total Cloud Cover',
        'VIS': 'Visibility',
        'GUST': 'Wind Gust',
        'APCP_24': '24 hour Accumulated Precipitation',
        'TMP_Z0_mean': 'Temperature',
        'ICEC_Z0_mean': 'Sea Ice Concentration'
    }
    if var_name in list(var_name_title_dict.keys()):
        var_name_title = var_name_title_dict[var_name]
    else:
        var_name_title = var_name
    # Build variable level title
    if 'P' in var_level:
        var_level_title = var_level.replace('P', '')+' hPa'
    elif 'Z' in var_level:
        if var_level == 'Z0':
            var_level_title = 'Surface'
        else:
            if var_name in ['TSOIL', 'SOILW']:
                var_level_title = var_level.replace('Z', '')+' centimeter'
            else:
                var_level_title = var_level.replace('Z', '')+' meter'
    elif 'L' in var_level:
        var_level_title = ''
    elif 'A' in var_level:
         var_level_title = ''
    elif var_level == 'all':
         var_level_title = ''
    else:
         var_level_title = var_level
    # Build variable extra info. title
    if var_extra == '':
        var_extra_title = ''
    elif 'GRIBlvltyp' in var_extra:
        if '7' in var_extra:
            var_extra_title = 'Tropopause'
        elif '200' in var_extra:
            var_extra_title = 'Entire Atmosphere'
        elif '215' in var_extra:
            var_extra_title = 'Cloud Ceiling'
    else:
        var_extra_title = var_extra
    # Build variable threshold title
    if var_thresh == '':
        var_thresh_title = ''
    elif var_thresh == 'all':
        var_thresh_title = ''
    else:
        var_thresh_title = var_thresh
    # Need to do some special formatting
    if 'P' in var_level:
        var_info_title = var_level_title+' '+var_name_title
        if var_extra_title != '':
            var_info_title = var_info_title+' '+var_extra_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    elif 'Z' in var_level:
        if var_name in ['PRMSL', 'WEASD', 'CAPE']:
            var_info_title = var_name_title
        else:
            var_info_title = var_level_title+' '+var_name_title
        if var_extra_title != '':
            var_info_title = var_info_title+' '+var_extra_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    elif 'L' in var_level:
        if var_name in ['HPBL', 'CWAT', 'PWAT', 'TOZONE', 'TCDC']:
            var_info_title = var_name_title
        elif var_name == 'HGT' and '215' in var_extra:
            var_info_title = var_extra_title
        else:
            var_info_title = var_extra_title+' '+var_name_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    elif 'A' in var_level:
        var_info_title = var_name_title
        if var_extra_title != '':
            var_info_title = var_info_title+' '+var_extra_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    elif var_level == 'all':
        var_info_title = var_name_title
        if var_extra_title != '':
            var_info_title = var_info_title+' '+var_extra_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    else:
        var_info_title = var_name_title+' '+var_level_title
        if var_extra_title != '':
            var_info_title = var_info_title+' '+var_extra_title
        if var_thresh_title != '':
            var_info_title = var_info_title+' '+var_thresh_title
    return var_info_title
