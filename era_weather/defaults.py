# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk), February 2024
"""
Defaults to use throughout the repository
"""

from era_weather import app_config

os_tiles = [
    "HO",
    "HP",
    "HT",
    "HU",
    "HW",
    "HX",
    "HY",
    "HZ",
    "NA",
    "NB",
    "NC",
    "ND",
    "NE",
    "NF",
    "NG",
    "NH",
    "NJ",
    "NK",
    "NL",
    "NM",
    "NN",
    "NO",
    "NP",
    "NR",
    "NS",
    "NT",
    "NU",
    "NW",
    "NX",
    "NY",
    "NZ",
    "OV",
    "SC",
    "SD",
    "SE",
    "TA",
    "SH",
    "SJ",
    "SK",
    "TF",
    "TG",
    "SM",
    "SN",
    "SO",
    "SP",
    "TL",
    "TM",
    "SR",
    "SS",
    "ST",
    "SU",
    "TQ",
    "TR",
    "SV",
    "SW",
    "SX",
    "SY",
    "SZ",
    "TV",
]

# pylint: disable=E1101
RAW_DATA_FOLDER = app_config.data_dirs["raw_era5_dir"]
OUTPUT_FOLDER = app_config.data_dirs["output_dir"]
OSGRID_FOLDER = app_config.data_dirs["osgrid_dir"]
# pylint: enable=E1101
