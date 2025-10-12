from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_all_duals
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path

import pandas as pd


class RunnerQ1b:
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.path = path
        self.question = "question_1b"
    def question1_b(self):
        """Run the scenario with original prices and alpha = 5"""
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
            "Deviation Up (kWh)": results.v_deviation_pos,
            "Deviation Down (kWh)": results.v_deviation_neg,
        }, index=pd.Index(range(24), name="Hour"))
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)b)Primalw=5", show=True, show_price_line=True,
                                   line_label="Deviation Down (kWh)",title=f"Primal Results Q1)b) (w=5), daily expenditure = {expenditure:.2f} DKK")

        dual_results_df = pd.DataFrame({
            "Load UB Dual (α_up)": results.duals.load_max,
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            "Production LB dual (μ_low)": results.duals.prod_min,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)b)DualResultsw=5", show=True, title="Dual Results 1)b) (w=5)")

        """Now we run the scenario with alpha = 2"""
        variable_name = 'alpha'
        alpha = 2
        model.update_data(variable_name, alpha)
        results = model.solve(verbose=True)
        results_df = pd.DataFrame({
            "Load": results.v_load,
            "Production": results.v_prod,
            "Import": results.v_import,
            "Export": results.v_export,
            "Import Excess": results.v_imp_excess,
            "Export Excess": results.v_exp_excess,
            "Deviation Up (kWh)": results.v_deviation_pos,
            "Deviation Down (kWh)": results.v_deviation_neg,
        }, index=pd.Index(range(24), name="Hour"))
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        print(deviations)
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*alpha for i in range(len(deviations)))
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)b)Primalw=2", show=True, show_price_line=True,
                                   line_label="Deviation Down (kWh)",title=f"Primal Scenario Results neg line Q1)b) (w=2), daily expenditure = {expenditure:.2f} DKK")

        dual_results_df = pd.DataFrame({
            "Load UB Dual (α_up)": results.duals.load_max,
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            "Production LB dual (μ_low)": results.duals.prod_min,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)b)DualResultsw=2", show=True, title="Dual Scenario Results 1)b) (w=2)")
        
    pass
