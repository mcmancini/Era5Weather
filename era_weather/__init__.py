# -*- coding: utf-8 -*-
# Copyright (c) 2024 LEEP, University of Exeter (UK)
# Mattia Mancini (m.c.mancini@exeter.ac.uk), February 2024
# ========================================================
"""
UkWofost package initialisation file
"""
import os
from era_weather.config_parser import ConfigReader

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
project_root = os.path.abspath(os.path.join(current_directory, ".."))
config_path = project_root + "\\config.ini"
# pylint: disable=E1101
app_config = ConfigReader(config_path)
# pylint: enable=E1101
