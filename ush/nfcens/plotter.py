#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, PathPatch
from matplotlib.path import Path
import numpy as np

class Plotter():
    def __init__(self, font_weight='bold',   axis_title_weight='bold',  
                axis_title_size=20,         axis_offset=False,
                axis_title_pad=15,          axis_label_weight='bold',  
                axis_label_size=16,         axis_label_pad=10,
                xtick_label_size=16,        xtick_major_pad=10,        
                ytick_label_size=16,        ytick_major_pad=10, 
                fig_subplot_right=.95,      fig_subplot_left=.1,      
                fig_subplot_top=.925,       fig_subplot_bottom=.075,
                legend_handle_text_pad=.25, legend_handle_length=1.25, 
                legend_border_axis_pad=0,   legend_col_space=1.,
                legend_frame_on=True,       fig_size=(14.,14.),        
                legend_bbox=(0,1),          legend_font_size=17, 
                legend_loc='center right',  legend_ncol=1,             
                title_loc='center'):
        self.font_weight = font_weight
        self.axis_title_weight = axis_title_weight
        self.axis_title_size = axis_title_size
        self.axis_title_pad = axis_title_pad
        self.axis_offset = axis_offset
        self.axis_label_weight = axis_label_weight
        self.axis_label_size = axis_label_size
        self.axis_label_pad = axis_label_pad
        self.xtick_label_size = xtick_label_size
        self.xtick_major_pad = xtick_major_pad
        self.ytick_label_size = ytick_label_size
        self.ytick_major_pad = ytick_major_pad
        self.fig_subplot_right = fig_subplot_right
        self.fig_subplot_left = fig_subplot_left
        self.fig_subplot_top = fig_subplot_top
        self.fig_subplot_bottom = fig_subplot_bottom
        self.legend_handle_text_pad = legend_handle_text_pad
        self.legend_handle_length = legend_handle_length
        self.legend_border_axis_pad = legend_border_axis_pad
        self.legend_col_space = legend_col_space
        self.legend_frame_on = legend_frame_on
        self.fig_size = fig_size
        self.legend_bbox = legend_bbox
        self.legend_fontsize = legend_font_size
        self.legend_loc = legend_loc
        self.legend_ncol = legend_ncol
        self.title_loc = title_loc

    def set_up_plots(self):
        plt.rcParams['font.weight'] = self.font_weight
        plt.rcParams['axes.titleweight'] = self.axis_title_weight
        plt.rcParams['axes.titlesize'] = self.axis_title_size
        plt.rcParams['axes.titlepad'] = self.axis_title_pad
        plt.rcParams['axes.labelweight'] = self.axis_label_weight
        plt.rcParams['axes.labelsize'] = self.axis_label_size
        plt.rcParams['axes.labelpad'] = self.axis_label_pad
        plt.rcParams['axes.formatter.useoffset'] = self.axis_offset
        plt.rcParams['xtick.labelsize'] = self.xtick_label_size
        plt.rcParams['xtick.major.pad'] = self.xtick_major_pad
        plt.rcParams['ytick.labelsize'] = self.ytick_label_size
        plt.rcParams['ytick.major.pad'] = self.ytick_major_pad
        plt.rcParams['figure.subplot.left'] = self.fig_subplot_left
        plt.rcParams['figure.subplot.right'] = self.fig_subplot_right
        plt.rcParams['figure.subplot.top'] = self.fig_subplot_top
        plt.rcParams['figure.subplot.bottom'] = self.fig_subplot_bottom
        plt.rcParams['legend.handletextpad'] = self.legend_handle_text_pad
        plt.rcParams['legend.handlelength'] = self.legend_handle_length
        plt.rcParams['legend.borderaxespad'] = self.legend_border_axis_pad
        plt.rcParams['legend.columnspacing'] = self.legend_col_space
        plt.rcParams['legend.frameon'] = self.legend_frame_on
      
    def get_plots(self, num):
        fig, ax = plt.subplots(1, 1, figsize=self.fig_size, num=num)
        return fig, ax

    def get_error_boxes(self, xdata, ydata, xerror, yerror, fc='None', 
                       ec='black', lw=1., ls='solid', alpha=0.75):
        errorboxes = []
        xerror = np.array(xerror)
        yerror = np.array(yerror)
        for xc, yc, xe, ye in zip(xdata, ydata, xerror.T, yerror.T):
            rect = Rectangle((xc+xe[0], yc+ye[0]), np.diff(xe), np.diff(ye))
            errorboxes.append(rect)
        pc = PatchCollection(
            errorboxes, facecolor=fc, alpha=alpha, edgecolor=ec, linewidth=lw, 
            linestyle=ls
        )
        return pc

    def get_error_brackets(self, xdata, ydata, xerror, yerror, fc='None', 
                          ec='black', lw=1., alpha=0.75):
        errorbrackets = []
        verts = []
        codes = []
        xerror = np.array(xerror)
        yerror = np.array(yerror)
        for xc, yc, xe, ye in zip(xdata, ydata, xerror.T, yerror.T):
            verts += [
                (xc+xe[1], yc+ye[0]),
                (xc+xe[0], yc+ye[0]),
                (xc+xe[0], yc+ye[1]),
                (xc+xe[1], yc+ye[1])
            ]
            codes += [
                Path.MOVETO,
                Path.LINETO,
                Path.LINETO,
                Path.LINETO,
            ]
        path = Path(verts, codes)
        pp = PathPatch(
            path, facecolor=fc, alpha=alpha, edgecolor=ec, linewidth=lw
        )
        return pp

    def get_logo_location(self, position, x_figsize, y_figsize, dpi):
        """! Get locations for the logos

            Args:
                position  - side of image (string, "left" or "right")
                x_figsize - image size in x direction (float)
                y_figsize - image size in y_direction (float)
                dpi       - image dots per inch (float)

            Returns:
                x_loc - logo position in x direction (float)
                y_loc - logo position in y_direction (float)
                alpha - alpha value (float)
        """
        alpha = 0.5
        if x_figsize == 8 and y_figsize == 6:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.858
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.9
                y_loc = y_figsize * dpi * 0.858
        elif x_figsize == 16 and y_figsize == 8:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.89
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.89
        elif x_figsize == 16 and y_figsize == 16:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.945
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.945
        else:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.95
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.95
        return x_loc, y_loc, alpha



