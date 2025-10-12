from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_all_columns_one_graph_2b
from utils.utils import plot_price_scenarios
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path
import numpy as np

import pandas as pd


class RunnerQ2b:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.path = path
        self.question = "question_2b"
    def question2_b(self):
        """Run the workflow for question 2b."""
        """Initially run with alpha = 5 and original prices"""
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
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        battery_size = results.v_battery_size
        plot_all_columns_one_graph_2b(results_df, save_path=Path(self.path)/"figures"/"2)b)PrimalResultsw=5,prices=original", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q2)b) (w=5, prices=original) daily expenditure = {expenditure:.2f} DKK, battery size = {battery_size:.2f} kWh")
        
        """
        try negative prices here
        """
        variable_name = "price" 
        scenario_price_profile = [1.1, 1.05, 1.0, 0.9, -0.85, -1.01, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2]
        model.update_data(variable_name, scenario_price_profile)
        model._build()
        results = model.solve(verbose=True)
        results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        print(deviations)
        battery_size = results.v_battery_size
        plot_all_columns_one_graph_2b(results_df, save_path=Path(self.path)/"figures"/"2)b)PrimalResultsw=5,prices=someneg", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q2)b) (w=5, prices=some negative) daily expenditure = {expenditure:.2f} DKK, battery size = {battery_size:.2f} kWh")

        """
        try decreased prices in hours 4 and 5, but then increase by same amount later on
        """
        variable_name = "price" 
        scenario_price_profile = [1.1, 1.05, 1.0, 0.9, 0.2, 0.3, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 3.15,
                                2.91, 1.8, 1.4, 1.2]
        model.update_data(variable_name, scenario_price_profile)
        model._build()
        results = model.solve(verbose=True)
        results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        print(deviations)
        battery_size = results.v_battery_size
        plot_all_columns_one_graph_2b(results_df, save_path=Path(self.path)/"figures"/"2)b)PrimalResultsw=5,prices=extremepeaks", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q2)b) (w=5, prices=extreme peaks) daily expenditure = {expenditure:.2f} DKK, battery size = {battery_size:.2f} kWh")
        
        """
        Now we run the scenario with alpha = 2 from 1)b)
        """
        variable_name = "alpha" 
        alpha = 2
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        """Reset model to original prices"""
        model2 = OptModel2(data, self.question)
        model2._build()
        model2.update_data(variable_name, alpha)
        model2._build()
        results = model2.solve(verbose=True)
        results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        print("Deviations are:",deviations)
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        battery_size = results.v_battery_size
        plot_all_columns_one_graph_2b(results_df, save_path=Path(self.path)/"figures"/"2)b)PrimalResultsw=2,prices=original", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q2)b) (w=2, prices=original) daily expenditure = {expenditure:.2f} DKK, , battery size = {battery_size:.2f} kWh")
        price_scenario_dict = {
            "original": [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2]
            ,"some negative": [1.1, 1.05, 1.0, 0.9, -0.85, -1.01, 1.05, 1.2, 1.4, 1.6, 
                         1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2]
            ,"extreme peaks (= daily total of original)": [1.1, 1.05, 1.0, 0.9, 0.2, 0.3, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 3.15,
                                2.91, 1.8, 1.4, 1.2]    
        }
        plot_price_scenarios(price_scenario_dict, save_path=Path(self.path)/"figures"/"2)b)PriceScenarios", show=True, title="Price Scenarios Q2)b)")
        pass
