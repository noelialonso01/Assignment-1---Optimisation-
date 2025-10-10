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
        variable_dict = {"Scenario 1 (w=0.1)": 0.1, "Scenario 2 (w=0.5)": 0.5, 
                         "Scenario 3 (w=1)": 1, "Scenario 4 (w=2)": 2, 
                         "Scenario 5 (w=3)": 3, "Scenario 6 (w=5)": 5, 
                         "Scenario 7 (w=10)": 10}
        
        variable_name = 'alpha'
        """
        Extracting the deviation values and expenditure for different alphas
        Want to plot deviation vs time for different alpha values (each one line)
        Also an expenditure sensitivity plot as usual
        """
        deviations_columns_dict = {}
        expenditure_list = []
        deviation_pos_dual_dict = {}
        deviation_neg_dual_dict = {}
        load_profile_dict = {}
        for key in variable_dict:
            model.update_data(variable_name, variable_dict[key])
            results = model.solve(verbose=True)
            deviations = results.v_deviation
            obj_value = results.obj
            load = results.v_load
            expenditure = obj_value - sum(deviations[i]*variable_dict[key] for i in range(len(deviations)))
            deviation_pos_dual = results.duals.deviation_pos
            deviation_neg_dual = results.duals.deviation_neg
            deviation_pos_dual_dict[key] = deviation_pos_dual
            deviation_neg_dual_dict[key] = deviation_neg_dual
            deviations_columns_dict[key] = deviations
            load_profile_dict[key] = load
            expenditure_list.append(expenditure)
        deviations = pd.DataFrame(deviations_columns_dict, index=pd.Index(range(24), name="Hour"))
        load = pd.DataFrame(load_profile_dict, index=pd.Index(range(24), name="Hour"))
        deviation_pos_dual = pd.DataFrame(deviation_pos_dual_dict, index=pd.Index(range(24), name="Hour"))
        deviation_neg_dual = pd.DataFrame(deviation_neg_dual_dict, index=pd.Index(range(24), name="Hour"))
        
        plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         save_path=Path(self.path)/"figures"/"1)b)ObjValues")
        plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)b)LoadScenarios")
        plot_dual_scenarios(deviation_pos_dual, save_path=Path(self.path)/"figures"/"1)b)DualValuesDevPos", title = "Deviation Positive dual values for the different weight scenarios")
        plot_dual_scenarios(deviation_neg_dual, save_path=Path(self.path)/"figures"/"1)b)DualValuesDevNeg", title = "Deviation Negative dual values for the different weight scenarios")
        pass