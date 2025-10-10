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


class RunnerQ1:
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
        # Generate scenarios as multiples of the original
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
            expenditure_list.append(expenditure)
        load = pd.DataFrame(load_profile_columns_dict, index=pd.Index(range(24), name="Hour"))
        power_balance_dual = pd.DataFrame(power_balance_dual_dict, index=pd.Index(range(24), name="Hour"))
        #import_excess_dual = pd.DataFrame(import_excess_dual_dict, index=pd.Index(range(24), name="Hour"))
        load_max_dual = pd.DataFrame(load_max_dual_dict, index=pd.Index(range(24), name="Hour"))
        np.set_printoptions(precision=4, suppress=False)
        print(repr(load_max_dual))
        plot_objective_value_sensitivity(variable_dict, variable_name, expenditure_list, 
                                         save_path=Path(self.path)/"figures"/"1)a)ObjValues")
        plot_load_scenarios(load, save_path=Path(self.path)/"figures"/"1)a)LoadScenarios")
        plot_dual_scenarios(power_balance_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Power balance dual values for the different price scenarios")
        #plot_dual_scenarios(import_excess_dual, save_path=Path(self.path)/"figures"/"1)a)DualValues", title = "Import Excess dual values for the different price scenarios")
        plot_dual_scenarios(load_max_dual, save_path=Path(self.path)/"figures"/"1)a)LoadMaxDualValues", title = "load_max_dual values for the different price scenarios")
        pass





    def question1_a_v_no_export_tariff(self):
        """
        Redefine the load min and max, emin to the original values
        Now change the tariffs to see how this affects the optimal solution
        Here we set the tariffs to 0, meaning there is no extra cost to import
        """
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        model.update_data("exp_tariff", 0)
        results = model.solve(verbose=True)
        print("Original emin value of 8kWh/day is changed to a flat minimum load of 0.3333 kW per hour")
        print("Optimised daily spend is:", results.obj)
        print("Dual for emin constraint:", results.duals.emin_constraint)
        print("Duals for Prod_max constraints:", results.duals.prod_max)
        print("Duals for load max constraints:", results.duals.load_max)
        print("Duals for load min constraints:", results.duals.load_min)
        print("Duals for imp_excess constraints:", results.duals.imp_excess)
        print("Duals for exp_excess constraints:", results.duals.exp_excess)
        results_df = pd.DataFrame({
                "Load": results.v_load,
                "Production": results.v_prod,
                "Import": results.v_import,
                "Export": results.v_export,
                "Import Excess": results.v_imp_excess,
                "Export Excess": results.v_exp_excess,
                "Price (DKK/kWh)": results.prices
            }, index=pd.Index(range(24), name="Hour"))
        print(f"Total daily expenditure for (DKK): {results.obj:,.2f}")
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)a)NoExportTariff", show=True, 
                                show_price_line=False, title="Stacked flows vs time (no export tariff)")
        pass
    




    def question1_a_v_fixed_hourly_load(self):
        """
        We want to fix the load to be flat across the day to create a baseline to compare to
        We keep the daily total (emin) at 8 equiv hours, which is 24kwh in 1 day, so load in 1 hour = 24/24 = 1 kW
        Relax the emin constraint so that it is no longer binding, as we now have a fixed load
        """
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        model.update_data("load_min", 1)
        model.update_data("load_max", 1)
        model.update_data("emin", 0)
        results = model.solve(verbose=True)
        print("Original emin value of 8kWh/day is changed to a flat minimum load of 0.3333 kW per hour")
        print("Optimised daily spend is:", results.obj)
        print("Dual for emin constraint:", results.duals.emin_constraint)
        print("Duals for Prod_max constraints:", results.duals.prod_max)
        print("Duals for load max constraints:", results.duals.load_max)
        print("Duals for load min constraints:", results.duals.load_min)
        print("Duals for imp_excess constraints:", results.duals.imp_excess)
        print("Duals for exp_excess constraints:", results.duals.exp_excess)
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
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"1)a)FixedHourlyLoad", show=True, show_price_line=False, title="Stacked flows vs time (fixed hourly load)")
        pass

    def _load_config(self) -> None:
        """Load configuration (placeholder method)"""
    # Extract simulation configuration and hyperparameter values (e.g. question, scenarios for sensitivity analysis, duration of simulation, solver name, etc.) and store them as class attributes (e.g. self.scenario_list, self.solver_name, etc.)
    
    def _create_directories(self) -> None:
        """Create required directories for each simulation configuration. (placeholder method)"""

    def prepare_data_single_simulation(self, question_name) -> None:
        """Prepare input data for a single simulation (placeholder method)"""
        # Prepare input data using DataProcessor for a given simulation configuration and store it as class attributes (e.g. self.data)

    def prepare_data_all_simulations(self) -> None:
        """Prepare input data for multiple scenarios/sensitivity analysis/questions (placeholder method)"""
        # Extend data_loader to handle multiple scenarios/questions
        # Prepare data using data_loader for multiple scenarios/questions
        
    def run_single_simulation(self,Args) -> None:
        """
        Run a single simulation for a given question and simulation path (placeholder method).

        Args (examples):
            question: The question name for the simulation
            simulation_path: The path to the simulation data

        """
        # Initialize Optimization Model for the given question and simulation path
        # Run the model
        pass
    def run_all_simulations(self) -> None:
        """Run all simulations for the configured scenarios (placeholder method)."""
        pass