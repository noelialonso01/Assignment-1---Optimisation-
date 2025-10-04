from pathlib import Path
import numpy as np
import pandas as pd
import gurobipy as gp
import xarray as xr
from gurobipy import GRB

from data_ops.data_loader import DataLoader

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
        variables.extend(["import", "export", "exp_excess", "imp_excess"])
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
        v_import = self.model.addVars(self.T, name="v_import")
        v_export = self.model.addVars(self.T, name="v_export")
        v_imp_excess = self.model.addVars(self.T, name="v_imp_excess")
        v_exp_excess = self.model.addVars(self.T, name="v_exp_excess")

        # make constraints varying over time
        for i in self.T:
            self.model.addConstr(v_prod[i] <= self.data.pmaxhourly[i], name=f"DER_max[{i}]")
            self.model.addConstr(v_imp_excess[i] >= v_import[i] - self.data.max_import, name=f"imp_excess[{i}]")
            self.model.addConstr(v_exp_excess[i] >= v_export[i] - self.data.max_export, name=f"exp_excess[{i}]")
            self.model.addLConstr(v_load[i] - v_prod[i] == v_import[i] - v_export[i], name=f"power_balance_{i}")
        # make total energy constraint that doesnt vary over time
        self.model.addConstr(sum(v_load[i] for i in self.T) >= self.data.emin, name="emin_constraint")
        
        # make objective function
        obj_fn = gp.quicksum(self.data.price[t]*v_import[t] + self.data.imp_tariff*v_import[t]
                        - self.data.price[t]*v_export[t] + self.data.exp_tariff*v_export[t] 
                        + self.data.excess_imp_tariff*v_imp_excess[t] + self.data.excess_exp_tariff*v_exp_excess[t] for t in self.T)
        
        self.model.setObjective(obj_fn, GRB.MINIMIZE)
        
        # store variable handles
        self.vars.v_load = v_load
        self.vars.v_prod = v_prod
        self.vars.v_import = v_import
        self.vars.v_export = v_export
        self.vars.v_imp_excess = v_imp_excess
        self.vars.v_exp_excess = v_exp_excess

    def update_data(self, data_name: str, new_value):
            for i in self.data.__dict__.keys():
                if i == data_name:
                    setattr(self.data, data_name, new_value)
                    print(f"Updated {data_name} to {new_value}")
                    self.model.update()
        
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
        self.results.v_import = np.array([v.v_import[i].X for i in self.T])
        self.results.v_export = np.array([v.v_export[i].X for i in self.T])
        self.results.v_imp_excess = np.array([v.v_imp_excess[i].X for i in self.T])
        self.results.v_exp_excess = np.array([v.v_exp_excess[i].X for i in self.T])
        self.results.obj = self.model.ObjVal
        self.results.prices = np.asarray(self.data.price, dtype=float).reshape(-1)
        return self.results
    

class OptModel2:
    def __init__(self, input_data: InputData):
        self.data = input_data
        self.results = Expando()
        self.model = gp.Model()
        self.vars = Expando()
        self.cons = Expando()  # store constraint handles
        self.cons.prod_max = {}
        self.cons.imp_excess = {}
        self.cons.exp_excess = {}
        self.cons.power_balance = {}
        self.T = self.data.T  # Time periods (0-23 hours)

    # helper: index if vector, otherwise treat as scalar
    def _at(self, x, t):
        try:
            return x[t]
        except Exception:
            return x

    def _set_objective(self):
        # same structure as yours; supports scalar or 24-vector tariffs/prices
        obj_fn = gp.quicksum(
            self._at(self.data.price, t)       * self.vars.v_import[t]
          + self._at(self.data.imp_tariff, t) * self.vars.v_import[t]
          - self._at(self.data.price, t)       * self.vars.v_export[t]
          + self._at(self.data.exp_tariff, t) * self.vars.v_export[t]
          + self.data.excess_imp_tariff       * self.vars.v_imp_excess[t]
          + self.data.excess_exp_tariff       * self.vars.v_exp_excess[t]
          for t in self.T
        )
        self.model.setObjective(obj_fn, GRB.MINIMIZE)

    def _build(self):
        ### variables are defined here, and denoted with v_
        print("emin is:", self.data.emin, "load max is:", self.data.load_max, "load min is:", self.data.load_min,
              "pmax is:", self.data.pmaxhourly, "price is:", self.data.price, "imp tariff is:", self.data.imp_tariff,
              "exp tariff is:", self.data.exp_tariff, "max import is:", self.data.max_import, "max export is:",
              self.data.max_export, "excess imp tariff is:", self.data.excess_imp_tariff, "excess exp tariff is:",
              self.data.excess_exp_tariff)

        # variable bounds (keep your names)
        v_load = self.model.addVars(self.T, lb=self.data.load_min, ub=self.data.load_max, name=f"v_load")
        v_prod = self.model.addVars(self.T, lb=0.0, name="v_prod")
        v_import = self.model.addVars(self.T, lb=0.0, name="v_import")
        v_export = self.model.addVars(self.T, lb=0.0, name="v_export")
        v_imp_excess = self.model.addVars(self.T, lb=0.0, name="v_imp_excess")
        v_exp_excess = self.model.addVars(self.T, lb=0.0, name="v_exp_excess")

        # store variable handles with your names
        self.vars.v_load = v_load
        self.vars.v_prod = v_prod
        self.vars.v_import = v_import
        self.vars.v_export = v_export
        self.vars.v_imp_excess = v_imp_excess
        self.vars.v_exp_excess = v_exp_excess

        # constraints (store handles so we can read Pi and update RHS later)
        for i in self.T:
            self.cons.prod_max[i] = self.model.addConstr(v_prod[i] <= self.data.pmaxhourly[i], name=f"prod_max[{i}]")
            # v_imp_excess[i] >= v_import[i] - max_import  ->  v_imp_excess - v_import >= -max_import (RHS)
            self.cons.imp_excess[i] = self.model.addConstr(
                v_imp_excess[i] >= v_import[i] - self.data.max_import, name=f"imp_excess[{i}]"
            )
            # v_exp_excess[i] >= v_export[i] - max_export  ->  v_exp_excess - v_export >= -max_export (RHS)
            self.cons.exp_excess[i] = self.model.addConstr(
                v_exp_excess[i] >= v_export[i] - self.data.max_export, name=f"exp_excess[{i}]"
            )
            self.cons.power_balance[i] = self.model.addLConstr(
                v_load[i] - v_prod[i] == v_import[i] - v_export[i], name=f"power_balance_{i}"
            )

        # total energy constraint (keep your name)
        self.cons.emin_constraint = self.model.addConstr(
            gp.quicksum(v_load[i] for i in self.T) >= self.data.emin, name="emin_constraint"
        )

        # objective (same expression as yours, factored into helper)
        self._set_objective()

    def update_data(self, data_name: str, new_value):
        # update Python-side data
        if not hasattr(self.data, data_name):
            raise AttributeError(f"No such data field on input data: {data_name}")
        setattr(self.data, data_name, new_value)
        print(f"Updated {data_name} to {new_value}")

        # propagate to model (bounds/RHS/objective), keeping your names
        if data_name == "pmaxhourly":
            for i in self.T:
                # v_prod[i] <= pmaxhourly[i]  (RHS)
                self.cons.prod_max[i].RHS = float(self.data.pmaxhourly[i])

        elif data_name == "emin":
            self.cons.emin_constraint.RHS = float(self.data.emin)

        elif data_name in {"load_min", "load_max"}:
            # bounds on v_load
            for i in self.T:
                self.vars.v_load[i].LB = float(self.data.load_min[i])
                self.vars.v_load[i].UB = float(self.data.load_max[i])

        elif data_name == "max_import":
            # v_imp_excess - v_import >= -max_import
            for i in self.T:
                self.cons.imp_excess[i].RHS = -float(self.data.max_import)

        elif data_name == "max_export":
            # v_exp_excess - v_export >= -max_export
            for i in self.T:
                self.cons.exp_excess[i].RHS = -float(self.data.max_export)

        elif data_name in {"price", "imp_tariff", "exp_tariff", "excess_imp_tariff", "excess_exp_tariff"}:
            # prices/tariffs affect the objective coefficients
            self._set_objective()

        self.model.update()

    def solve(self, verbose: bool = False):
        if not verbose:
            self.model.Params.OutputFlag = 0
        self.model.optimize()
        if self.model.Status not in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
            raise RuntimeError(f"Gurobi status: {self.model.Status}")

        # Collect and store results in self.results
        v = self.vars
        self.results.v_load = np.array([v.v_load[i].X for i in self.T], dtype=float)
        self.results.v_prod = np.array([v.v_prod[i].X for i in self.T], dtype=float)
        self.results.v_import = np.array([v.v_import[i].X for i in self.T], dtype=float)
        self.results.v_export = np.array([v.v_export[i].X for i in self.T], dtype=float)
        self.results.v_imp_excess = np.array([v.v_imp_excess[i].X for i in self.T], dtype=float)
        self.results.v_exp_excess = np.array([v.v_exp_excess[i].X for i in self.T], dtype=float)
        self.results.obj = float(self.model.ObjVal)
        self.results.prices = np.asarray(self.data.price, dtype=float).reshape(-1)

        duals = Expando()
        # per-hour constraints -> arrays length |T|
        duals.prod_max       = np.array([self.cons.prod_max[i].Pi       for i in self.T], dtype=float)
        duals.imp_excess    = np.array([self.cons.imp_excess[i].Pi    for i in self.T], dtype=float)
        duals.exp_excess    = np.array([self.cons.exp_excess[i].Pi    for i in self.T], dtype=float)
        duals.power_balance = np.array([self.cons.power_balance[i].Pi for i in self.T], dtype=float)
        # single daily energy constraint -> scalar
        duals.emin_constraint = float(self.cons.emin_constraint.Pi)

        self.results.duals = duals
        return self.results
    

    