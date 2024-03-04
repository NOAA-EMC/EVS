#!/usr/bin/python

###############################################################
# This script defines and calls a function to create a        #
# blank performance diagram, as introduced in Roebber (2009). #
# Commented lines 64-68 provide the syntax for plotting text  #
# and markers on the diagram. This script is provided as is.  #
# Author: Dan Halperin                                        #
###############################################################

#Import necessary modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import subprocess
import os

#Function definition
def get_bias_label_position(bias_value, radius):
  x = np.sqrt(np.power(radius, 2)/(np.power(bias_value, 2)+1))
  y = np.sqrt(np.power(radius, 2) - np.power(x, 2))
  return (x, y)

def performance_diag():
  #INPUT file with CTC line 
  CTCfile01 = os.environ['CTCfile01']
  row = np.loadtxt(CTCfile01,dtype=str)
  total = float(row[24])
  hit = float(row[25])
  falsea = float(row[26])
  miss = float(row[27])
  POD = hit/(hit + miss)
  FAR = falsea/(hit + falsea)
  SUR = 1.0 - FAR
#  print(POD)
#  print(FAR)
#  print(SUR)
  POD1 = POD + 0.03

  CTCfile02 = os.environ['CTCfile02']
  xrow = np.loadtxt(CTCfile02,dtype=str)
  xtotal = float(xrow[24])
  xhit = float(xrow[25])
  xfalsea = float(xrow[26])
  xmiss = float(xrow[27])
  xPOD = xhit/(xhit + xmiss)
  xFAR = xfalsea/(xhit + xfalsea)
  xSUR = 1.0 - xFAR
  xPOD1 = xPOD + 0.03

  CTCfile03 = os.environ['CTCfile03']
  yrow = np.loadtxt(CTCfile03,dtype=str)
  ytotal = float(yrow[24])
  yhit = float(yrow[25])
  yfalsea = float(yrow[26])
  ymiss = float(yrow[27])
  yPOD = yhit/(yhit + ymiss)
  yFAR = yfalsea/(yhit + yfalsea)
  ySUR = 1.0 - yFAR
  yPOD1 = yPOD + 0.03

  #Output file name
  outf = "tcgen_performance_diagram.png"

  #Define figure, plot axis
  fig = plt.figure(figsize=(8,8))
  ax  = fig.add_axes([0.1, 0.1, 0.8, 0.8])

  #Define range for x, y; create 2D array of x, y values
  x     = np.arange(0,1.01,0.01)
  y     = np.arange(0,1.01,0.01)
  xi,yi = np.meshgrid(x, y)

  #Calculate bias and CSI; set contour levels
  bias    = yi/xi
  blevs   = [0.1, 0.25, 0.5, 0.75, 1, 1.25, 2.5, 5, 10]
  csi     = 1/( (1/xi) + (1/yi) - 1 )
  csilevs = np.arange(0.1,1,0.1)

  #The second way-Calculate bias and CSI; set contour levels
  grid_ticks = np.arange(0, 1.01, 0.01)
  sr_g, pod_g = np.meshgrid(grid_ticks, grid_ticks)
  biasp = pod_g / sr_g
#  csip = 1.0 / (1.0 / sr_g + 1.0 / pod_g - 1.0)
#  csi_cmap="Blues"
#  csi_contour = plt.contourf(sr_g, pod_g, csip, np.arange(0.1, 1.1, 0.1), extend="max", cmap=csi_cmap)
#  cbar = plt.colorbar(csi_contour)
#  csi_label="Critical Success Index"
#  cbar.set_label(csi_label, fontsize=14)

  bias_contour_vals = [0.1, 0.3, 0.6, 1., 1.5, 3., 10.]
  b_contour = plt.contour(sr_g, pod_g, biasp, bias_contour_vals,colors='gray', linestyles='--')
  plt.clabel(
      b_contour, fmt='%1.1f',
      manual=[
          get_bias_label_position(bias_value, .75)
          for bias_value in bias_contour_vals
      ]
  )

  #Axis labels, tickmarks
  ax.set_xlabel('Success Ratio (1 - False Alarm Ratio)',fontsize=12,fontweight='bold')
  ax.set_ylabel('Probability of Detection',fontsize=12,fontweight='bold')
  ax.set_xticks(np.arange(0,1.1,0.1))
  ax.set_yticks(np.arange(0,1.1,0.1))
  plt.setp(ax.get_xticklabels(),fontsize=13)
  plt.setp(ax.get_yticklabels(),fontsize=13)

  #Second y-axis for bias values < 1
#  ax2 = ax.twinx()
#  ax2.set_yticks(blevs[0:5])
#  plt.setp(ax2.get_yticklabels(),fontsize=13)

  #Axis labels for bias values > 1
#  ax.text(0.1,1.015,'10',fontsize=13,va='center',ha='center')
#  ax.text(0.2,1.015,'5',fontsize=13,va='center',ha='center')
#  ax.text(0.4,1.015,'2.5',fontsize=13,va='center',ha='center')
#  ax.text(0.8,1.015,'1.25',fontsize=13,va='center',ha='center')

  #Plot bias and CSI lines at specified contour intervals
#  cbias =  ax.contour(x,y,bias,blevs,colors='black',linewidths=1,linestyles='--')
  ccsi  =  ax.contour(x,y,csi,csilevs,colors='gray',linewidths=1,linestyles='-')
  plt.clabel(ccsi,csilevs,inline=True,fmt='%.1f',fontsize=10,colors='black')

  #Test/sample markers/text
  ax.plot(SUR,POD,marker='o',markersize=10,c='black')
#  ax.text(SUR,POD1,'GFS',fontsize=11,fontweight='bold',ha='center',va='center',color='black')

  ax.plot(xSUR,xPOD,marker='o',markersize=10,c='red')
#  ax.text(xSUR,xPOD1,'ECMWF',fontsize=11,fontweight='bold',ha='center',va='center',color='red')

  ax.plot(ySUR,yPOD,marker='o',markersize=10,c='blue')
#  ax.text(ySUR,yPOD1,'CMC',fontsize=11,fontweight='bold',ha='center',va='center',color='blue')

  ax.plot(0.3,0.95,marker='o',markersize=6,c='black')
  ax.text(0.35,0.95,'GFS',fontsize=6,fontweight='bold',ha='center',va='center',color='black')

  ax.plot(0.5,0.95,marker='o',markersize=6,c='red')
  ax.text(0.55,0.95,'ECMWF',fontsize=6,fontweight='bold',ha='center',va='center',color='red')

  ax.plot(0.7,0.95,marker='o',markersize=6,c='blue')
  ax.text(0.75,0.95,'CMC',fontsize=6,fontweight='bold',ha='center',va='center',color='blue')

#  title="Performance Diagram"
#  plt.title(title, fontsize=12, fontweight="bold")
  TCGENdays = os.environ['TCGENdays']
  plt.title(TCGENdays, fontsize=12, fontweight="bold")

  #Save, close, and trim whitespace around plot
#  plt.savefig(outf,pad_inches=0.01, orientation='landscape')
  plt.savefig(outf,dpi=160,bbox_inches='tight')
  plt.close()
#  subprocess.call("convert -trim "+outf+" "+outf, shell=True)

#Function call
performance_diag()

sys.exit()
