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
        if line_label == "Deviation Down (kWh)":
            price_ser2 = df.pop("Deviation Up (kWh)")
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
        if line_label == "Deviation Down (kWh)":
            ax2.plot(x, price_ser2.reindex(df.index).to_numpy(dtype=float), marker="o", color="purple", linestyle="--" ,label="Deviation Up (kWh)")
        price_line.set_zorder(3)  # draw line above bars
        ax2.tick_params(axis="y", colors="red")
        ax2.spines["right"].set_color("red")
        if line_label == "Deviation Down (kWh)":
            line_label = "Deviation (kWh)" 
        ax2.set_ylabel(line_label, color="red")
        if line_label == "Price (DKK/kWh)":
            ax2.set_ylim(-1.5, 3)
        if line_label == "Deviation (kWh)":
            ax2.set_ylim(-3, 3)
        if line_label == "Battery SOC (kWh)":
            ax2.set_ylim(0, 7)
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
    ax.set_ylim(-3,3)
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




def plot_price_scenarios(variable_dict, save_path: str | None = None, show: bool = True, title: str = "Price Scenarios for different price profiles"):
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
    markers = ['o', 'x', 's', '^', 'v', '*', 'D', 'p', '+', '>', 'h']
    linestyles = ['-', '--', '-.', ':']
    for idx, key in enumerate(dual_dict):
        marker = markers[idx % len(markers)]
        linestyle = linestyles[idx % len(linestyles)]
        plt.plot(hours, dual_dict[key], marker=marker,ms=8, linestyle=linestyle, alpha=0.7, label=key)
    # Graph features
    plt.xlabel('Hour of Day')
    plt.xticks(hours)
    plt.ylabel('Dual Value')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper left", bbox_to_anchor=(1,1.07))
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

def plot_all_columns_one_graph_2b(df: pd.DataFrame, save_path: str | None = None, show: bool = True, 
                               show_price_line = True, title: str = "Stacked flows vs time (with energy price)",
                               line_label: str = "Price (DKK/kWh)"):
    if show_price_line == True:
        price_ser = df.pop(line_label)
        if line_label == "Deviation Down (kWh)":
            price_ser2 = df.pop("Deviation Up (kWh)")
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
        if line_label == "Deviation Down (kWh)":
            ax2.plot(x, price_ser2.reindex(df.index).to_numpy(dtype=float), marker="o", color="purple", linestyle="--" ,label="Deviation Up (kWh)")
        price_line.set_zorder(3)  # draw line above bars
        ax2.tick_params(axis="y", colors="red")
        ax2.spines["right"].set_color("red")
        if line_label == "Deviation Down (kWh)":
            line_label = "Deviation (kWh)" 
        ax2.set_ylabel(line_label, color="red")
        if line_label == "Price (DKK/kWh)":
            ax2.set_ylim(-1.5, 3)
        if line_label == "Deviation (kWh)":
            ax2.set_ylim(-3, 3)
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
    ax.set_ylim(-3,3)
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