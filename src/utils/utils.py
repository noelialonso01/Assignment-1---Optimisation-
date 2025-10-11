"placeholder for various utils functions"

import json
import csv
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np

"""
Here we have two functions for loading a dataset and loading a file
"""
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


"""
Now we have some plotting functions
"""
def plot_all_columns_one_graph(df: pd.DataFrame, save_path: str | None = None, show: bool = True, 
                               show_price_line = True, title: str = "Stacked flows vs time (with energy price)",
                               line_label: str = "Price (DKK/kWh)"):
    if show_price_line == True:
        price_ser = df.pop(line_label)
    cols = [c for c in df.columns if not df[c].dropna().empty]
    if not cols:
        raise ValueError("No numeric columns to plot.")

    to_neg = [c for c in cols if ("load" in c.lower()) or ("export" in c.lower()) or ("Charged to battery" in c.lower())]
    df_plot = df.copy()
    for c in to_neg:
        df_plot[c] = -df_plot[c]
    
    x = np.arange(len(df_plot.index))
    x_labels = df_plot.index
    x_label = df.index.name or "Time"

    fig, ax = plt.subplots(figsize=(10, 6))
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
    ax2 = None
    if show_price_line:
        ax2 = ax.twinx()
        price_line, = ax2.plot(x, price_ser.reindex(df.index).to_numpy(dtype=float), marker="x", color="red", linestyle="--" ,label=line_label)
        price_line.set_zorder(3)  # draw line above bars
        ax2.tick_params(axis="y", colors="red")
        ax2.spines["right"].set_color("red")
        ax2.set_ylabel(line_label, color="red")
        ax2.set_ylim(-1.5, 3)
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
        ax.legend(handles, labels, bbox_to_anchor=(1.07, 1), loc='upper left')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_objective_value_sensitivity(variable_dict, variable_name: str, obj_values = None,
                               save_path: str | None = None, show: bool = True):
    
    plt.figure(figsize=(6, 2))
    y_position = 1  # fixed y-coordinate for all points
    scenario_names = list(variable_dict.keys())
    plt.axhline(y=y_position, color='gray', linestyle='--', linewidth=1)
    # Plot each scenario as a point at the same y-coordinate

    for name, value in zip(scenario_names, obj_values):
        if name == "original_price_profile":
            plt.scatter(value, y_position, marker='x', s=100, label=name)
        else:
            plt.scatter(value, y_position, marker='o', s=80, label=name)
    plt.xlabel("Daily Consumer Costs (DKK)")
    plt.yticks([])
    plt.title("Sensitivity Analysis of Objective Value Across Price Scenarios")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # put legend outside plot
    plt.grid(True, axis ="x", linestyle='--', alpha=0.5)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

def plot_emin_sensitivity(variable_dict, variable_name: str, obj_values = None,
                               save_path: str | None = None, show: bool = True):
    
    plt.figure(figsize=(6, 2))
    y_position = 1  # fixed y-coordinate for all points
    scenario_names = list(variable_dict.keys())
    plt.axhline(y=y_position, color='gray', linestyle='--', linewidth=1)
    # Plot each scenario as a point at the same y-coordinate

    for name, value in zip(scenario_names, obj_values):
        if name == "original_price_profile":
            plt.scatter(value, y_position, marker='x', s=100, label=name)
        else:
            plt.scatter(value, y_position, marker='o', s=80, label=name)
    plt.xlabel("Emin constraint dual value")
    plt.yticks([])
    plt.title("Sensitivity Analysis of Emin Constraint Dual Across Price Scenarios")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # put legend outside plot
    plt.grid(True, axis ="x", linestyle='--', alpha=0.5)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_price_scenarios(variable_dict, save_path: str | None = None, show: bool = True):
    hours = np.arange(24)
    plt.figure(figsize=(12, 6))

    for col in variable_dict.keys():
        if col == "original_price_profile":
            plt.plot(hours, variable_dict[col], marker='o', linestyle='-', label='Original', linewidth=2)
        else:
            plt.plot(hours, variable_dict[col], marker='x', linestyle='--', alpha=0.7, label=col)
    # Graph features
    plt.xlabel('Hour of Day')
    plt.ylabel('Price (DKK)')
    plt.title('Price Scenarios over 24 Hours')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()
    
def plot_load_scenarios(load_df, save_path: str | None = None, show: bool = True):
    hours = load_df.index.values
    plt.figure(figsize=(12, 6))
    # Plot original profile
    for col in load_df.columns:
        if col == "original_price_profile":
            plt.plot(hours, load_df[col], marker='o', linestyle='-', label='Original', linewidth=2)
        else:
            plt.plot(hours, load_df[col], marker='x', linestyle='--', alpha=0.7, label=col)
    # Graph features
    plt.xlabel('Hour of Day')
    plt.ylabel('Load (kWh)')
    plt.title('Optimal load profiles for the different price scenarios')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

def plot_dual_scenarios(dual_df, save_path: str | None = None, show: bool = True, title: str = "Dual values for the different price scenarios"):
    hours = dual_df.index.values
    plt.figure(figsize=(12, 6))
    # Plot original profile
    for col in dual_df.columns:
        if col == "original_price_profile":
            plt.plot(hours, dual_df[col], marker='o', linestyle='-', label='Original', linewidth=2)
        else:
            plt.plot(hours, dual_df[col], marker='x', linestyle='--', alpha=0.7, label=col)
    # Graph features
    plt.xlabel('Hour of Day')
    plt.ylabel('Dual Value')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

def plot_all_duals(dual_dict, save_path: str | None = None, show: bool = True, title: str = "Dual values for the different price scenarios"):
    hours = np.arange(24)
    plt.figure(figsize=(12, 6))
    markers = ['o', 'x', 's', '^', 'v', 'D', '*', 'p', '+', '>']
    linestyles = ['-', '--', '-.', ':']
    for idx, key in enumerate(dual_dict):
        marker = markers[idx % len(markers)]
        linestyle = linestyles[idx % len(linestyles)]
        plt.plot(hours, dual_dict[key], marker=marker, linestyle=linestyle, alpha=0.7, label=key)
    # Graph features
    plt.xlabel('Hour of Day')
    plt.ylabel('Dual Value')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()