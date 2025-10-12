"""
Placeholder for main function to execute the model runner. This function creates a single/multiple instance of the Runner class, prepares input data,
and runs a single/multiple simulation.

Suggested structure:
- Import necessary modules and functions.
- Define a main function to encapsulate the workflow (e.g. Create an instance of your the Runner class, Run a single simulation or multiple simulations, Save results and generate plots if necessary.)
- Prepare input data for a single simulation or multiple simulations.
- Execute main function when the script is run directly.
"""

from runner.runnerQ1a import RunnerQ1a
from runner.runnerQ1b import RunnerQ1b
from runner.runnerQ1c import RunnerQ1c
from runner.runnerQ2b import RunnerQ2b

import pandas as pd


from pathlib import Path

"""Here you need to set your path to the data folder to be able to run the code below"""
path = r"C:\Users\alex\OneDrive\Desktop\DTU\Optimistation\Assignment-1---Optimisation-\data"

"""
Please uncomment the relevant question you want to run below. When you run the code, it will generate and save the relevant plots in the figures folder.
So you can close them all and then view the figures afterwards if yu prefer
"""

### Question 1a
"""
Question_1a = RunnerQ1a(path)
Question_1a.question1_a()
"""

### Question 1b
"""
Question_1b = RunnerQ1b(path)
Question_1b.question1_b()
"""


### Question 1c
"""
Question_1c = RunnerQ1c(path)
Question_1c.question1_c()
"""


### Question 2b
"""
Question_2b = RunnerQ2b(path)
Question_2b.question2_b()
"""






