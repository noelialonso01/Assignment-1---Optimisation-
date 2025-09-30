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
import yaml

from src.utils.utils import load_dataset
from src.utils.utils import load_datafile



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
        ###self.load_aux_data('question1a_scenario1_aux_data.yaml')
        ###self.data()
        """
        Post-initialization to load and validate all required datasets (placeholder function)

        example usage:
        self.input_path = Path(self.input_path).resolve()
        
        # Load metadata (auxiliary scenario data)
        self.load_aux_data('question1a_scenario1_aux_data.yaml')
        
        # Load CSV and json datasets
        self.data()
        """
        pass

    def _load_dataset(self, question_name: str):
        self.question = question_name
        raw_data = load_dataset(question_name, self.input_path)
        for key, value in raw_data.items():
            setattr(self, key, pd.DataFrame(value))

        """Helper function to load all CSV or json files, using the appropriate method based on file extension.
        
        example usage: 
        call the load_dataset() function from utils.py to load all files in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)
        """
        return raw_data
        pass


    def _load_data_file(self, question_name: str, file_name: str):
        self.question = question_name
        self.file_name = file_name
        raw_data = load_datafile(file_name, question_name, self.input_path)
        for key, value in raw_data.items():
            setattr(self, key, pd.DataFrame(value))

        """
        Placeholder function 
        Helper function to load a specific CSV or json file, using the appropriate method based on file extension.. Raises FileNotFoundError if missing.
        
        example usage: 
        define and call a load_data_file() function from utils.py to load a specific file in the input_path directory
        save all data as class attributes (e.g. self.demand, self.wind, etc.), structured as pandas DataFrames or Series (or other format as prefered)"""
        return raw_data
        pass

    def load_aux_data(self, question_name: str, filename: str):
        """
        Placeholder Helper function to Load auxiliary metadata for the scenario/question from a YAML/json file or other formats
        
        Example application: 
        define and call a load_aux_data() function from utils.py to load a specific auxiliary file in the input_path directory
        Save the content as s class attributes, in a dictionary, pd datframe or other: self.aux_data
        Attach key values as class attributes (flattened).
        """
        pass


"""
When running, define path and question as inputs. Path should be:

"""

path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataLoader(input_path=path, question=question)
loaded_data = data._load_dataset(question)
#print(loaded_data)

path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataLoader(input_path=path, question=question)
filename = "consumer_params.json"
loaded_data = data._load_data_file(question, filename)
#print(loaded_data)