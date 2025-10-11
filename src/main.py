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
#from data_ops.opt_model import OptModel
from data_ops.opt_model import OptModel2
from runner.runnerQ1a import RunnerQ1a
from runner.runnerQ1b import RunnerQ1b
from runner.runnerQ1c import RunnerQ1c

import pandas as pd


from pathlib import Path

"""Here you need to set your path to the data folder to be able to run the code below"""
path = r"C:\Users\alex\OneDrive\Desktop\DTU\Optimistation\Assignment-1---Optimisation-\data"

#Question_1a = RunnerQ1a(path)
#Question_1a.question1_a_iv()
#Question_1a.question1_a_v_vary_price_profile()

#Question_1b = RunnerQ1b(path)
#Question_1b.question1_b_iv()
#Question_1b.question1_b_v_varying_alpha()

Question_1c = RunnerQ1c(path)
Question_1c.question1_c_iv()





