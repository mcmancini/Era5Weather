# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk)
"""
Sample script to download and rechunk ERA5 Reanalysis weather data from Copernicus
using the CDS API (https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5)
More info on how to optimise data download can be found here:
http://tinyurl.com/5dvy4evm

ERA5 hourly weather reanalysis data are organised in files containing hourly time series
of all weather variables for the whole of GB in monthly or yearly chunks.
This script rechunks the data to create daily time series (averaging hourly data) for
each 1km tile in GB for the entire temporal span of the data and for all weather variables.
Hence, each file contains the whole available data (daily) for one tile and there are as
many files as there are 1km tiles.
The output files can be stored in netcdf or csv format based on user needs.
"""
import argparse

import geopandas as gpd

# import pandas as pd
from joblib import Parallel, delayed

from era_weather.defaults import OSGRID_FOLDER, OUTPUT_FOLDER, RAW_DATA_FOLDER, os_tiles
from era_weather.era_downloader import download_era
from era_weather.rechunk_weather import aggregate_years, rechunk_data
from era_weather.utils import count_processes, create_directory, validate_options

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download and process historic ERA5 reanalysis weather data"
    )
    parser.add_argument(
        "-s",
        "--start",
        type=int,
        required=True,
        help="The first year for which wheater data is required",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=int,
        required=True,
        help="The last year for which wheater data is required",
    )
    parser.add_argument(
        "-o",
        "--options",
        type=validate_options,
        required=False,
        help=(
            "Options for the downloader. It can assume values of 'download' "
            "or 'process' or it can be left empty, in which case the data will"
            "be both downloaded and rechunked"
        ),
    )

    args = parser.parse_args()
    FIRST_YEAR = args.start
    LAST_YEAR = args.end
    PROCESSING_OPTIONS = getattr(args, "options", "both")

    if PROCESSING_OPTIONS == "download":
        download_era(
            start_year=FIRST_YEAR, end_year=LAST_YEAR, download_path=RAW_DATA_FOLDER
        )
    elif PROCESSING_OPTIONS == "process":
        # Check that all files have been aggregated from monthly to yearly first
        yearly_file_list = aggregate_years(
            raw_data_folder=RAW_DATA_FOLDER, start_year=FIRST_YEAR, end_year=LAST_YEAR
        )

        # retrieve available lon and lats for all OS Grid 1km cells in the UK.
        os_data = gpd.read_file(f"{OSGRID_FOLDER}os_bng_grids.gpkg", layer="1km_grid")
        os_data_filtered = os_data[os_data["tile_name"].str[:2].isin(os_tiles)]

        create_directory(OUTPUT_FOLDER)
        num_processes = count_processes()
        Parallel(n_jobs=num_processes)(
            delayed(rechunk_data)(row, yearly_file_list, OUTPUT_FOLDER)
            for _, row in os_data_filtered.iterrows()
        )
    else:
        download_era(
            start_year=FIRST_YEAR, end_year=LAST_YEAR, download_path=RAW_DATA_FOLDER
        )
        yearly_file_list = aggregate_years(
            raw_data_folder=RAW_DATA_FOLDER, start_year=FIRST_YEAR, end_year=LAST_YEAR
        )
        os_data = gpd.read_file(f"{OSGRID_FOLDER}os_bng_grids.gpkg", layer="1km_grid")
        os_data_filtered = os_data[os_data["tile_name"].str[:2].isin(os_tiles)]
        create_directory(OUTPUT_FOLDER)
        num_processes = count_processes()
        Parallel(n_jobs=num_processes)(
            delayed(rechunk_data)(row, yearly_file_list, OUTPUT_FOLDER)
            for _, row in os_data_filtered.iterrows()
        )
