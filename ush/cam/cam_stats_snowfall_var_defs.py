#!/usr/bin/env python3
"""
cam_stats_snowfall_var_defs.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Defines variable configurations for Snowfall verification in the cam component.

Environment Variables (Inputs):
    None (this module is imported and used by other scripts).

Outputs:
    - Provides the generate_stats_jobs_dict dictionary containing variable
      definitions and options for Snowfall verification jobs.

This module is intended to be imported by job script generators in the cam
component to supply variable definitions for Snowfall verification.
"""

generate_stats_jobs_dict = {
    'WEASD': {
        'nohrsc': {
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
            'rrfs': {
                'var1_fcst_name': 'WEASD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\"; convert(x) = x * 0.001 * 10;',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'rrfsmem': {
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
            'rrfs': {
                'var1_fcst_name': 'SNOD',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_units = \\"m\\";',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'rrfsmem': {
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
            'rrfs': {
                'var1_fcst_name': 'ASNOW',
                'var1_fcst_levels': 'Z0',
                'var1_fcst_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_fcst_options': 'censor_thresh = lt0; censor_val = 0; set_attr_level = \\"Z0\\"; set_attr_units = \\"m\\";',
                'var1_obs_name': 'ASNOW',
                'var1_obs_levels': '',
                'var1_obs_thresholds': 'ge0.0254,ge0.0508,ge0.1016,ge0.2032,ge0.3048',
                'var1_obs_options': '',
            },
            'rrfsmem': {
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
