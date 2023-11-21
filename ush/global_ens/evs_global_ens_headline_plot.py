#! /usr/bin/env python3
#*******************************************************************************
# Purose: generate GEFS headline ACC plot 
#          
#  Note: This script first read 3 text files that conain the yearly averaged
#        forecast hour ~ ACC data for GEFS, NAEFS and GFS, respectively 
#        Then generate the headline plot
#
#   Last update: 11/16/2023  by Binbin Zhou (Lynker@NCPE/EMC)
#***************************************************************

# library to get a directory listing

import glob

#from mpl_toolkits.basemap import Basemap, cm

import os

import matplotlib as mpl

# from mpl_toolkits.basemap import Basemap

from matplotlib import pyplot

import matplotlib.pyplot as plt

import numpy as np

#from pyhdf.SD import SD, SDC

#import h5py as h5py

from netCDF4 import Dataset

from scipy import stats

import math

import netCDF4 as nc

import sys

import os

gfs_scores = np.ones((16))
gefs_scores = np.ones((16))
naefs_scores = np.ones((16))

fcst_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
ac_scores = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
days_x = np.arange(len(fcst_days))
scores_y = np.arange(len(ac_scores))

gfs_scores_fname= 'GFS_500HGT_NH_PAC_YYYY.txt'
gefs_scores_fname= 'GEFS_500HGT_NH_PAC_YYYY.txt'
naefs_scores_fname= 'NAEFS_500HGT_NH_PAC_YYYY.txt'

text_file1 = open(gfs_scores_fname, "r")
text_file2 = open(gefs_scores_fname, "r")
text_file3 = open(naefs_scores_fname, "r")

for i in range(0, 16):

    gfs_scores[i] = text_file1.readline()
    gefs_scores[i] = text_file2.readline()
    naefs_scores[i] = text_file3.readline()

print ("GFS Scores Input:")
print (gfs_scores)
print ("GEFS Scores Input:")
print (gefs_scores)
print ("NAEFS Scores Input:")
print (naefs_scores)

fig = plt.figure(figsize=(11, 6))
width = 0.25
plt.rcParams['font.weight'] = 'bold'
plt.bar(days_x - width, gfs_scores, color = 'royalblue', width = width, label ="GFS")
plt.bar(days_x, gefs_scores, color = 'red', width = width, label ="GEFS")
plt.bar(days_x + width, naefs_scores, color = 'limegreen', width = width, label ="NAEFS")
#plt.grid(axis='y')
#plt.legend(loc = 'upper right')
#plt.legend(loc = 'Best')
plt.legend()
plt.title('NH Anomaly Correlation for 500hPa Height\n', weight= 'bold', fontsize=16)
#plt.suptitle('(Period: January 1st YYYY - December 31st YYYY)\n', fontsize=10)
#plt.text(7.5, 1.02, '(Period: January 1st - December 31st YYYY)', fontsize=12, ha='center',weight= 'bold')
plt.text(7.5, 1.02, '(Period: FIRST - LAST )', fontsize=12, ha='center',weight= 'bold')
plt.xlabel('Forecast Leading Time (Days)', weight= 'bold', fontsize=12)
plt.ylabel('Anomaly Correlation', weight= 'bold', fontsize=12)
plt.xticks(days_x, fcst_days, weight= 'bold', fontsize=11)
plt.ylim ([0, 1])
plt.yticks(ac_scores, weight= 'bold', fontsize=11)
plt.grid(axis='y', linestyle='-', linewidth='0.1', color='black')
plt.show()
figure_name='NH_H500_PAC_YYYY'
pngfile = "{0}.png".format(figure_name)
fig.savefig(pngfile)
