from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_objective_value_sensitivity
from utils.utils import plot_load_scenarios
from utils.utils import plot_dual_scenarios
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path

import pandas as pd


class RunnerQ1c:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.path = path
        self.question = "question_1c"
    def question1_c_iv(self):
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
            "Price (DKK/kWh)": results.prices,
            "Charged to battery (kWh)": results.v_E_charged,
            "Discharged from battery (kWh)": results.v_E_discharged,
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
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)iv)", show=True, show_price_line=False,title="Stacked flows vs time Q1)b) (original data used)")
    pass