# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), March 2024
"""
Functions to process and reassign ERA5 reanalysis data to daily
weather for each 1km cell in the British National Grid.
"""

import numpy as np
import pandas as pd
from pyproj import Transformer
import xarray as xr
from era_weather.utils import relative_humidity


def process_weather_cell(file, coords_lonlat):
    """Weather rechunking routines"""
    yr_ds = xr.open_dataset(file)
    cell_ds = yr_ds.sel(
        longitude=coords_lonlat[0],
        latitude=coords_lonlat[1],
        method="nearest",
    )
    cell_df = cell_ds.to_dataframe()
    cell_df["wspeed"] = np.sqrt(cell_df["u10"] ** 2 + cell_df["v10"] ** 2)
    cell_df["tas"] = cell_df["t2m"] - 273.15
    cell_df["dp"] = cell_df["d2m"] - 273.15
    cell_df["hurs"] = relative_humidity(
        temperature=cell_df["tas"], dewpoint=cell_df["dp"]
    )

    cell_daily = cell_df.groupby(cell_df.index.date).agg(
        tasmean=("tas", "mean"),
        tasmin=("tas", "min"),
        tasmax=("tas", "max"),
        pr=("tp", "sum"),
        ssrd=("ssrd", "sum"),
        hurs=("hurs", "mean"),
        wspeed=("wspeed", "mean"),
    )
    cell_daily["irrad"] = cell_daily["ssrd"] / (24 * 3600)
    yr_ds.close()
    return cell_daily


def rechunk_data(row, yearly_file_list, output_path):
    """Main loop to be parallelised"""
    centroid = row.geometry.centroid
    cell_coordinates = (centroid.x, centroid.y)
    transformer = Transformer.from_crs(27700, 4326, always_xy=True)
    coords_lonlat = transformer.transform(cell_coordinates[0], cell_coordinates[1])
    cell_name = row["tile_name"]
    output = pd.DataFrame()
    for file in yearly_file_list:
        weather_time_series = process_weather_cell(file, coords_lonlat)
        output = pd.concat([output, weather_time_series])
    cell_filename = f"{output_path}{cell_name}.csv"
    output.to_csv(cell_filename)
