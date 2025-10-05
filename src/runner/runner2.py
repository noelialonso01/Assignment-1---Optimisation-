from pathlib import Path
from typing import Dict, List

from utils.utils import plot_all_columns_one_graph
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
        print(f"Total daily expenditure for question 1)a)iv) (DKK): {results.obj:,.2f}")
        deviations = results.v_deviation
        print("Deviations from the average load profile (in kW) for each hour:")
        for hour, deviation in enumerate(deviations):
            print(f"Hour {hour}: Deviation = {deviation:.4f} kW")
        print("Hourly load is",results.v_load)
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"question1)b)iv)", show=True, show_price_line=False,title="Stacked flows vs time (original data used)")
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
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"question1)a)FixedHourlyLoad", show=True, show_price_line=False, title="Stacked flows vs time (fixed hourly load)")
        pass


    def question1_a_v_no_import_tariff(self):
        """
        Redefine the load min and max, emin to the original values
        Now change the tariffs to see how this affects the optimal solution
        Here we set the tariffs to 0, meaning there is no extra cost to import
        """
        data = DataProcessor(input_path=self.path, question=self.question).getCoefficients()
        model = OptModel2(data, self.question)
        model._build()
        model.update_data("imp_tariff", 0)
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
        print(f"Total daily expenditure (DKK): {results.obj:,.2f}")
        plot_all_columns_one_graph(results_df, save_path=Path(self.path)/"figures"/"question1)a)NoImportTariff", show=True,
                                    show_price_line=False, title="Stacked flows vs time (no import tariff)")
        pass