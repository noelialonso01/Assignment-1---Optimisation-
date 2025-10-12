from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_all_duals
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path
import numpy as np
import copy


import pandas as pd


class RunnerQ1a:
    def __init__(self, path) -> None:
        self.question = "question_1a"
        self.path = path
    def question1_a(self):
        """Run the scenario with original prices"""
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        results = model.solve(verbose=True)
        primal_results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Price (DKK/kWh)": results.prices
        }, index=pd.Index(range(24), name="Hour"))
        expenditure = -results.obj
        print(primal_results_df)
        plot_all_columns_one_graph(primal_results_df, save_path=Path(self.path)/"figures"/"1)a)PrimalResultsOGCosts", show=True, show_price_line=True,
                                   line_label="Price (DKK/kWh)",title=f"Primal Results 1)a) (original cost structure), Daily Expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Load UB Dual (α_up)": results.duals.load_max,
            "Emin Dual (β)": results.duals.emin_constraint,
            "Production UB dual (μ_up) ": results.duals.prod_max,
            "Production LB dual (μ_low)": results.duals.prod_min,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)a)DualResultsOGCosts", show=True, title="Dual Results 1)a) (original cost structure)")

        """Now we run the scenario with some negative prices"""
        variable_name = "price" 
        scenario_price_profile = [1.1, 1.05, 1.0, 0.9, -0.85, -1.01, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2]
        model.update_data(variable_name, scenario_price_profile)
        results2 = model.solve(verbose=True)
        primal_results_scenario_df = pd.DataFrame({
            "Load": results2.v_load,
            "Production": results2.v_prod,
            "Import": results2.v_import,
            "Export": results2.v_export,
            "Import Excess": results2.v_imp_excess,
            "Export Excess": results2.v_exp_excess,
            "Price (DKK/kWh)": results2.prices
        }, index=pd.Index(range(24), name="Hour"))
        expenditure = -results2.obj
        plot_all_columns_one_graph(primal_results_scenario_df, save_path=Path(self.path)/"figures"/"1)a)PrimalResultsnegprices", show=True, show_price_line=True,title=f"Primal Results 1)a) (introducing some negative prices), Daily Expenditure = {expenditure:.2f} DKK")
        
        dual_results_scenario_df = pd.DataFrame({
            "Power Balance Dual (λ)": results2.duals.power_balance,
            "Load UB Dual (α_up)": results2.duals.load_max,
            "Emin Dual (β)": results2.duals.emin_constraint,
            "Production UB dual (μ_up) ": results2.duals.prod_max,
            "Production LB dual (μ_low)": results2.duals.prod_min,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_scenario_df, save_path=Path(self.path)/"figures"/"1)a)DualResultsnegprices", show=True, title="Dual Results 1)a) (introducing some negative prices)")
        
        pass


 


    