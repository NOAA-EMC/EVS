##Python script to plot TC genesis HITS

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

domain = "eastpac"
if(domain == "eastpac"):
    ax = plt.axes(projection=ccrs.Miller(central_longitude=-60.0))
#    ax.set_extent([180, 290, 0, 60], crs=ccrs.PlateCarree())
    ax.set_extent([180, 290, 0, 50], crs=ccrs.PlateCarree())
##PLS NOTE THAT THE ax_extent is diff from tick marks and that is by design
    xticks = [-70, -80, -90, -100, -110, -120, -130, -140, -150, -160, -170, -180]
#    yticks = [ 0, 10, 20, 30, 40, 50, 60]
    yticks = [ 0, 10, 20, 30, 40, 50]
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
#    plt.annotate("50N " , (0,0), (-15,180), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("40N " , (0,0), (-15,140), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("30N " , (0,0), (-15,104), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("20N " , (0,0), (-15,69), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("10N " , (0,0), (-15,35), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)

    plt.annotate("80W " , (0,0), (318,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("90W " , (0,0), (286,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("100W " , (0,0), (250,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("110W " , (0,0), (218,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("120W " , (0,0), (185,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("130W " , (0,0), (152,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("140W " , (0,0), (119,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("150W " , (0,0), (87,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("160W " , (0,0), (55,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)
    plt.annotate("170W " , (0,0), (23,-5), xycoords='axes fraction', textcoords='offset points', va='top', color='Black', fontsize=6.5)

###############END OF AREAS##################################
    hitfile = os.environ['hitfile']
    hits  = np.loadtxt(hitfile,dtype=str)

    numhits = 0
    numhits = numhits + len(hits)
    #Plot each hit event
    for i in range(len(hits)):
      lat  = float(hits[i,31])
      lon  = float(hits[i,32]) + 360.
      print(lat)
      print(lon)
      plt.scatter(lon, lat,transform=ccrs.PlateCarree(), marker='o', color='green',s=12, facecolor='none')

    falsefile = os.environ['falsefile']
    fals  = np.loadtxt(falsefile,dtype=str)
    numfals = 0
    numfals = numfals + len(fals)
    #Plot each fals event
    for i in range(len(fals)):
      lat1  = float(fals[i,31])
      lon1  = float(fals[i,32]) + 360.
      plt.scatter(lon1, lat1,transform=ccrs.PlateCarree(), marker='s', color='red',s=12, facecolor='none')

    plt.scatter(185, 47,transform=ccrs.PlateCarree(), marker='o', color='green',s=12, facecolor='none')
    plt.scatter(185, 45,transform=ccrs.PlateCarree(), marker='s', color='red',s=12, facecolor='none')
    plt.annotate("Hits ("+str(numhits)+")", (0,0), (20,168), xycoords='axes fraction', textcoords='offset points', va='top', color='Green', fontsize=6.5)
    plt.annotate("False alarms ("+str(numfals)+")", (0,0), (20,160), xycoords='axes fraction', textcoords='offset points', va='top', color='Red', fontsize=6.5)

#    plt.title(f"East Pacific TC Genesis Hits")
    TCGENdays = os.environ['TCGENdays']
    plt.title(TCGENdays)
####################################################################
##The plt is saved as png and converted to gif in the bash script.

plt.savefig('TC_genesis.png', dpi=160,bbox_inches='tight')

exit
    # ----------------------------

