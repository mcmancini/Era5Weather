# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP, University of Exeter (UK)
# Mattia Mancini (m.c.mancini@exeter.ac.uk), February 2024
# ========================================================
"""
rechunk_era
===========
ERA5 hourly weather reanalysis data are organised in files containing hourly time series
of all weather variables for the whole of GB in monthly or yearly chunks.
This script rechunks the data to create daily time series (averaging hourly data) for
each tile in GB for the entire temporal span of the data and for all weather variables.
Hence, each file contains the whole available data (daily) for one tile and there are as
many files as there are tiles.
The output files can be stored in netcdf or csv format based on user needs.
"""

import geopandas as gpd

# import pandas as pd
import xarray as xr
from era_weather import app_config
from era_weather.rechunk_weather import rechunk_data
from era_weather.utils import list_files, create_directory

# pylint: disable=E1101
RAW_DATA_FOLDER = app_config.data_dirs["raw_era5_dir"]
OUTPUT_FOLDER = app_config.data_dirs["output_dir"]
OSGRID_FOLDER = app_config.data_dirs["osgrid_dir"]
# pylint: enable=E1101


# Check that all files have been aggregated from monthly to yearly first
# unique_years = list_years(RAW_DATA_FOLDER)
unique_years = [2016, 2017, 2018, 2019, 2020, 2021, 2022]
yearly_file_list = []
for year in unique_years:
    # Has the data been already aggregated to yearly?
    yearly_file = list_files(directory=RAW_DATA_FOLDER, year=year, monthly=False)
    if not yearly_file:
        monthly_files = list_files(directory=RAW_DATA_FOLDER, year=year, monthly=True)
        if not monthly_files:
            raise ValueError(f"No available data for year '{year}'")
        if len(monthly_files) < 12:
            raise ValueError(
                f"Missing {12 - len(monthly_files)} months of data for year '{year}'!"
            )
        datasets = [xr.open_dataset(file) for file in monthly_files]
        combined_dataset = xr.concat(datasets, dim="time")
        combined_dataset.to_netcdf(f"{RAW_DATA_FOLDER}/era5_surface_ukeire_{year}.nc")
        yearly_file = list_files(directory=RAW_DATA_FOLDER, year=year, monthly=False)
        yearly_file_list.append(yearly_file)
    yearly_file_list.append(yearly_file)

# retrieve available lon and lats for all OS Grid 1km cells in the UK.
os_data = gpd.read_file(f"{OSGRID_FOLDER}os_bng_grids.gpkg", layer="1km_grid")
create_directory(OUTPUT_FOLDER)

for _, row in os_data.iterrows():
    rechunk_data(row, yearly_file_list=yearly_file_list, output_path=OUTPUT_FOLDER)
