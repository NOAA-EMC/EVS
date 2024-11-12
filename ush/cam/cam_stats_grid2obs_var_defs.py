#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_stats_grid2obs_var_defs.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Configurations for each variable that will be processed by MET
#
# =============================================================================

generate_stats_jobs_dict = {
    'HGT': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'HGT',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'TMP': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'UGRD_VGRD': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'NONE',
                'VL1L2': 'STAT',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'UGRD': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'VGRD': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P400, "
                                     + "P300, P250, P200'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P400, "
                                    + "P300, P250, P200'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'SPFH': {
        'raob': {
            'hrrr': {
                'var1_fcst_name': 'SPFH',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
                'var1_obs_name': 'SPFH',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
            },
            'namnest': {
                'var1_fcst_name': 'SPFH',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P75, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
                'var1_obs_name': 'SPFH',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P75, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
            },
            'rrfs': {
                'var1_fcst_name': 'SPFH',
                'var1_fcst_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                     + "P850, P825, P800, P775, P750, P725, "
                                     + "P700, P675, P650, P625, P600, P575, "
                                     + "P550, P525, P500, P475, P450, P425, "
                                     + "P400, P375, P350, P325, P300, P275, "
                                     + "P250, P225, P200, P175, P150, P125, "
                                     + "P100, P70, P50, P30, P20, P10'"),
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
                'var1_obs_name': 'SPFH',
                'var1_obs_levels': ("'P1000, P975, P950, P925, P900, P875, "
                                    + "P850, P825, P800, P775, P750, P725, "
                                    + "P700, P675, P650, P625, P600, P575, "
                                    + "P550, P525, P500, P475, P450, P425, "
                                    + "P400, P375, P350, P325, P300, P275, "
                                    + "P250, P225, P200, P175, P150, P125, "
                                    + "P100, P70, P50, P30, P20, P10'"),
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"g/kg\\"; convert(x)=x*1000',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'HPBL': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'GRIB_lvl_typ = 220; set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'GRIB_lvl_typ = 220; set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'GRIB_lvl_typ = 220; set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'HPBL',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'HPBL',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'HPBL',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'le500,ge2000',
                'var1_fcst_options': 'set_attr_level = \\"PBL\\"',
                'var1_obs_name': 'HPBL',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'le500,ge2000',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'SBCAPE': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hrrr': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'namnest': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'rrfs': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ >0 ];',
                'var1_obs_name': 'CAPE',
                'var1_obs_levels': 'L0-100000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = UNION;',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'MLCAPE': {
        'raob': {
            'hireswarw': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'hrrr': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'namnest': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = INTERSECTION;',
            },
            'rrfs': {
                'var1_fcst_name': 'CAPE',
                'var1_fcst_levels': 'P0-90',
                'var1_fcst_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_fcst_options': 'cnt_thresh = [ >0 ];',
                'var1_obs_name': 'MLCAPE',
                'var1_obs_levels': 'L0-90000',
                'var1_obs_thresholds': 'ge250,ge500,ge1000,ge1500,ge2000,ge3000,ge4000',
                'var1_obs_options': 'cnt_thresh = [ >0 ]; cnt_logic = UNION;',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'TMP2m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'TMP',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'TMP',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'UGRD10m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'VGRD10m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'VGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'VGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'UGRD_VGRD10m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'UGRD',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var2_fcst_name': 'VGRD',
                'var2_fcst_levels': 'Z10',
                'var2_fcst_thresholds': '',
                'var2_fcst_options': '',
                'var1_obs_name': 'UGRD',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
                'var2_obs_name': 'VGRD',
                'var2_obs_levels': 'Z10',
                'var2_obs_thresholds': '',
                'var2_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'NONE',
                'VL1L2': 'STAT',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'WIND10m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'WIND',
                'var1_fcst_levels': 'Z10',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'WIND',
                'var1_obs_levels': 'Z10',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'GUSTsfc': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'GUST',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': '',
                'var1_obs_name': 'GUST',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'RH2m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'hrrr': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'namnest': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'rrfs': {
                'var1_fcst_name': 'RH',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'le15,le20,le25,le30',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'RH',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'le15,le20,le25,le30',
                'var1_obs_options': 'cnt_thresh = [ NA, <=15, <=20, <=25, <=30 ]; cnt_logic = INTERSECTION;',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'DPT2m': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'hrrr': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'namnest': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'rrfs': {
                'var1_fcst_name': 'DPT',
                'var1_fcst_levels': 'Z2',
                'var1_fcst_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_fcst_options': 'cnt_thresh = [ NA, NA, NA, NA, NA, NA ]; cnt_logic = INTERSECTION;',
                'var1_obs_name': 'DPT',
                'var1_obs_levels': 'Z2',
                'var1_obs_thresholds': 'ge277.594,ge283.15,ge288.706,ge294.261',
                'var1_obs_options': 'cnt_thresh = [ NA, >=272.039, >=277.594, >=283.15, >=288.706, >=294.261 ]; cnt_logic = INTERSECTION;',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'MSLP': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'MSLET',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'MSLET',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'hireswfv3': {
                'var1_fcst_name': 'MSLET',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'hrrr': {
                'var1_fcst_name': 'MSLMA',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'namnest': {
                'var1_fcst_name': 'MSLET',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'rrfs': {
                'var1_fcst_name': 'MSLET',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': '',
                'var1_fcst_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
                'var1_obs_name': 'PRMSL',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': '',
                'var1_obs_options': 'set_attr_units = \\"hPa\\"; convert(p)=PA_to_HPA(p);',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'STAT',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'TCDC': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'GRIB_lvl_typ = 200; set_attr_level = \\"TOTAL\\";',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': 'GRIB_lvl_typ = 200;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'GRIB_lvl_typ = 200; set_attr_level = \\"TOTAL\\";',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': 'GRIB_lvl_typ = 200;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'GRIB_lvl_typ = 200; set_attr_level = \\"TOTAL\\";',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': 'GRIB_lvl_typ = 200;',
            },
            'hrrr': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'set_attr_level = \\"TOTAL\\"; GRIB2_ipdtmpl_index = [ 9 ]; GRIB2_ipdtmpl_val = [ 10 ];',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'GRIB_lvl_typ = 200; set_attr_level = \\"TOTAL\\";',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': 'GRIB_lvl_typ = 200;',
            },
            'rrfs': {
                'var1_fcst_name': 'TCDC',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_fcst_options': 'set_attr_level = \\"TOTAL\\"; GRIB2_ipdtmpl_index = [ 8, 9 ]; GRIB2_ipdtmpl_val = [ {lead?fmt=%H}, 200 ];',
                'var1_obs_name': 'TCDC',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt10,gt10,gt50,gt90',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'VIS': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'rrfs': {
                'var1_fcst_name': 'VIS',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_fcst_options': 'censor_thresh = gt16093.44; censor_val = 16093.44;',
                'var1_obs_name': 'VIS',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'lt805,lt1609,lt4828,lt8045,lt16090,ge8045',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'STAT',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'CEILING': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'GRIB_lvl_typ = 215; censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\";',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'GRIB_lvl_typ = 215; censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\";',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'hireswfv3': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'GRIB_lvl_typ = 215; censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\";',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'hrrr': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'GRIB_lvl_typ = 215; censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\";',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'namnest': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'GRIB_lvl_typ = 215; censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\";',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'rrfs': {
                'var1_fcst_name': 'HGT',
                'var1_fcst_levels': 'L0',
                'var1_fcst_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = -9999; set_attr_level = \\"CEILING\\"; GRIB2_ipdtmpl_index = [ 9 ]; GRIB2_ipdtmpl_val = [ 215 ];',
                'var1_obs_name': 'CEILING',
                'var1_obs_levels': 'L0',
                'var1_obs_thresholds': 'lt152,lt305,lt914,lt1524,lt3048,ge914',
                'var1_obs_options': 'GRIB_lvl_typ = 215;',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'STAT',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'NONE',
            }
        },
    },
    'PTYPE': {
        'metar': {
            'hireswarw': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'hireswfv3': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'hrrr': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'namnest': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'rrfs': {
                'var1_fcst_name': 'PTYPE',
                'var1_fcst_levels': '\\"(*,*)\\"',
                'var1_fcst_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_fcst_options': 'set_attr_name = \\"PTYPE\\";',
                'var1_obs_name': 'PRWE',
                'var1_obs_levels': 'Z0',
                'var1_obs_thresholds': 'ge1.0, ge2.0, ge3.0, ge4.0',
                'var1_obs_options': 'censor_thresh = [<161, >=161&&<=163, >=164&&<=166, >=167&&<=170, >=171&&<=173, >=174&&<=176, >176]; censor_val=[0.0, 1.0, 3.0, 0.0, 2.0, 4.0, 0.0];',
            },
            'output_types': {
                'CTC': 'NONE',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'NONE',
                'MCTC': 'STAT',
            }
        },
    },
}
