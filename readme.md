# ERA5 Historic Weather download
---
**Author**: [Mattia C. Mancini](https://github.com/mcmancini) -- (m.c.mancini@exeter.ac.uk)  
**Date**: July 30th, 2024  

---
This document goes through the steps required to download and process [ERA5 reanalysis land hourly historic data](https://cds-beta.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview) for the purposes of driving the [UK implementation](https://github.com/mcmancini/UkWofost) of the [WOFOST](https://www.wur.nl/en/research-results/research-institutes/environmental-research/facilities-tools/software-models-and-databases/wofost.htm) crop yield model.  
Downloading and processing of the ERA5 reanalysis data is done using the `download_and_process_era5.py` script, which allows to:
1. Download and store hourly data for the whole of the UK in monthly chunks for a set of years of interest;
2. Process the downloaded data: this includes the following:
    - unit changes, such that the output weather variables are expressed in the required units to run WOFOST;
    - reprojection to British National Grid;
    - Aggregation from hourly to daily data;
    - Assignment of weather data to each 1km tile in the British National Grid;
    - The weather data associated with each tile in the 1km BNG is then stored on disk as a .csv file. Each output file contains a daily time series of weather data with the correct units and for the entire timeframe of interest for the BNG tile that it refers to.

## Content
- [Quickstart](#quickstart)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Basic usage](#basic-usage)
  - [Notebooks](#notebooks)
- [Development](#development)
  - [Tests](#tests)
- [Overview](#overview)
  - [Modules](#modules)
  - [Types](#types)
## Quickstart

### Prerequisites
- A [`Python`](https://www.python.org/) installation (3.11+).
- A [`Conda`](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) installation.

### Installation
1. Clone the repository to your local disk'
2. With Conda and Python installed, create a new Conda environment from file running the command: `conda env create -f "full\path\of\environment.yml"` The `full\path\of\environment.yml` is the full path of the `environment.yml` file in the main project directory of the newly cloned repository.

### Basic usage
To use the ERA5 weather data downloader and processer, a series of steps are required.
1. **Step 1: User registration with Copernicus ECMWF.**
To access the [Copernicus Climate Data Store](https://cds-beta.climate.copernicus.eu) an account is required. As of the writing of this notebook, old accounts (registered before July 18th, 2024) are no longer working so users who registered in the past will need to register again given the CDS migration to the new infrastructure and new CDS  engine. Equally, old API keys and endpoints will no longer work.

2. **Step 2: set up the API access token and endpoint.**
Downloads will be available through the use of the [cdsapi python package](https://github.com/ecmwf/cdsapi) which is installed through pip. If you install the Conda environmment defined in `environment.yml` in the main project folder, this will be installed automatically.
An API access token is required for the API to work. This is available [here](https://cds-beta.climate.copernicus.eu/how-to-api#install-the-cds-api-token) (after log-in).  
Once the access token has been generated, it must be stored in your `$HOME` directory. For Windows machines, this is usually `C:\Users\username\` (change *'username'* to your own). To store the access token:
- create a new text file called `.cdsapirc`. Make sure that the file does not have a .txt extension to work properly.
- Open the `.cdsapirc` file with a text editor and paste your access token retrieved from the CDS website. This will look something like:
    ```
    url: https://cds-beta.climate.copernicus.eu/api
    key: your_api_key
    ```
- Save and close the `.cdsapirc` file.

3. **Step 3: accept the license to download the dataset of interest.**
Each data type comes with a license that needs to be accepted before download. Clicking on the `Download` tab for each dataset brings you to a page at the bottom of which there is a `Terms of use` section which allows to read the terms of the license and accept them. Failing to accept the license will return a self explanatory error when trying to download the dataset using the API. 

More information on the CDS system and the API set up is available [here](https://confluence.ecmwf.int/display/CKB/Please+read%3A+CDS+and+ADS+migrating+to+new+infrastructure%3A+Common+Data+Store+%28CDS%29+Engine) and [here](https://forum.ecmwf.int/t/the-new-climate-data-store-beta-cds-beta-is-now-live/3315).

4. **Step 4: Download and process the required data.**
This is done running the script `download_and_process_era5.py` contained in the main project directory.  
For this to work, the following steps are required:
    - Download and extract the [British National Grid 1km data](https://github.com/OrdnanceSurvey/OS-British-National-Grids) into a folder.
    - Open the [`config.ini`](/config.ini) file in the main project folder and edit the paths to point to locations on your disk where the data will need to be stored/read from. In particular:
    - **raw_era5_dir**: this is where the raw ERA5 data retrieved using the API will be stored.
    - **output_dir**: this is where the processed csv files will be stored. If the location does not exist, it will be created.
    - **osgrid_dir**: this is where the British National Grid 1km data is stored (see first bullet point above).
    - Run the [download_and_process_era5.py](/download_and_process_era5.py) script. This is done from terminal and the following syntax must be used: `python download_and_process_era5.py --start XXXX --end YYYY --options download` where `XXXX` and `YYYY` are the start year and the end year for which data needs to be downloaded. The argument `--options` is optional, and indicates whether the data needs to be dowloaded, processed or both. As such, it can take values of `download`, for only donwloading the hourly data, `process`, to only rechunk and assign already downloaded raw weather data to BNG. If left empty (i.e., `python download_and_process_era5.py --start XXXX --end YYYY`), then the script will both download and process the data for the required time frame. 

### Notebooks
The notebook [era5_downloader.ipynb](/examples/era5_downloader.ipynb) contains detailed instructions on how to set up and run the weatehr data downloader and processor.

## Development

### Tests

## Overview

### Modules

### Types