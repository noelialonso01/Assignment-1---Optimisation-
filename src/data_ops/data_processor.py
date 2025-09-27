import json
import csv
import pandas as pd
from pathlib import Path

from src.data_ops.data_loader import DataLoader


class DataProcessor():
    def __init__(self, input_path: str, question: str):
        self.question = question
        self.input_path = input_path

        data = DataLoader(input_path=input_path, question=question)
        self.all_data = data._load_dataset(question)
        self.data = data

    def getVariables(self):

        appliance_params = self.data._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        variables = [key for key, value in appliance_params_unwrapped.items() if value is not None]

        variables.extend(["bought", "sold"])

        return variables
        
path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataProcessor(input_path=path, question=question)

variables = data.getVariables()

print(variables)