from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr


#from src.data_ops import data_loader
from src.data_ops.data_loader import DataLoader
from src.data_ops.data_processor import DataProcessor
#from ...data_ops.data_loader import DataLoader
class Expando(object):
    pass

class InputData:
"""
holds an empty list of all the parameters needed for the optimization model
"""    
    pass

class OptModel:

    def __init__(self, input_data: InputData):
        self.data = input_data
        self.results = Expando() #define results attributes?
        self.model = gp.Model()
        self.vars = Expando()
        self.T = range(0, 24)  # Time periods (0-23 hours)

    def _build_variables(self):
        load = self.model.addVars(self.data.load, name="load")
        DER = self.model.addVars(self.data.DER, name="DER")
        bought = self.model.addVars(self.data.bought, name="bought")
        sold = self.model.addVars(self.data.sold, name="sold")

    def _build_constraints(self):
        self.constraints = {}

        power_balance = list[str]
        power_balance = {f"power_balance_{t}":self.model.addLConstr(load[t] == DER[t] + bought[t] - sold[t], name=f"power_balance_{t}") for t in self.T}
        
        print(power_balance)
        return power_balance
        
        #max value constraint = self.model.addLConstr(self.variables[DER] + self.variables['y'] <= 10, name='constraint_1')
    """
    Placeholder for optimization models using Gurobipy.

    Attributes (examples):
        N (int): Number of time steps/consumers/etc.
        question/scenario name (str): Configuration/question identifier.
        ...
    """


path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = OptModel(input_path=path, question=question)

variables = data._build_variables()
constraints = data._build_constraints()

print("hello")