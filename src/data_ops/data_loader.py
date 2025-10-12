# -----------------------------
# Load Data
# -----------------------------
import json
import csv
import pandas as pd
from pathlib import Path

from pathlib import Path
from dataclasses import dataclass
from logging import Logger
import pandas as pd
import xarray as xr
import numpy as np
#import yaml

from utils.utils import load_dataset
from utils.utils import load_datafile



class DataLoader:
    """
    Loads energy system input data for a given configuration/question from structured CSV and json files
    and an auxiliary configuration metadata file.
    
    Example usage:
    open interactive window in VSCode,
    >>> cd ../../
    run the script data_loader.py in the interactive window,
    >>> data = DataLoader(input_path='..')
    """
    question: str
    input_path: Path

    def __init__(self, input_path: str, question: str = "question_1a"):
        ### These self definitions are establishing the class attributes, not used yet
        self.input_path = Path(input_path).resolve()
        self.question = question
        pass

    def _load_dataset(self, question_name: str):
        """
        loads all relevant data for a given question from structured CSV and json files in the input_path directory.
        """
        self.question = question_name
        raw_data = load_dataset(question_name, self.input_path)
        for key, value in raw_data.items():
            setattr(self, key, pd.DataFrame(value))
        return raw_data


    def _load_data_file(self, question_name: str, file_name: str):
        """
        loads a specific data file for a given question from the input_path directory."""
        self.question = question_name
        self.file_name = file_name
        raw_data = load_datafile(file_name, question_name, self.input_path)
        for key, value in raw_data.items():
            setattr(self, key, pd.DataFrame(value))
        return raw_data