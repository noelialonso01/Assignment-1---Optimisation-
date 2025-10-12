from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_all_duals
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path
import numpy as np

import pandas as pd


class RunnerQ1c:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.path = path
        self.question = "question_1c"
    def question1_c(self):
        """Run the scenario with original prices and alpha = 5 from 1)a)"""
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
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)PrimalResultsw=5,prices=original", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q1)c) (w=5, prices=original) daily expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            "SOC max dual (ψ_up)": results.duals.SOC_max,
            "SOC initial dual (ς_begin)": results.duals.SOC_ini,
            "SOC final dual (ς_end)": results.duals.SOC_fin,
            "Charge max dual (φ_c,up)": results.duals.charge_max,
            "Discharge max dual (φ_r,up)": results.duals.discharge_max,
            "SOC dynamics dual (ζ)": results.duals.SOC_dynamics,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)c)DualResultsw=5,prices=original", show=True, title="Dual Results 1)c) (w=5, prices=original)")

        """
        Now we run the scenario with some negative prices from 1)a)
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
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)PrimalResultsw=5,prices=someneg", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q1)c) (w=5, prices=some negative) daily expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            "SOC max dual (ψ_up)": results.duals.SOC_max,
            "SOC initial dual (ς_begin)": results.duals.SOC_ini,
            "SOC final dual (ς_end)": results.duals.SOC_fin,
            "Charge max dual (φ_c,up)": results.duals.charge_max,
            "Discharge max dual (φ_r,up)": results.duals.discharge_max,
            "SOC dynamics dual (ζ)": results.duals.SOC_dynamics,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)c)DualResultsw=5,prices=someneg", show=True, title="Dual Results 1)c) (w=5, prices=some negative)")


        """
        Now we run the scenario with alpha = 2 from 1)b)
        """
        variable_name = "alpha" 
        alpha = 2
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
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
        print(f"Total daily expenditure for question 1)a)iv) (DKK): {expenditure}")
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)PrimalResultsw=2,prices=original", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q1)c) (w=2, prices=original) daily expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            "SOC max dual (ψ_up)": results.duals.SOC_max,
            "SOC initial dual (ς_begin)": results.duals.SOC_ini,
            "SOC final dual (ς_end)": results.duals.SOC_fin,
            "Charge max dual (φ_c,up)": results.duals.charge_max,
            "Discharge max dual (φ_r,up)": results.duals.discharge_max,
            "SOC dynamics dual (ζ)": results.duals.SOC_dynamics,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)c)DualResultsw=2,prices=original", show=True, title="Dual Results 1)c) (w=2, prices=original)")
    pass

