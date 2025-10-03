from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr
from gurobipy import GRB

from src.data_ops.data_loader import DataLoader

class InputData:

    def __init__(
        self,
        price: list[float],
        imp_tariff: float,
        exp_tariff: float,
        max_import: float,
        max_export: float,
        excess_imp_tariff: float,
        excess_exp_tariff: float,
        pmaxhourly: list[float],
        emin: float,
        load_min: list[float],
        load_max: list[float]):

        self.T = list(range(24))
        self.price = price
        self.imp_tariff = imp_tariff
        self.exp_tariff = exp_tariff
        self.max_import = max_import
        self.max_export = max_export
        self.excess_imp_tariff = excess_imp_tariff
        self.excess_exp_tariff = excess_exp_tariff
        self.pmaxhourly = pmaxhourly
        self.load_min = load_min
        self.load_max = load_max
        self.emin = emin

class DataProcessor():

    def __init__(self, input_path: str, question: str):
        self.question = question
        self.input_path = input_path
        data = DataLoader(input_path=input_path, question=question)
        # Load all data to self.all.data
        self.all_data = data._load_dataset(question)
        self.data_loader = data

    def getVariables(self):

        appliance_params = self.data_loader._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        variables = [key for key, value in appliance_params_unwrapped.items() if value is not None]
        variables.extend(["bought", "sold", "exp_excess", "imp_excess"])
        variables = pd.DataFrame({"variables": variables})
        self.variables = variables

        return variables

    def getCoefficients(self):
        appliance_params = self.data_loader._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        usage_preferences = self.data_loader._load_data_file(self.question, "usage_preferences.json")
        usage_preferences_unwrapped = usage_preferences["usage_preferences"]

        bus_params = self.data_loader._load_data_file(self.question, "bus_params.json")
        bus_params_unwrapped = bus_params["bus_params"]

        DER_production = self.data_loader._load_data_file(self.question, "DER_production.json")
        DER_production_unwrapped = DER_production["DER_production"]

        imp_tariff = float(bus_params_unwrapped[0]["import_tariff_DKK/kWh"])
        exp_tariff = float(bus_params_unwrapped[0]["export_tariff_DKK/kWh"])
        max_import = float(bus_params_unwrapped[0]["max_import_kW"])
        max_export = float(bus_params_unwrapped[0]["max_export_kW"])
        excess_imp_tariff = float(bus_params_unwrapped[0]["penalty_excess_import_DKK/kWh"])
        excess_exp_tariff = float(bus_params_unwrapped[0]["penalty_excess_export_DKK/kWh"])
        price = [float(x) for x in bus_params_unwrapped[0]["energy_price_DKK_per_kWh"]]

        pmax = float(appliance_params_unwrapped["DER"][0]["max_power_kW"])
        pmaxhourly = [float(x)*pmax for x in DER_production_unwrapped[0]["hourly_profile_ratio"]]
        load_min = float(appliance_params_unwrapped["load"][0]["min_load_ratio"])*float(appliance_params_unwrapped["load"][0]["max_load_kWh_per_hour"])
        #print("load min iis:", load_min)
        load_max = float(appliance_params_unwrapped["load"][0]["max_load_kWh_per_hour"])
        emin = float(usage_preferences_unwrapped[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"])*load_max
        print("emin is:", emin, "load max is:", load_max, "load min is:", load_min, "pmax is:", pmax, "pmaxhourly is:", pmaxhourly, "price is:", price, "imp tariff is:", imp_tariff, "exp tariff is:", exp_tariff, "max import is:", max_import, "max export is:", max_export, "excess imp tariff is:", excess_imp_tariff, "excess exp tariff is:", excess_exp_tariff,)
        return InputData(price, imp_tariff, exp_tariff, max_import, max_export, excess_imp_tariff,
               excess_exp_tariff, pmaxhourly,  emin, load_min, load_max)

class Expando(object):

    pass


class OptModel:

    def __init__(self, input_data: InputData):
        self.data = input_data
        self.results = Expando()
        self.model = gp.Model()
        self.vars = Expando()
        self.T = self.data.T  # Time periods (0-23 hours)

    def _build(self):
        ### variables are defined here, and denoted with v_
        print("emin is:", self.data.emin, "load max is:", self.data.load_max, "load min is:", self.data.load_min, "pmax is:", self.data.pmaxhourly, "price is:", self.data.price, "imp tariff is:", self.data.imp_tariff, "exp tariff is:", self.data.exp_tariff, "max import is:", self.data.max_import, "max export is:", self.data.max_export, "excess imp tariff is:", self.data.excess_imp_tariff, "excess exp tariff is:", self.data.excess_exp_tariff)
        v_load = self.model.addVars(self.T, lb=self.data.load_min, ub=self.data.load_max, name=f"v_load")
        v_prod = self.model.addVars(self.T, name="v_prod")
        v_bought = self.model.addVars(self.T, name="v_bought")
        v_sold = self.model.addVars(self.T, name="v_sold")
        v_imp_excess = self.model.addVars(self.T, name="v_imp_excess")
        v_exp_excess = self.model.addVars(self.T, name="v_exp_excess")

        # make constraints varying over time
        for i in self.T:
            self.model.addConstr(v_prod[i] <= self.data.pmaxhourly[i], name=f"DER_max[{i}]")
            self.model.addConstr(v_imp_excess[i] >= v_bought[i] - self.data.max_import, name=f"imp_excess[{i}]")
            self.model.addConstr(v_exp_excess[i] >= v_sold[i] - self.data.max_export, name=f"exp_excess[{i}]")
            self.model.addLConstr(v_load[i] - v_prod[i] == v_bought[i] - v_sold[i], name=f"power_balance_{i}")
        # make total energy constraint that doesnt vary over time
        self.model.addConstr(sum(v_load[i] for i in self.T) >= self.data.emin, name="emin_constraint")
        
        # make objective function
        obj_fn = gp.quicksum(self.data.price[t]*v_bought[t] + self.data.imp_tariff*v_bought[t]
                        - self.data.price[t]*v_sold[t] + self.data.exp_tariff*v_sold[t] 
                        + self.data.excess_imp_tariff*v_imp_excess[t] + self.data.excess_exp_tariff*v_exp_excess[t] for t in self.T)
        
        self.model.setObjective(obj_fn, GRB.MINIMIZE)
        
        # store variable handles
        self.vars.v_load = v_load
        self.vars.v_prod = v_prod
        self.vars.v_bought = v_bought
        self.vars.v_sold = v_sold
        self.vars.v_imp_excess = v_imp_excess
        self.vars.v_exp_excess = v_exp_excess
        
    def solve(self, verbose: bool = False):
        if not verbose:
            self.model.Params.OutputFlag = 0
        self.model.optimize()
        if self.model.Status not in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
            raise RuntimeError(f"Gurobi status: {self.m.Status}")


        # Collect and store results in self.results
        v = self.vars
        self.results.v_load = np.array([v.v_load[i].X for i in self.T])
        self.results.v_prod = np.array([v.v_prod[i].X for i in self.T])
        self.results.v_bought = np.array([v.v_bought[i].X for i in self.T])
        self.results.v_sold = np.array([v.v_sold[i].X for i in self.T])
        self.results.v_imp_excess = np.array([v.v_imp_excess[i].X for i in self.T])
        self.results.v_exp_excess = np.array([v.v_exp_excess[i].X for i in self.T])
        self.results.obj = self.model.ObjVal
        return self.results
        


path = r"C:\Users\alex\OneDrive\Desktop\DTU\Optimistation\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataProcessor(input_path=path, question=question).getCoefficients()
model = OptModel(data)
model._build()
results = model.solve(verbose=True)
results_df = pd.DataFrame({
    "Load (kWh)": results.v_load,
    "Production (kWh)": results.v_prod,
    "Bought (kWh)": results.v_bought,
    "Sold (kWh)": results.v_sold,
    "Import Excess (kWh)": results.v_imp_excess,
    "Export Excess (kWh)": results.v_exp_excess
}, index=pd.Index(range(24), name="Hour"))
print(f"Total daily expenditure (DKK): {results.obj:,.2f}")
print(results_df)

#variables = data._build_variables()
#constraints = data._build_constraints()

#print("hello")
