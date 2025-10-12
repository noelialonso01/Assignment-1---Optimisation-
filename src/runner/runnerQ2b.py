from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_all_duals
from utils.utils import plot_objective_value_sensitivity
from utils.utils import plot_load_scenarios
from utils.utils import plot_dual_scenarios
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
    def question1_c(self):
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
            #"Price (DKK/kWh)": results.prices,
            #"Charged to battery (kWh)": results.v_E_charged,
            #"Discharged from battery (kWh)": results.v_E_discharged,
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        
        deviations_pos = results.v_deviation_pos
        deviations_neg = results.v_deviation_neg
        deviations = [deviations_pos[i] + deviations_neg[i] for i in range(len(deviations_pos))]
        obj_value = results.obj
        expenditure = -obj_value - sum(deviations[i]*5 for i in range(len(deviations)))
        battery_size = results.v_battery_size
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)PrimalResultsw=5,prices=original", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title=f"Stacked flows vs time Q1)c) (w=5, prices=original) daily expenditure = {expenditure:.2f} DKK, battery size = {battery_size:.2f} kWh")
        
        dual_results_df = pd.DataFrame({
            #"Load UB Dual (α_up)": results.duals.load_max,
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB Dual (μ_up) ": results.duals.prod_max,
            "Deviation Dual (η) ": results.duals.deviation,
            #"Production LB dual (μ_low)": results.duals.prod_min,
            #"SOC min dual (ψ_low)": results.duals.SOC_min,
            "SOC max dual (ψ_up)": results.duals.SOC_max,
            "SOC initial dual (ς_begin)": results.duals.SOC_ini,
            "SOC final dual (ς_end)": results.duals.SOC_fin,
            "Charge max dual (φ_c,up)": results.duals.charge_max,
            "Discharge max dual (φ_r,up)": results.duals.discharge_max,
            "SOC dynamics dual (ζ)": results.duals.SOC_dynamics,
        }, index=pd.Index(range(24), name="Hour"))
        #plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)c)DualResultsw=5,prices=original", show=True, title="Dual Results 1)c) (w=5, prices=original)")
        pass
