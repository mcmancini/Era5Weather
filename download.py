# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP - University of Exeter (UK)
# Mattia C. Mancini (m.c.mancini@exeter.ac.uk)
"""
Sample script to download ERE5 Reanalysis weather data from Copernicus
using the CDS API (https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5)
More info on how to optimise data download can be found here:
http://tinyurl.com/5dvy4evm
"""

import cdsapi

c = cdsapi.Client()

FIRST_YEAR = 2016
LAST_YEAR = 2017

for year in range(FIRST_YEAR, LAST_YEAR + 1):
    for month in range(1, 13):
        print("=========================================================")
        print(f"Downloading {year}-{month:02d}")
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": "2m_temperature",
                "year": str(year),
                "month": f"{month:02d}",
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": [
                    "00:00",
                    "01:00",
                    "02:00",
                    "03:00",
                    "04:00",
                    "05:00",
                    "06:00",
                    "07:00",
                    "08:00",
                    "09:00",
                    "10:00",
                    "11:00",
                    "12:00",
                    "13:00",
                    "14:00",
                    "15:00",
                    "16:00",
                    "17:00",
                    "18:00",
                    "19:00",
                    "20:00",
                    "21:00",
                    "22:00",
                    "23:00",
                ],
                "area": [
                    61,
                    -9,
                    49,
                    2,
                ],
                "format": "nc",
            },
            f"{year}-{month:02d}.nc",
        )