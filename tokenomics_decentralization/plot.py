import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
import tokenomics_decentralization.helper as hlp
import colorcet as cc
import pandas as pd
import pathlib

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent / 'output'    


def plot():
    """
    Plots the data contained in the output file
    """
    output_df = pd.read_csv(OUTPUT_DIR / 'output.csv')
    figures_path = OUTPUT_DIR / 'figures'
    if not figures_path.is_dir():
        figures_path.mkdir()
    metric_cols = output_df.columns[2:]
    for metric in metric_cols:
        output_df.pivot('snapshot','ledger', metric).plot(title=metric, xticks=output_df.snapshot, grid=True, marker='o', xlabel='time', ylabel=metric)
        plt.savefig(figures_path / f'{metric}.png', bbox_inches='tight')
