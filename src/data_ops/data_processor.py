import json
import csv
import pandas as pd
from pathlib import Path

from src.data_ops.data_loader import DataLoader


class DataProcessor():

    """
    This function should read the actual numbers loaded data and assign it to the variables, constraints...
    """
    def __init__(self, input_path: str, question: str):
        self.question = question
        self.input_path = input_path
        # create instance of the class
        data = DataLoader(input_path=input_path, question=question)
        # Load all data to self.all.data
        self.all_data = data._load_dataset(question)
        # Then create self.data which is this instance of the class data loader
        self.data_loader = data

    def getVariables(self):

        appliance_params = self.data._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        variables = [key for key, value in appliance_params_unwrapped.items() if value is not None]

        variables.extend(["bought", "sold", "exp_excess", "imp_excess"])

        return variables

    def getConstraints(self):



        """
        Collect the constraints: 
        pmax(t), 
        emin (min energy consumed in a day), 
        max and min load (make hourly but constant every hour)
        """
        return constraints
    def getObjCoefficients(self):
        """
        Collect hourly price data,
        buy and sell tariffs,
        penalty excess costs for import and export
        """
        return obj_coefficients


        
        """
path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataProcessor(input_path=path, question=question)

