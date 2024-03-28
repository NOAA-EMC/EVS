##Python script to plot TC genesis/HITS

from __future__ import print_function

#import tkinter as tk
import os
import sys
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ast import literal_eval
import ast
import datetime
import matplotlib.path as mpath
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
from cartopy.feature import GSHHSFeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.feature as cfeature

cartopyDataDir = os.environ['cartopyDataDir']
cartopy.config['data_dir'] = cartopyDataDir

# RE -------------------
#Initialize the empty Plot (only need to call the figure to write the map.)
fig = plt.figure()

###FOR THE INTERSTED DOMAIN PART###############
##e.g Alaska, CONUS etc
## Map proj are different for different areas. 
domain = "atlantic"
if(domain == "atlantic"):
    ax = plt.axes(projection=ccrs.Miller(central_longitude=-55.0))
#    ax.set_extent([260, 370, -5, 65], crs=ccrs.PlateCarree())
    ax.set_extent([260, 370, -5, 50], crs=ccrs.PlateCarree())

##PLS NOTE THAT THE ax_extent is diff from tick marks and that is by design
    xticks = [-130, -120, -110, -100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10]
#    yticks = [-5, 0, 10, 20, 30, 40, 50, 60, 65]
    yticks = [-5, 0, 10, 20, 30, 40, 50]
    ax.gridlines(xlocs=xticks, ylocs=yticks,color='gray', alpha=0.9, linestyle='--')
###Add topography, lakes, borders etc
    ax.coastlines('10m',linewidth=0.30, color='black')
    ax.add_feature(cfeature.GSHHSFeature('low', levels=[2],
                                         facecolor='white'), color='black', linewidth=0.1)
    land_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                           edgecolor='face',
                                           facecolor='None')
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(land_10m)

########This part is a roundabout
###for the known issues with
###cartopy LCC/Northpolarstero projection.
    plt.annotate("0 " , (0,0), (-6,18), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("10N " , (0,0), (-15,52), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("20N " , (0,0), (-15,85), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("30N " , (0,0), (-15,120), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("40N " , (0,0), (-15,157), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
#    plt.annotate("50N " , (0,0), (-15,198), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
#    plt.annotate("60N " , (0,0), (-15,245), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)

    plt.annotate("90W " , (0,0), (27,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("80W " , (0,0), (60,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("70W " , (0,0), (92,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("60W " , (0,0), (125,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("50W " , (0,0), (157,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("40W " , (0,0), (189,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("30W " , (0,0), (220,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("20W " , (0,0), (253,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("10W " , (0,0), (286,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("0 "   , (0,0), (323,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)

######################atlantic##################################################
#    falsefile="tc_gen_2021_genmpr_FYOY.txt"
#    hits    = np.loadtxt(falsefile,dtype=str)
    falsefile = os.environ['falsefile']
    hits  = np.loadtxt(falsefile,dtype=str)

    numhits = 0
    numhits = numhits + len(hits)
    #Plot each hit event
    for i in range(len(hits)):
      lat  = float(hits[i,31])
      lon  = float(hits[i,32]) + 360.
      print(lat)
      print(lon)
      plt.scatter(lon, lat,transform=ccrs.PlateCarree(), marker='s', color='red',s=12, facecolor='none')

    plt.scatter(346, 47,transform=ccrs.PlateCarree(), marker='s', color='red',s=12, facecolor='none')
    plt.annotate("False alarms ("+str(numhits)+")", (0,0), (286,185), xycoords='axes fraction', textcoords='offset points', va='top', color='Red', fontsize=6.5)

#    plt.title(f"Atlantic TC Genesis False Alarms")
    TCGENdays = os.environ['TCGENdays']
    plt.title(TCGENdays)
####################################################################
##The plt is saved as png and converted to gif in the bash script.

plt.savefig('TC_genesis.png', dpi=160,bbox_inches='tight')

exit
    # ----------------------------

