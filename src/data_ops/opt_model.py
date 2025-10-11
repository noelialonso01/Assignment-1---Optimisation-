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
        load_max: list[float],
        load_profile: list[float],
        pmin: float,
        # optional battery parameters
        SOC_ratio_ini: float | None = None,         
        SOC_ratio_fin: float | None = None,         
        bat_capacity: float | None = None,          
        max_charge_power_ratio: float | None = None,    
        max_discharge_power_ratio: float | None = None, 
        charge_eff: float | None = None,            
        discharge_eff: float | None = None):

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
        self.load_profile = load_profile
        self.pmin = pmin
        
        #optional battery parameters
        self.SOC_ratio_ini = SOC_ratio_ini
        self.SOC_ratio_fin = SOC_ratio_fin
        self.bat_capacity = bat_capacity
        self.max_charge_power_ratio = max_charge_power_ratio
        self.max_discharge_power_ratio = max_discharge_power_ratio
        self.charge_eff = charge_eff
        self.discharge_eff = discharge_eff

class DataProcessor():

    def __init__(self, input_path: str, question: str):
        self.question = question
        self.input_path = input_path
        data = DataLoader(input_path=input_path, question=question)
        self.data_loader = data

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
        pmin = float(appliance_params_unwrapped["DER"][0]["min_power_ratio"])*pmax
        pmaxhourly = [float(x)*pmax for x in DER_production_unwrapped[0]["hourly_profile_ratio"]]
        load_min = float(appliance_params_unwrapped["load"][0]["min_load_ratio"])*float(appliance_params_unwrapped["load"][0]["max_load_kWh_per_hour"])
        load_max = float(appliance_params_unwrapped["load"][0]["max_load_kWh_per_hour"])
        if self.question == "question_1a":
            load_profile = None
            emin = float(usage_preferences_unwrapped[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"])*load_max
        else:
            load_profile = [float(x) for x in (usage_preferences_unwrapped[0]["load_preferences"][0]["hourly_profile_ratio"])]
            emin = None
        if self.question == "question_1c":
            SOC_ratio_ini = float(usage_preferences_unwrapped[0]["storage_preferences"][0]["initial_soc_ratio"])
            SOC_ratio_fin = float(usage_preferences_unwrapped[0]["storage_preferences"][0]["final_soc_ratio"])
            bat_capacity = float(appliance_params_unwrapped["storage"][0]["storage_capacity_kWh"])
            max_charge_power_ratio = float(appliance_params_unwrapped["storage"][0]["max_charging_power_ratio"])
            max_discharge_power_ratio = float(appliance_params_unwrapped["storage"][0]["max_discharging_power_ratio"])
            charge_eff = float(appliance_params_unwrapped["storage"][0]["charging_efficiency"])
            discharge_eff = float(appliance_params_unwrapped["storage"][0]["discharging_efficiency"])
            return InputData(price, imp_tariff, exp_tariff, max_import, max_export, excess_imp_tariff,
               excess_exp_tariff, pmaxhourly,  emin, load_min, load_max, load_profile, pmin, SOC_ratio_ini, 
               SOC_ratio_fin, bat_capacity, max_charge_power_ratio, max_discharge_power_ratio, charge_eff, discharge_eff)
        else:
        #print("emin is:", emin, "load max is:", load_max, "load min is:", load_min, "pmax is:", pmax, "pmaxhourly is:", pmaxhourly, "price is:", price, "imp tariff is:", imp_tariff, "exp tariff is:", exp_tariff, "max import is:", max_import, "max export is:", max_export, "excess imp tariff is:", excess_imp_tariff, "excess exp tariff is:", excess_exp_tariff,)
            return InputData(price, imp_tariff, exp_tariff, max_import, max_export, excess_imp_tariff,
               excess_exp_tariff, pmaxhourly,  emin, load_min, load_max, load_profile, pmin)
    

class Expando(object):
    pass

class OptModel2:
    def __init__(self, input_data: InputData, question: str):
        self.data = input_data
        self.question = question
        self.results = Expando()
        self.model = gp.Model()
        self.vars = Expando()
        self.cons = Expando()  # store constraint handles
        self.cons.prod_max = {}
        self.cons.imp_excess = {}
        self.cons.exp_excess = {}
        self.cons.power_balance = {}
        self.cons.load_max = {}
        self.cons.load_min = {}
        self.cons.deviation_pos = {}
        self.cons.deviation_neg = {}
        self.cons.prod_min = {}
        self.T = self.data.T  # Time periods (0-23 hours)


    # helper: index if vector, otherwise treat as scalar
    def _at(self, x, t):
        try:
            return x[t]
        except Exception:
            return x

    def _set_objective(self):
    ### sets relevant objective function based on question 
        if self.question == "question_1a":
            obj_fn = -gp.quicksum(
                self._at(self.data.price, t)       * self.vars.v_import[t]
              + self._at(self.data.imp_tariff, t) * self.vars.v_import[t]
              - self._at(self.data.price, t)       * self.vars.v_export[t]
              + self._at(self.data.exp_tariff, t) * self.vars.v_export[t]
              + self.data.excess_imp_tariff       * self.vars.v_imp_excess[t]
              + self.data.excess_exp_tariff       * self.vars.v_exp_excess[t]
              for t in self.T
            )
        if self.question == "question_1b":
            obj_fn = -gp.quicksum(
                self._at(self.data.price, t)       * self.vars.v_import[t]
              + self._at(self.data.imp_tariff, t) * self.vars.v_import[t]
              - self._at(self.data.price, t)       * self.vars.v_export[t]
              + self._at(self.data.exp_tariff, t) * self.vars.v_export[t]
              + self.data.excess_imp_tariff       * self.vars.v_imp_excess[t]
              + self.data.excess_exp_tariff       * self.vars.v_exp_excess[t]
              + self.data.alpha * self.vars.v_deviation[t] for t in self.T
            )
        if self.question == "question_1c":
            ### same as 1b i think?
            obj_fn = -gp.quicksum(
                self._at(self.data.price, t)       * self.vars.v_import[t]
              + self._at(self.data.imp_tariff, t) * self.vars.v_import[t]
              - self._at(self.data.price, t)       * self.vars.v_export[t]
              + self._at(self.data.exp_tariff, t) * self.vars.v_export[t]
              + self.data.excess_imp_tariff       * self.vars.v_imp_excess[t]
              + self.data.excess_exp_tariff       * self.vars.v_exp_excess[t]
              + self.data.alpha * self.vars.v_deviation[t] for t in self.T
            )


        self.model.setObjective(obj_fn, GRB.MAXIMIZE)

    def _build(self, alpha: float = 10):
        ### variables are defined here, and denoted with v_
        self.data.alpha = alpha
        v_load = self.model.addVars(self.T, lb=0.0, name=f"v_load")
        v_prod = self.model.addVars(self.T, lb=-GRB.INFINITY, name="v_prod")
        v_import = self.model.addVars(self.T, lb=0.0, name="v_import")
        v_export = self.model.addVars(self.T, lb=0.0, name="v_export")
        v_imp_excess = self.model.addVars(self.T, lb=0.0, name="v_imp_excess")
        v_exp_excess = self.model.addVars(self.T, lb=0.0, name="v_exp_excess")
        v_deviation = self.model.addVars(self.T, lb=0.0, name="v_deviation")
        v_SOC = self.model.addVars(self.T, lb=0.0, name="v_SOC")
        v_E_charged = self.model.addVars(self.T, lb=0.0, name="v_E_charged")
        v_E_discharged = self.model.addVars(self.T, lb=0.0, name="v_E_discharged")


        # store variable handles
        self.vars.v_load = v_load
        self.vars.v_prod = v_prod
        self.vars.v_import = v_import
        self.vars.v_export = v_export
        self.vars.v_imp_excess = v_imp_excess
        self.vars.v_exp_excess = v_exp_excess
        self.vars.v_deviation = v_deviation
        self.vars.v_SOC = v_SOC
        self.vars.v_E_charged = v_E_charged
        self.vars.v_E_discharged = v_E_discharged

        # constraints (store handles so we can read Pi and update RHS later)
        for i in self.T:
            self.cons.prod_max[i] = self.model.addConstr(v_prod[i] <= self.data.pmaxhourly[i], name=f"prod_max[{i}]")
            self.cons.prod_min[i] = self.model.addConstr(-v_prod[i] <= -self.data.pmin, name=f"prod_min[{i}]")
            self.cons.imp_excess[i] = self.model.addConstr(v_imp_excess[i] >= v_import[i] - self.data.max_import, name=f"imp_excess[{i}]")
            self.cons.exp_excess[i] = self.model.addConstr(v_exp_excess[i] >= v_export[i] - self.data.max_export, name=f"exp_excess[{i}]")
            self.cons.load_max[i] = self.model.addConstr(v_load[i] <= self.data.load_max, name=f"load_max[{i}]")
            self.cons.load_min[i] = self.model.addConstr(v_load[i] >= self.data.load_min, name=f"load_min[{i}]")

        if self.question == "question_1a":
            # total energy constraint (not per-hour)
            self.cons.emin_constraint = self.model.addConstr(
                gp.quicksum(-v_load[i] for i in self.T) <= -self.data.emin, name="emin_constraint")
            for i in self.T:
                self.cons.power_balance[i] = self.model.addLConstr(v_load[i] - v_prod[i] == v_import[i] - v_export[i], name=f"power_balance_{i}")
        if self.question == "question_1b":
            print("Load profile is set to:", self.data.load_profile)
            for i in self.T:
                self.cons.deviation_pos[i] = self.model.addConstr(0 >= v_load[i] - self.data.load_profile[i]*self.data.load_max - v_deviation[i], name="deviation_pos")
                self.cons.deviation_neg[i] = self.model.addConstr(0 >= -(v_load[i] - self.data.load_profile[i]*self.data.load_max) - v_deviation[i], name="deviation_pos")
                self.cons.power_balance[i] = self.model.addLConstr(v_load[i] - v_prod[i] == v_import[i] - v_export[i], name=f"power_balance_{i}")
        if self.question == "question_1c":
            # intial and final SOC constraints, not for each hour
            self.cons.SOC_ini = self.model.addConstr(v_SOC[0] == self.data.SOC_ratio_ini*self.data.bat_capacity + (self.data.charge_eff*v_E_charged[0] - v_E_discharged[0]/self.data.discharge_eff), name="SOC_ini")
            self.cons.SOC_fin = self.model.addConstr(v_SOC[23] == self.data.SOC_ratio_fin*self.data.bat_capacity, name="SOC_fin")
            for i in self.T:
                self.cons.power_balance[i] = self.model.addLConstr(v_load[i] - v_prod[i] + v_E_charged[i] - v_E_discharged[i] == v_import[i] - v_export[i], name=f"power_balance_{i}")
                self.cons.deviation_pos[i] = self.model.addConstr(0 >= v_load[i] - self.data.load_profile[i]*self.data.load_max - v_deviation[i], name=f"deviation_pos_{i}")
                self.cons.deviation_neg[i] = self.model.addConstr(0 >= -(v_load[i] - self.data.load_profile[i]*self.data.load_max) - v_deviation[i], name=f"deviation_pos_{i}")
                self.cons.SOC_max = self.model.addConstr(0 <= self.data.bat_capacity - v_SOC[i], name=f"SOC_dynamics_{i}")
                self.cons.charge_max = self.model.addConstr(0 <= self.data.max_charge_power_ratio*self.data.bat_capacity - v_E_charged[i], name=f"charge_max_{i}")
                self.cons.discharge_max = self.model.addConstr(0 <= self.data.max_discharge_power_ratio*self.data.bat_capacity - v_E_discharged[i], name=f"discharge_max_{i}")
            for i in list(range(1,24,1)):
                ### only does SOC dynamics for hours 1-23, as 0 is handled by initial SOC constraint
                self.cons.SOC_dynamics = self.model.addConstr(v_SOC[i] == v_SOC[i-1] + (self.data.charge_eff*v_E_charged[i] - v_E_discharged[i]/self.data.discharge_eff), name=f"SOC_dynamics_{i}")
                

        self._set_objective()

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
        self.results.v_deviation = np.array([v.v_deviation[i].X for i in self.T], dtype=float)
        self.results.obj = float(self.model.ObjVal)
        self.results.prices = np.asarray(self.data.price, dtype=float).reshape(-1)
        if self.question == "question_1c":
            self.results.v_SOC = np.array([v.v_SOC[i].X for i in self.T], dtype=float)
            self.results.v_E_charged = np.array([v.v_E_charged[i].X for i in self.T], dtype=float)
            self.results.v_E_discharged = np.array([v.v_E_discharged[i].X for i in self.T], dtype=float)

        duals = Expando()
        # per-hour constraints -> arrays length |T|
        duals.prod_max       = np.array([self.cons.prod_max[i].Pi       for i in self.T], dtype=float)
        duals.prod_min       = np.array([self.cons.prod_min[i].Pi       for i in self.T], dtype=float)
        duals.load_max       = np.array([self.cons.load_max[i].Pi       for i in self.T], dtype=float)
        duals.load_min       = np.array([self.cons.load_min[i].Pi       for i in self.T], dtype=float)
        duals.imp_excess    = np.array([self.cons.imp_excess[i].Pi    for i in self.T], dtype=float)
        duals.exp_excess    = np.array([self.cons.exp_excess[i].Pi    for i in self.T], dtype=float)
        duals.power_balance = np.array([self.cons.power_balance[i].Pi for i in self.T], dtype=float)
        if self.question == "question_1b":
            duals.deviation_pos = np.array([self.cons.deviation_pos[i].Pi for i in self.T], dtype=float)
            duals.deviation_neg = np.array([self.cons.deviation_neg[i].Pi for i in self.T], dtype=float)
        # single daily energy constraint -> scalar
        if self.question == "question_1a":
            duals.emin_constraint = float(self.cons.emin_constraint.Pi)
        
        if self.question == "question_1c":
            duals.SOC_ini = float(self.cons.SOC_ini.Pi)
            duals.SOC_fin = float(self.cons.SOC_fin.Pi)
            duals.SOC_max = np.array([self.cons.SOC_max.Pi for i in self.T], dtype=float)
            duals.charge_max = np.array([self.cons.charge_max.Pi for i in self.T], dtype=float)
            duals.discharge_max = np.array([self.cons.discharge_max.Pi for i in self.T], dtype=float)
            duals.deviation_pos = np.array([self.cons.deviation_pos[i].Pi for i in self.T], dtype=float)
            duals.deviation_neg = np.array([self.cons.deviation_neg[i].Pi for i in self.T], dtype=float)
            
        self.results.duals = duals
        return self.results
    
    def update_data(self, data_name: str, new_value):
        # update Python-side data
        if not hasattr(self.data, data_name):
            raise AttributeError(f"No such data field on input data: {data_name}")
        setattr(self.data, data_name, new_value)
        print(f"Updated {data_name} to {new_value}")

        # propagate to model (bounds/RHS/objective)
        if data_name == "pmaxhourly":
            for i in self.T:
                # v_prod[i] <= pmaxhourly[i]  (RHS)
                self.cons.prod_max[i].RHS = float(self.data.pmaxhourly[i])

        elif data_name == "emin":
            self.cons.emin_constraint.RHS = float(self.data.emin)

        elif data_name in {"load_min", "load_max"}:
            # bounds on v_load
            for i in self.T:
                self.cons.load_min[i].RHS = float(self.data.load_min)
                self.cons.load_max[i].RHS = float(self.data.load_max)

        elif data_name == "max_import":
            # v_imp_excess - v_import >= -max_import
            for i in self.T:
                self.cons.imp_excess[i].RHS = -float(self.data.max_import)

        elif data_name == "max_export":
            # v_exp_excess - v_export >= -max_export
            for i in self.T:
                self.cons.exp_excess[i].RHS = -float(self.data.max_export)

        elif data_name in {"price", "imp_tariff", "exp_tariff", "excess_imp_tariff", "excess_exp_tariff", "alpha"}:
            # prices/tariffs affect the objective coefficients
            self._set_objective()
        elif data_name == "load_profile":
            for i in self.T:
                # Rebuild the RHS if you changed load_profile
                self.cons.deviation_pos[i].RHS = 0
                self.cons.deviation_neg[i].RHS = 0

        self.model.update()
    
    

    