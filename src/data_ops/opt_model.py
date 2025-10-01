from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr
from gurobipy import GRB



from src.data_ops.data_loader import DataLoader
from src.data_ops.data_processor import DataProcessor
class Expando(object):
    pass

class InputData:
    """
    holds an empty list of all the parameters needed for the optimization model
<<<<<<< HEAD
    """    
=======
    please store them in the form of dictionaries with the key being the name of the thing e.g 
    load, load_max, DER, bought, etc. using the names from the data given.
    See my code below for how i have used it.
    We need to make sure the names align with OptModel names and data processor names
    """
>>>>>>> 08cd1b2601503ab784857c4f3d819d059caa050c
    pass

class OptModel:

    def __init__(self, input_data: InputData):
        self.data = input_data
        self.results = Expando() #define results attributes?
        self.model = gp.Model()
        self.vars = Expando()
        self.T = range(0, 24)  # Time periods (0-23 hours)

    def _build(self):
        load = self.model.addVars(self.T, self.data.load, ub=self.data.load_max, name="load")
        DER = self.model.addVars(self.T,self.data.DER, name="DER")
        bought = self.model.addVars(self.T,self.data.bought, name="bought")
        sold = self.model.addVars(self.T,self.data.sold, name="sold")
        imp_excess = self.model.addVars(self.T,self.data.imp_excess, name="imp_excess")
        exp_excess = self.model.addVars(self.T,self.data.exp_excess, name="exp_excess")

        # make constraints varying over time
        for i in self.T:
            self.model.addConstr(DER[i] <= self.data.DER_max[i], name=f"DER_max[{i}]")
            self.model.addConstr(imp_excess[i] >= bought[i] - self.data.bought_max[i] , name=f"imp_excess[{i}]")
            self.model.addConstr(exp_excess[i] >= sold[i] - self.data.sold_max[i] , name=f"exp_excess[{i}]")
            self.model.addLConstr(load[i] - DER[i] == bought[i] - sold[i], name=f"power_balance_{i}")
        ### make total energy constraint that doesnt vary over time
        self.model.addConstr(sum(load[i] for i in self.T) >= self.data.emin, name="emin_constraint")
        
        ### make objective function
        obj_fn = gp.quicksum(self.data.price[t]*bought[t] + self.data.grid_tariff_buy[t]*bought[t]
                        - self.data.price[t]*sold[t] + self.data.grid_tariff_sell[t]*sold[t] 
                        + self.data.penalty_import*imp_excess[t] + self.data.penalty_export*exp_excess[t] for t in self.T)
        
        self.model.setObjective(obj_fn, GRB.MINIMIZE)
        
    def solve(self, verbose: bool = False):
        if not verbose:
            self.m.Params.OutputFlag = 0
        self.model.optimize()
        if self.model.Status not in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
            raise RuntimeError(f"Gurobi status: {self.m.Status}")

        # Collect and store results in self.results
        v = self.vars
        self.results.load = np.array([v.load[i].X for i in self.T])
        self.results.DER = np.array([v.DER[i].X for i in self.T])
        self.results.bought = np.array([v.bought[i].X for i in self.T])
        self.results.sold = np.array([v.sold[i].X for i in self.T])
        self.results.imp_excess = np.array([v.imp_excess[i].X for i in self.T])
        self.results.exp_excess = np.array([v.exp_excess[i].X for i in self.T])
        self.results.obj = self.model.ObjVal
        
        pass
        
    """
    Placeholder for optimization models using Gurobipy.

    Attributes (examples):
        N (int): Number of time steps/consumers/etc.
        question/scenario name (str): Configuration/question identifier.
        
    """


path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = OptModel(input_path=path, question=question)

variables = data._build_variables()
constraints = data._build_constraints()

print("hello")