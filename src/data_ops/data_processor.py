import json
import csv
import pandas as pd
from pathlib import Path
import numpy as np

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

        appliance_params = self.data_loader._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        variables = [key for key, value in appliance_params_unwrapped.items() if value is not None]
        variables.extend(["bought", "sold", "exp_excess", "imp_excess"])
        variables = pd.DataFrame({"variables": variables})
        self.variables = variables
        return variables

    def getCoefficients(self):
        
        """
        Collect the constraints: 
        pmax(t), 
        emin (min energy consumed in a day), 
        max and min load (make hourly but constant every hour)
        """
        # --- Load and unwrap ---
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
        hourly_energy_price = [float(x) for x in bus_params_unwrapped[0]["energy_price_DKK_per_kWh"]]

        pmax = float(appliance_params_unwrapped["DER"][0]["max_power_kW"])
        pmaxhourly = [float(x)*pmax for x in DER_production_unwrapped[0]["hourly_profile_ratio"]]
        load_max = float(appliance_params_unwrapped["load"][0]["max_load_kWh_per_hour"])
        emin = float(usage_preferences_unwrapped[0]["load_preferences"][0]["min_total_energy_per_day_hour_equivalent"])
        return(pmaxhourly, emin, load_max, hourly_energy_price, imp_tariff, exp_tariff, max_import, max_export, excess_imp_tariff, excess_exp_tariff)



        
        
#path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
path = r"C:\Users\alex\OneDrive\Desktop\DTU\Optimistation\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataProcessor(input_path=path, question=question)


variables = data.getVariables()
print("Variables:", variables)

constraints = data.getCoefficients()
#print("Constraints DataFrame:")
#print(constraints)
