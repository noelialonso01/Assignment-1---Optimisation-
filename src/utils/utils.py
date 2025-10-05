"placeholder for various utils functions"

import json
import csv
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np

# example function to load data from a specified directory
def load_dataset(question_name, input_path):
    base_path = Path(input_path) / question_name
    result = {}
 
    for file_path in base_path.glob("*"):
        stem = file_path.stem
        suffix = file_path.suffix.lower()
 
        try:
            if suffix == '.json':
                with open(file_path, 'r') as f:
                    result[stem] = json.load(f)
            elif suffix == '.csv':
                with open(file_path, 'r') as f:
                    result[stem] = list(csv.DictReader(f))
            else:
                with open(file_path, 'r') as f:
                    result[stem] = f.read()
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
 
    return result

def load_datafile(file_name, question_name, input_path):
    base_path = Path(input_path) / question_name / file_name
    result = {}

    stem = base_path.stem
    with open(base_path, "r") as f:
        result[stem] = json.load(f)
    return result

def plot_all_columns_one_graph(df: pd.DataFrame, save_path: str | None = None, show: bool = True, show_price_line = True, title: str = "Stacked flows vs time (with energy price)"):
    price_ser = df.pop("Price (DKK/kWh)")
    cols = [c for c in df.columns if not df[c].dropna().empty]
    if not cols:
        raise ValueError("No numeric columns to plot.")

    to_neg = [c for c in cols if ("load" in c.lower()) or ("export" in c.lower() and "import" not in c.lower())]
    df_plot = df.copy()
    for c in to_neg:
        df_plot[c] = -df_plot[c]
    
    x = np.arange(len(df_plot.index))
    x_labels = df_plot.index
    x_label = df.index.name or "Time"

    fig, ax = plt.subplots()
    cum_pos = np.zeros(len(df_plot), dtype=float)
    cum_neg = np.zeros(len(df_plot), dtype=float)

    for col in cols:
        vals = df_plot[col].fillna(0).to_numpy(dtype=float)
        pos = np.where(vals > 0, vals, 0.0)
        neg = np.where(vals < 0, vals, 0.0)

        # positives stack upward
        if pos.any():
            ax.bar(x, pos, bottom=cum_pos, label=str(col))
            cum_pos += pos

        # negatives stack downward (skip legend duplication)
        if neg.any():
            ax.bar(x, neg, bottom=cum_neg, label=str(col))
            cum_neg += neg
    handles, labels = ax.get_legend_handles_labels()
    if show_price_line:
        price_line, = ax2.plot(x, price_ser.reindex(df.index).to_numpy(dtype=float), marker="x", color="red",label="Price (DKK/kWh)")
        price_line.set_zorder(3)  # draw line above bars
        ax2 = ax.twinx()
        ax2.tick_params(axis="y", colors="red")
        ax2.spines["right"].set_color("red")
        ax2.set_ylabel("Price (DKK/kWh)", color="red")
        # Merge legends
        h2, l2 = ax2.get_legend_handles_labels()
        handles += h2
        labels += l2
    else:
        for extra_ax in getattr(fig, "axes", [])[1:]:
            extra_ax.remove()
        # keep legend for the bars only
    ax.legend(handles, labels, loc="best")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Flows (kWh)")
    ax.set_title(title)
    ax.yaxis.set_minor_locator(AutoMinorLocator(4)) 
    ax.set_xticks(x, labels=x_labels)
    ax.grid(True, which="major", axis="y")
    ax.grid(True, which="minor", axis="y", alpha=0.4)
    ax.legend()
    fig.tight_layout()

    if handles:
        ax.legend(handles, labels, loc="best")
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)

# example function to save model results in a specified directory
def save_model_results():
    """Placeholder for save_model_results function."""
    pass

# example function to plot data from a specified directory
def plot_data():
    """Placeholder for plot_data function."""
    pass