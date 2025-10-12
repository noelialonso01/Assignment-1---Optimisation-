from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
#from utils.utils import plot_objective_value_sensitivity
#from utils.utils import plot_emin_sensitivity
#from utils.utils import plot_price_scenarios
#from utils.utils import plot_load_scenarios
#from utils.utils import plot_dual_scenarios
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
        #data_original = copy.deepcopy(DataProcessor(input_path=self.path, question=self.question).getCoefficients())
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


    def question1_a_scenario(self):
        pass


        """
        scenario_2_price_profile = [p * 2 for p in original_price_profile]
        model.update_data(variable_name, scenario_2_price_profile)
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
        plot_all_columns_one_graph(primal_results_df, save_path=Path(self.path)/"figures"/"1)a)PrimalResults2xprices", show=True, show_price_line=True,title=f"Primal Results 1)a) (2 x hourly prices), Daily Expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Load UB Dual (α_up)": results.duals.load_max,
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB dual (μ_up) ": results.duals.prod_max,
            "Emin Dual (β)": results.duals.emin_constraint,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)a)DualResults2xprices", show=True, title="Dual Results 1)a) (2 x hourly prices)")
        
        original_price_profile = [1.1, 1.05, 1.0, 0.9, 0.85, 1.01, 1.05, 1.2, 1.4, 1.6,
                                1.5, 1.1, 1.05, 1.0, 0.95, 1.0, 1.2, 1.5, 2.1, 2.5,
                                2.2, 1.8, 1.4, 1.2]
        scenario_1_price_profile = [p * 0.5 for p in original_price_profile]
        
           
        model.update_data(variable_name, scenario_1_price_profile)
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
        plot_all_columns_one_graph(primal_results_df, save_path=Path(self.path)/"figures"/"1)a)PrimalResults0,5xprices", show=True, show_price_line=True,title=f"Primal Results 1)a) (0.5 x hourly prices), Daily Expenditure = {expenditure:.2f} DKK")
        
        dual_results_df = pd.DataFrame({
            "Load UB Dual (α_up)": results.duals.load_max,
            "Power Balance Dual (λ)": results.duals.power_balance,
            "Production UB dual (μ_up) ": results.duals.prod_max,
            "Emin Dual (β)": results.duals.emin_constraint,
        }, index=pd.Index(range(24), name="Hour"))
        plot_all_duals(dual_results_df, save_path=Path(self.path)/"figures"/"1)a)DualResults0,5xprices", show=True, title="Dual Results 1)a) (0.5 x hourly prices)")

        """


    """

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

        variable_name = "price"
        #plot_price_scenarios(variable_dict, save_path=Path(self.path)/"figures"/"1)a)PriceScenarios")
        load_profile_columns_dict = {}
        expenditure_list = []
        power_balance_dual_dict = {}
        load_max_dual_dict = {}
        emin_dual_list = []
        prod_max_dual_dict = {}
        for key in variable_dict:
            model.update_data(variable_name, variable_dict[key])
            results = model.solve(verbose=True)
            load = results.v_load
            expenditure = results.obj
            power_blance_dual = results.duals.power_balance
            load_max_dual = results.duals.load_max
            pmax_dual = results.duals.prod_max
            load_profile_columns_dict[key] = load
            power_balance_dual_dict[key] = power_blance_dual
            load_max_dual_dict[key] = load_max_dual
            prod_max_dual_dict[key] = pmax_dual
            expenditure_list.append(-expenditure)
            emin_dual_list.append(results.duals.emin_constraint)
        load = pd.DataFrame(load_profile_columns_dict, index=pd.Index(range(24), name="Hour"))
        power_balance_dual = pd.DataFrame(power_balance_dual_dict, index=pd.Index(range(24), name="Hour"))
        load_max_dual = pd.DataFrame(load_max_dual_dict, index=pd.Index(range(24), name="Hour"))
        prod_max_dual = pd.DataFrame(prod_max_dual_dict, index=pd.Index(range(24), name="Hour"))
        #plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         #save_path=Path(self.path)/"figures"/"1)a)ObjValues")
        #plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)a)LoadScenarios")
        #plot_dual_scenarios(power_balance_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Power balance dual values for the different price scenarios")
        #plot_dual_scenarios(load_max_dual, save_path=Path(self.path)/"figures"/"1)a)LoadMaxDualValues", title = "load_max_dual values for the different price scenarios")
        plot_dual_scenarios(prod_max_dual, save_path=Path(self.path)/"figures"/"1)a)ProdMaxDualValues", title = "Production max dual values for the different price scenarios")
        plot_emin_sensitivity(variable_dict, variable_name, emin_dual_list,
                              save_path=Path(self.path)/"figures"/"1)a)EminDualValues")
        pass

"""



    