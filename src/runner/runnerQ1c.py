from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_objective_value_sensitivity
from utils.utils import plot_load_scenarios
from utils.utils import plot_dual_scenarios
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
            #"Price (DKK/kWh)": results.prices,
            #"Charged to battery (kWh)": results.v_E_charged,
            #"Discharged from battery (kWh)": results.v_E_discharged,
            "Battery SOC (kWh)": results.v_SOC
        }, index=pd.Index(range(24), name="Hour"))
        

        deviations = results.v_deviation
        obj_value = results.obj
        expenditure = obj_value - sum(deviations[i]*100 for i in range(len(deviations)))
        print(f"Total daily expenditure for question 1)a)iv) (DKK): {expenditure}")
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)c)iv)", show=True, show_price_line=True,
                                   line_label="Battery SOC (kWh)",title="Stacked flows vs time Q1)c) (original data used)")
    pass


    def question1_c_v_varying_alpha(self):
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
            expenditure_list.append(-expenditure)
        deviations = pd.DataFrame(deviations_columns_dict, index=pd.Index(range(24), name="Hour"))
        load = pd.DataFrame(load_profile_dict, index=pd.Index(range(24), name="Hour"))
        deviation_pos_dual = pd.DataFrame(deviation_pos_dual_dict, index=pd.Index(range(24), name="Hour"))
        deviation_neg_dual = pd.DataFrame(deviation_neg_dual_dict, index=pd.Index(range(24), name="Hour"))
        
        plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         save_path=Path(self.path)/"figures"/"1)b)ObjValues")
        #plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)c)LoadScenarios")
        plot_dual_scenarios(deviation_pos_dual, save_path=Path(self.path)/"figures"/"1)c)DualValuesDevPos", title = "Deviation Positive dual values for the different weight scenarios")
        plot_dual_scenarios(deviation_neg_dual, save_path=Path(self.path)/"figures"/"1)c)DualValuesDevNeg", title = "Deviation Negative dual values for the different weight scenarios")
        pass


    def question1_c_v_vary_price_profile(self):
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        variable_dict = {
        "original_price_profile": [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2],}
        
        factors = [0.2, 0.5, 0.8, 1.5, 2]
        # Generate price scenarios as multiples of the original price profile
        for i, factor in enumerate(factors, start=1):
            variable_dict[f"Scenario {i} (x{factor})"] = [round(p * factor, 2) for p in variable_dict["original_price_profile"]]
        """
        Extracting the costs and load profile for different price profiles
        Plot all price profiles on one graph, to showcase the different trials done
        Plot all found load profiles associated with this to showcase the outputs       
        """
        variable_name = "price"
        #plot_price_scenarios(variable_dict, save_path=Path(self.path)/"figures"/"1)a)PriceScenarios")
        load_profile_columns_dict = {}
        expenditure_list = []
        power_balance_dual_dict = {}
        load_max_dual_dict = {}
        #import_excess_dual_dict = {}
        for key in variable_dict:
            model.update_data(variable_name, variable_dict[key])
            results = model.solve(verbose=True)
            load = results.v_load
            expenditure = results.obj
            power_blance_dual = results.duals.power_balance
            load_max_dual = results.duals.load_max
            load_profile_columns_dict[key] = load
            power_balance_dual_dict[key] = power_blance_dual
            load_max_dual_dict[key] = load_max_dual
            expenditure_list.append(-expenditure)
        load = pd.DataFrame(load_profile_columns_dict, index=pd.Index(range(24), name="Hour"))
        power_balance_dual = pd.DataFrame(power_balance_dual_dict, index=pd.Index(range(24), name="Hour"))
        load_max_dual = pd.DataFrame(load_max_dual_dict, index=pd.Index(range(24), name="Hour"))
        np.set_printoptions(precision=4, suppress=False)
        plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         save_path=Path(self.path)/"figures"/"1)c)ObjValues")
        plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)c)LoadScenarios")
        plot_dual_scenarios(power_balance_dual, save_path=Path(self.path)/"figures"/"1)c)DualValues", title = "Power balance dual values for the different price scenarios")
        #plot_dual_scenarios(import_excess_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Import Excess dual values for the different price scenarios")
        plot_dual_scenarios(load_max_dual, save_path=Path(self.path)/"figures"/"1)c)LoadMaxDualValues", title = "load_max_dual values for the different price scenarios")