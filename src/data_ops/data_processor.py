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

        appliance_params = self.data_loader._load_data_file(self.question, "appliance_params.json")
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
        # --- Load and unwrap ---
        appliance_params = self.data_loader._load_data_file(self.question, "appliance_params.json")
        appliance_params_unwrapped = appliance_params["appliance_params"]

        # --- Horizon (defaults to 24 if self.T not set) ---
        T = len(self.T) if hasattr(self, "T") else 24
        hours = pd.RangeIndex(0, T, name="hour")

        # --- Fetch pmax(t): must be a 24-vector in JSON ---
        pmax = _get_any(appliance_params_unwrapped, ["pmax", "p_max", "pmax_t", "pmax_profile"])
        pmax = np.asarray(pmax, dtype=float)
        if pmax.size != 24:
            raise ValueError(f"'pmax' must be length-24, got length {pmax.size}")

        # --- Fetch emin (scalar in JSON) ---
        emin_day = _get_any(appliance_params_unwrapped, ["emin", "Emin", "emin_day", "E_min"])
        emin_day = float(emin_day)  # scalar
        self.emin_day = emin_day    # keep the scalar available elsewhere

        # --- Fetch lmin, lmax (scalars in JSON), then broadcast to 24h vectors ---
        lmin_scalar = float(_get_any(appliance_params_unwrapped, ["lmin", "Lmin", "L_min"]))
        lmax_scalar = float(_get_any(appliance_params_unwrapped, ["lmax", "Lmax", "L_max"]))

        lmin_vec = np.full(T, lmin_scalar, dtype=float)
        lmax_vec = np.full(T, lmax_scalar, dtype=float)

        # --- Build the hourly DataFrame (emin repeated only for convenience/visibility) ---
        constraints = pd.DataFrame({
            "pmax": pmax[:T],      # if T==24 this is a no-op; keeps code flexible
            "lmin": lmin_vec,
            "lmax": lmax_vec,
            "emin_day": emin_day,  # informational; the true constraint is daily, not hourly
        }, index=hours)

        # Optional sanity checks
        if np.any(lmin_vec > lmax_vec):
            raise ValueError("Found lmin > lmax after broadcasting.")
        # If you want to ensure feasibility wrt emin, you could check:
        # if emin_day < lmin_vec.sum() or emin_day > lmax_vec.sum():
        #     raise ValueError("emin_day is infeasible given lmin/lmax bounds over the day.")

        # Keep for downstream access
        self.constraints = constraints

        return constraints

    def getObjCoefficients(self):
        """
        Collect hourly price data,
        buy and sell tariffs,
        penalty excess costs for import and export
        """
        return obj_coefficients


        
        
path = r"C:\Users\inesm\Desktop\Optimization\Assignment-1---Optimisation-\data"
question = "question_1a"
data = DataProcessor(input_path=path, question=question)


variables = data.getVariables()
print("Variables:", variables)

constraints = data.getConstraints()
print("Constraints DataFrame:")
print(constraints)
