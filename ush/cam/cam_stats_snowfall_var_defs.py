#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_stats_snowfall_var_defs.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Configurations for each variable that will be processed by MET
#
# =============================================================================

generate_stats_jobs_dict = {
    'WEASD': {
        'nohrsc': {
            'hireswarw': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_level = \\"Z0\\"; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'hireswarwmem2': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_level = \\"Z0\\"; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'hireswfv3': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'hrrr': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'STAT',
            }
        },
    },
    'SNOD': {
        'nohrsc': {
            'hrrr': {
                'var1_fcst_name': 'SNOD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\";',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'namnest': {
                'var1_fcst_name': 'SNOD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\";',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'STAT',
            }
        },
    },
    'ASNOW': {
        'nohrsc': {
            'hrrr': {
                'var1_fcst_name': 'ASNOW',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_level = \\"Z0\\"; set_attr_units = \\"m\\";',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'output_types': {
                'CTC': 'STAT',
                'SL1L2': 'NONE',
                'VL1L2': 'NONE',
                'CNT': 'NONE',
                'VCNT': 'NONE',
                'NBRCNT': 'STAT',
            }
        },
    },
}
