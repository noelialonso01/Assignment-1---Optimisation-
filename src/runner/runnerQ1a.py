from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
from utils.utils import plot_objective_value_sensitivity
from utils.utils import plot_price_scenarios
from utils.utils import plot_load_scenarios
from utils.utils import plot_dual_scenarios
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel2
from pathlib import Path
import numpy as np


import pandas as pd


class RunnerQ1a:
    """
    Handles configuration setting, data loading and preparation, model(s) execution, results saving and ploting
    """
    def __init__(self, path) -> None:
        """Initialize the Runner."""
        self.question = "question_1a"
        self.path = path
    def question1_a_iv(self):
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
        print(f"Total daily expenditure for question 1)a)iv) (DKK): {results.obj:,.2f}")
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)a)iv)", show=True, show_price_line=True,title="Stacked flows vs time (original data used)")
    pass

    

    def question1_a_v_vary_price_profile(self):
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
        plot_price_scenarios(variable_dict, save_path=Path(self.path)/"figures"/"1)a)PriceScenarios")
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
            #import_excess_dual = results.duals.imp_excess
            load_profile_columns_dict[key] = load
            power_balance_dual_dict[key] = power_blance_dual
            #import_excess_dual_dict[key] = import_excess_dual
            load_max_dual_dict[key] = load_max_dual
            expenditure_list.append(-expenditure)
        load = pd.DataFrame(load_profile_columns_dict, index=pd.Index(range(24), name="Hour"))
        power_balance_dual = pd.DataFrame(power_balance_dual_dict, index=pd.Index(range(24), name="Hour"))
        #import_excess_dual = pd.DataFrame(import_excess_dual_dict, index=pd.Index(range(24), name="Hour"))
        load_max_dual = pd.DataFrame(load_max_dual_dict, index=pd.Index(range(24), name="Hour"))
        np.set_printoptions(precision=4, suppress=False)
        plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         save_path=Path(self.path)/"figures"/"1)a)ObjValues")
        plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)a)LoadScenarios")
        plot_dual_scenarios(power_balance_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Power balance dual values for the different price scenarios")
        #plot_dual_scenarios(import_excess_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Import Excess dual values for the different price scenarios")
        plot_dual_scenarios(load_max_dual, save_path=Path(self.path)/"figures"/"1)a)LoadMaxDualValues", title = "load_max_dual values for the different price scenarios")
        pass





    