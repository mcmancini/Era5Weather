# -*- coding: utf-8 -*-
# Copyright (c) 2023 LEEP, University of Exeter (UK)
# Mattia Mancini (m.c.mancini@exeter.ac.uk), April 2024
# =========================================================
"""
Utility functions to download and store a variety of climate data.
==================================================================

Functions defined here:
-----------------------

download_era(start_date, end_date, download_path=DEFAULT_DOWNLOAD_PATH):
    Download and store a netcdf file containing ERA5 reanalysis data to
    drive the WOFOST crop yield model implementation for the UK.

"""
import os

import cdsapi

from era_weather import app_config

# pylint: disable = E1101
DEFAULT_DOWNLOAD_PATH = app_config.data_dirs["raw_era5_dir"]
# pylint: enable = E1101


def download_era(start_year, end_year, download_path=DEFAULT_DOWNLOAD_PATH):
    """
    Download and store a netcdf file containing ERA5 reanalysis data to
    drive the WOFOST crop yield model implementation for the UK.
    We use Copernicus and we interface with their servers using
    the CDS API:
    (https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5).
    More info on how to optimise data download can be found here:
    http://tinyurl.com/5dvy4evm

    Parameters
    ----------
    :param start_year (int): The start year for the timeframe of
        interest.
    :param end_year (int): The end year for the timeframe of
        interest.
    :param download_path (str): the location where the downloaded
        data will be stored. If not set, then the path will be taken
        from the config.ini file.

    """
    cds_client = cdsapi.Client()
    for year in range(start_year, end_year + 1):
        yearly_filename = f"{download_path}/ERA5_{year}.nc"
        if os.path.exists(yearly_filename):
            print(f"Data for year '{year}' already downloaded. Skipping...")
            continue
        for month in range(1, 13):
            print("========================================================")
            print(f"Downloading data for year '{year}' and month '{month}' ...")
            monthly_filename = f"{download_path}/ERA5_{year}_{month:02d}.nc"
            if os.path.exists(monthly_filename):
                print(
                    f"data for year '{year}' and month '{month}' "
                    f"already exists. Skipping..."
                )
                continue
            cds_client.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "format": "netcdf",
                    "variable": [
                        "2m_temperature",
                        "2m_dewpoint_temperature",
                        "surface_pressure",
                        "10m_u_component_of_wind",
                        "10m_v_component_of_wind",
                        "total_precipitation",
                        "total_cloud_cover",
                        "mean_surface_net_long_wave_radiation_flux",
                        "mean_surface_downward_long_wave_radiation_flux",
                        "total_sky_direct_solar_radiation_at_surface",
                        "surface_solar_radiation_downwards",
                        "land_sea_mask",
                    ],
                    "year": str(year),
                    "month": f"{month:02d}",
                    "day": [str(i).zfill(2) for i in range(1, 32)],
                    "time": [f"{hour:02d}:00" for hour in range(24)],
                    "area": [61, -9, 49, 2],
                },
                f"{download_path}/era5_surface_ukeire_{year}-{month:02d}.nc",
            )
            print("... done ...")
    print("All data has been downloaded.")
