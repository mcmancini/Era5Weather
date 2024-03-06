# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), February 2024
"""
Utility functions required to process era-weather data

Functions defined here:
-----------------------

list_files(directory, year)
    extracts a list of files contained in "directory" for
    the year specified in "year"

list_years(directory)
    extracts a list of years for which there is available data
    in the folder "directory"

lonlat2osgrid(coords, figs)
    converts a lon-lat pair to an OS grid code

create_directory(directory):
    Check if directory exists. If not, create it.
"""

import os
import re
from math import floor, exp
import numpy as np
import pandas as pd
from pyproj import Transformer


def list_files(directory, year, monthly):
    """
    Extract the path(s) of any files in "directory" containing
    "year" in the filename. The function expects files to be named
    according to the following convention: "/abcdefghilmn_YYYY-MM.nc"
    if containing month, or "/abcdefghilmn_YYYY.nc" if not.

    Parameters
    ----------
    directory (str): The directory in which the files are contained.
    year (int): the year for the query
    monthly (bool): Boolean True or False. If True, the search will
        only include files containing in their name both year and month
        (i.e., "_YYYY-mm.nc"). This is useful to find all files not yet
        aggregated from monthly to yearly. If False, return only files
        which have already been aggregated yearly (i.e, "_YYYY.nc")

    Returns
    -------
    output (str or list): A list of the full paths of the matching files
        if `monthly` is True. Otherwise, a single full path of the
        matching file as a string. Returns an empty list or None if no
        matching files are found.
    """
    file_list = [os.path.join(directory, item) for item in os.listdir(directory)]

    if monthly:
        output = []
        for file in file_list:
            match = re.search(r"(\d{4})-(\d{2})\b", file)
            if match and int(match.group(1)) == year:
                output.append(file)
    else:
        output = None
        for file in file_list:
            match = re.search(r"(\d{4})\.nc$", file)
            if match:
                file_year = int("".join(i for i in match.group(1) if i.isdigit()))
                if file_year == year:
                    output = file
                    break
    return output


def list_years(directory):
    """
    extracts a list of years for which there is available data
    in the folder "directory"

    Parameters
    ----------
    directory (str): The directory in which the search needs to
        be performed

    Return
    ------
    year_list (list): A list of unique years for which data files
        are available in "directory"
    """
    file_list = [os.path.join(directory, item) for item in os.listdir(directory)]
    year_list = []
    for file in file_list:
        match = re.search(r"(\d{4})\b", file)
        year_list.append(int(match.group(1)))
    unique_years = list(set(year_list))
    unique_years.sort()
    return unique_years


class BNGError(Exception):
    """Exception raised by OSgrid coordinate conversion functions"""


def _init_regions_and_offsets():
    # Region codes for 100 km grid squares.
    regions = [
        ["HL", "HM", "HN", "HO", "HP", "JL", "JM"],
        ["HQ", "HR", "HS", "HT", "HU", "JQ", "JR"],
        ["HV", "HW", "HX", "HY", "HZ", "JV", "JW"],
        ["NA", "NB", "NC", "ND", "NE", "OA", "OB"],
        ["NF", "NG", "NH", "NJ", "NK", "OF", "OG"],
        ["NL", "NM", "NN", "NO", "NP", "OL", "OM"],
        ["NQ", "NR", "NS", "NT", "NU", "OQ", "OR"],
        ["NV", "NW", "NX", "NY", "NZ", "OV", "OW"],
        ["SA", "SB", "SC", "SD", "SE", "TA", "TB"],
        ["SF", "SG", "SH", "SJ", "SK", "TF", "TG"],
        ["SL", "SM", "SN", "SO", "SP", "TL", "TM"],
        ["SQ", "SR", "SS", "ST", "SU", "TQ", "TR"],
        ["SV", "SW", "SX", "SY", "SZ", "TV", "TW"],
    ]

    # Transpose so that index corresponds to offset
    regions = list(zip(*regions[::-1]))

    # Create mapping to access offsets from region codes
    offset_map = {}
    for i, row in enumerate(regions):
        for j, region in enumerate(row):
            offset_map[region] = (1e5 * i, 1e5 * j)

    return regions, offset_map


_regions, _offset_map = _init_regions_and_offsets()


def lonlat2osgrid(coords, figs=4):
    """
    Convert WGS84 lon-lat coordinates to British National Grid references.
    Grid references can be 4, 6, 8 or 10 fig, specified by the figs keyword.
    Adapted from John A. Stevenson's 'bng' package that can be found at
    https://pypi.org/project/bng/

    Parameters
    ----------
    :param coords (tuple): x, y coordinates to convert
    :param figs (int): - number of figures to output
    :return gridref (str): - BNG grid reference

    Return
    ------
    os_code (str): a string representing the OSgrid code of a location
        at a specified resolution (4, 6, 8, or 10 digits) starting with
        a pair of letters identifying the tile (e.g., "SX") forllowed by
        digits

    Examples
    --------

    Single value
    >>> lonlat2osgrid((-5.21469, 49.96745))

    For multiple values, use Python's zip function and list comprehension
    >>> x = [-5.21469, -5.20077, -5.18684]
    >>> y = [49.96745, 49.96783, 49.96822]
    >>> [lonlat2osgrid(coords, figs=4) for coords in zip(x, y)]
    """
    # Validate input
    bad_input_message = (
        f"Valid inputs are x, y tuple e.g. (-5.21469, 49.96783),"
        f" or list of x, y tuples. [{coords}]"
    )

    if not isinstance(coords, tuple):
        raise BNGError(bad_input_message)

    try:
        # convert to WGS84 to OSGB36 (EPSG:27700)
        # pylint: disable=E0633
        transformer = Transformer.from_crs(4326, 27700, always_xy=True)
        x_coord, y_coord = transformer.transform(coords[0], coords[1])
        # pylint: enable=E0633
    except ValueError as exc:
        raise BNGError(bad_input_message) from exc

    out_of_region_message = "Coordinate location outside UK region"
    if (x_coord < 0) or (y_coord < 0):
        raise BNGError(out_of_region_message)

    # Calculate region and SW corner offset

    try:
        region = _regions[int(floor(x_coord / 100000.0))][
            int(floor(y_coord / 100000.0))
        ]
        x_offset, y_offset = _offset_map[region]
    except IndexError as exc:
        raise BNGError(out_of_region_message) from exc

    # Format the output based on figs
    templates = {
        4: "{}{:02}{:02}",
        6: "{}{:03}{:03}",
        8: "{}{:04}{:04}",
        10: "{}{:05}{:05}",
    }
    factors = {4: 1000.0, 6: 100.0, 8: 10.0, 10: 1.0}
    try:  # Catch bad number of figures
        coords = templates[figs].format(
            region,
            int(floor((x_coord - x_offset) / factors[figs])),
            int(floor((y_coord - y_offset) / factors[figs])),
        )
    except KeyError as exc:
        raise BNGError("Valid inputs for figs are 4, 6, 8 or 10") from exc

    return coords


def create_directory(directory):
    """
    Check if the directory exists. If not, create it.

    Parameters
    ----------
    :param directory (str): The directory path.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")


def relative_humidity(temperature, dewpoint):
    """
    Calculate relative humidity from temperature and
    dewpoint in degrees Celsius.

    Parameters
    ----------
    :param temperature (Pandas.Series or float): temperature
        value or Pandas Series of temperature values in
        degrees Celsius
    :param dewpoint (Pandas.Series or float): dewpoint temperature
        value or Pandas Series of dewpoint temperature values in
        degrees Celsius

    Return
    ------
    rel_humidity (float or Pandas.Series): a value or a Pandas Series
    of values for relative humidity in percentage (i.e., 0 to 100)
    """
    if isinstance(temperature, pd.Series) and isinstance(dewpoint, pd.Series):
        if len(temperature) == len(dewpoint):
            rel_humidity = 100 * (
                ((17.625 * dewpoint) / (243.04 + dewpoint)).apply(exp)
                / ((17.625 * temperature) / (243.04 + temperature)).apply(exp)
            )
            return round(rel_humidity, 2)
        raise ValueError("Both series must be of the same length")
    if isinstance(temperature, (float, int, np.float32, np.float64)) and isinstance(
        dewpoint, (float, int, np.float32, np.float64)
    ):
        rel_humidity = 100 * (
            exp((17.625 * dewpoint) / (243.04 + dewpoint))
            / exp((17.625 * temperature) / (243.04 + temperature))
        )
        return round(rel_humidity, 2)
    raise TypeError("Unsupported type. Please provide either pandas Series or floats.")
