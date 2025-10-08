from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
#from utils.utils import plot_objective_value_sensitivity
from utils.utils import sensitivity_analysis_on_obj_value
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path

import pandas as pd


class RunnerQ2:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.path = path
        self.question = "question_1b"
    def question1_b_iv(self):
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        results = model.solve(verbose=True)
        results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Price (DKK/kWh)": results.prices
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations = results.v_deviation
        obj_value = results.obj
        expenditure = obj_value - sum(deviations[i]*100 for i in range(len(deviations)))
        print(f"Total daily expenditure for question 1)a)iv) (DKK): {expenditure}")
        print("Deviations from the average load profile (in kW) for each hour:")
        for hour, deviation in enumerate(deviations):
            print(f"Hour {hour}: Deviation = {deviation:.4f} kW")
        total_load = sum(results.v_load[i] for i in range(len(results.v_load)))
        print("Total daily load is:", total_load)
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)b)iv)", show=True, show_price_line=False,title="Stacked flows vs time Q1)b) (original data used)")
    pass

    def question1_b_v_varying_alpha(self):
        """
        Vary alpha (defines how strongly consumer wants to keep to load profile)
        """
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        variable_list = [0.1, 0.5, 1, 2, 3, 5, 10]
        variable_name = 'alpha'
        """
        Extracting the deviation values and expenditure for different alphas
        """
        deviations_columns_dict = {}
        expenditure_columns_dict = {}
        for variable in variable_list:
            model.update_data(variable_name, variable)
            results = model.solve(verbose=True)
            deviations = results.v_deviation
            obj_value = results.obj
            expenditure = obj_value - sum(deviations[i]*variable for i in range(len(deviations)))
            deviations_columns_dict[f"alpha={variable}"] = deviations
            expenditure_columns_dict[f"alpha={variable}"] = [expenditure]
        deviations = pd.DataFrame(deviations_columns_dict, index=pd.Index(range(24), name="Hour"))
        expenditure = pd.DataFrame(expenditure_columns_dict, index=["Daily Expenditure"])
        print("This is deviations table")
        print(deviations)
        print("This is daily expenditure table")
        print(expenditure)
        pass