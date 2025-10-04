"""
Placeholder for main function to execute the model runner. This function creates a single/multiple instance of the Runner class, prepares input data,
and runs a single/multiple simulation.

Suggested structure:
- Import necessary modules and functions.
- Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
- Prepare input data for a single simulation or multiple simulations.
- Execute main function when the script is run directly.
"""

from utils.utils import plot_all_columns_one_graph
from data_ops.opt_model import DataProcessor
from data_ops.opt_model import OptModel
from data_ops.opt_model import OptModel2

import pandas as pd


from pathlib import Path

"""Here you need to set your path to the data folder to be able to run the code below"""
path = r"C:\Users\alex\OneDrive\Desktop\DTU\Optimistation\Assignment-1---Optimisation-\data"

def question1_a_iv():
    question = "question_1a"
    data = DataProcessor(input_path=path, question=question).getCoefficients()
    model = OptModel(data)
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
    plot_all_columns_one_graph(results_df, save_path=Path(path)/"figures"/"question1)a)iv)", show=True)
    pass


question = "question_1a"
data = DataProcessor(input_path=path, question=question).getCoefficients()
model = OptModel2(data)
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

print("Duals for Prod_max constraints:", results.duals.prod_max)
print("Dual for emin constraint:", results.duals.emin_constraint)
print("Duals for imp_excess constraints:", results.duals.imp_excess)
print("Duals for exp_excess constraints:", results.duals.exp_excess)
#print(f"Total daily expenditure for question 1)a)iv) (DKK): {results.obj:,.2f}")
#plot_all_columns_one_graph(results_df, save_path=Path(path)/"figures"/"question1)a)iv)", show=True)
