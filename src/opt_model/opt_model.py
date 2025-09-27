from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr

from src.data_ops import data_loader


class OptModel:

    def __init__(self, question: str, input_path: str):
        data = DataLoader(input_path=input_path, question=question)
        self.data = data._load_dataset(question)

        self.results = Expando() #define results attributes?
        self._build_model() #call method to build model

    def _build_variables(self, variables: list):
        # variables in order of: PV, 
        self.variables = {v: self.model.addVar(lb=0, name=f'{v}') for v in variables}

    def _build_constraints(self):
        self.constraints = {}
        
        max value constraint = self.model.addLConstr(self.variables[DER] + self.variables['y'] <= 10, name='constraint_1')
    """
    Placeholder for optimization models using Gurobipy.

    Attributes (examples):
        N (int): Number of time steps/consumers/etc.
        question/scenario name (str): Configuration/question identifier.
        ...
    """