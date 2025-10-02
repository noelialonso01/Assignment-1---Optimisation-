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
    Input data for the consumer LP (Step 1A).

    Symbols:
      p_t            → p                  (list[float], DKK/kWh) market price
      g^{ti}         → g_ti               (float, DKK/kWh)  import tariff
      g^{te}         → g_te               (float, DKK/kWh)  export tariff
      b_t^{max}      → b_max              (float or list, kW) max import
      s_t^{max}      → s_max              (float or list, kW) max export
      g^{ti,pen}     → g_ti_pen           (float, DKK/kWh) penalty for import above b_max
      g^{te,pen}     → g_te_pen           (float, DKK/kWh) penalty for export above s_max
      \overline P_t  → Pbar               (list[float], kWh) PV availability per hour
      \underline L_t → L_lower            (list[float], kWh) minimum load
      \overline L_t  → L_upper            (list[float], kWh) maximum load
      E^{min}        → Lmin_total         (float, kWh) daily minimum energy

    Conventions:
      - All hourly arrays must have length T.
      - If b_max / s_max are scalars, they apply to all hours.
    """
    def _init_(
        self,
        p: list[float],
        gti: float,
        gte: float,
        bmax: float,
        smax: float,
        gti_pen: float,
        gte_pen: float,
        Pbar: list[float],
        Lmin: float,
        L_lower: list[float] = None,
        L_upper: list[float] = None,):

        assert len(p) == len(Pbar) == 24, "p and Pbar must be length-24"
        if L_lower is not None:
            assert len(L_lower) == 24, "L_lower must be length-24 if provided"
        if L_upper is not None:
            assert len(L_upper) == 24, "L_upper must be length-24 if provided"

        self.T = list(range(24))
        self.price = p
        self.grid_tariff_buy = gti
        self.grid_tariff_sell = gte
        self.bought_max = bmax if isinstance(bmax, list) else [bmax] * 24
        self.sold_max = smax if isinstance(smax, list) else [smax] * 24
        self.penalty_import = gti_pen
        self.penalty_export = gte_pen
        self.DER_max = Pbar
        self.load_min = L_lower or [0.0] * 24
        self.load_max = L_upper or [float("inf")] * 24
        self.emin = Lmin

class OptModel:

    def __init__(self, input_data: InputData):
        self.data = input_data
        self.results = Expando() #define results attributes?
        self.model = gp.Model()
        self.vars = Expando()
        self.T = self.data.T  # Time periods (0-23 hours)

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