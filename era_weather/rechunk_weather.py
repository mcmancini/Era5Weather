# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), March 2024
"""
Functions to process and reassign ERA5 reanalysis data to daily
weather for each 1km cell in the British National Grid.
"""

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer

from era_weather.utils import list_files, list_years, relative_humidity


def process_weather_cell(file, coords_lonlat):
    """Weather rechunking routines"""
    yr_ds = xr.open_dataset(file)
    cell_ds = yr_ds.sel(
        longitude=coords_lonlat[0],
        latitude=coords_lonlat[1],
        method="nearest",
    )
    cell_df = cell_ds.to_dataframe().reset_index().dropna()
    cell_df["wspeed"] = np.sqrt(cell_df["u10"] ** 2 + cell_df["v10"] ** 2)
    cell_df["tas"] = cell_df["t2m"] - 273.15
    cell_df["dp"] = cell_df["d2m"] - 273.15
    cell_df["hurs"] = relative_humidity(
        temperature=cell_df["tas"], dewpoint=cell_df["dp"]
    )
    cell_df["tp"] = cell_df["tp"] * 1000  # rain in m!

    if "time" in cell_df.columns:
        cell_df.drop(columns=["time"], inplace=True)

    if 'date' not in cell_df.columns:
        if 'valid_time' in cell_df.columns:
            cell_df.rename(columns={'valid_time': 'date'}, inplace=True)
        else:
            raise ValueError("Neither 'date' nor 'valid_time' column found in the DataFrame.")

    cell_daily = cell_df.groupby(cell_df.date).agg(
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


def aggregate_years(raw_data_folder, start_year, end_year):
    """Routine to list raw monthly data and aggregate to yearly"""
    years_to_process = list(range(start_year, end_year + 1))
    unique_years = list_years(raw_data_folder)
    yearly_file_list = []
    for year in set(unique_years).intersection(years_to_process):
        # Has the data been already aggregated to yearly?
        yearly_file = list_files(directory=raw_data_folder, year=year, monthly=False)
        if not yearly_file:
            monthly_files = list_files(
                directory=raw_data_folder, year=year, monthly=True
            )
            if not monthly_files:
                raise ValueError(f"No available data for year '{year}'")
            if len(monthly_files) < 12:
                raise ValueError(
                    f"Missing {12 - len(monthly_files)} months of data for year '{year}'!"
                )
            datasets = [xr.open_dataset(file) for file in monthly_files]
            combined_dataset = xr.concat(datasets, dim="valid_time")
            encoding = {
                var: {"dtype": combined_dataset[var].dtype}
                for var in combined_dataset.data_vars
            }
            combined_dataset.to_netcdf(
                f"{raw_data_folder}/era5_surface_ukeire_{year}.nc", encoding=encoding
            )
            yearly_file = list_files(
                directory=raw_data_folder, year=year, monthly=False
            )
            yearly_file_list.append(yearly_file)
        yearly_file_list.append(yearly_file)
    return yearly_file_list


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
    output.reset_index(inplace=True)
    output.rename(columns={"index": "date"}, inplace=True)
    output.to_csv(cell_filename, index=False)
