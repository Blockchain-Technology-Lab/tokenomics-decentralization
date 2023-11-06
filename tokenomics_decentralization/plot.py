import logging
import matplotlib.pyplot as plt
import pandas as pd
import pathlib

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent / 'output'    


def plot():
    """
    Plots the data contained in the output file
    """
    logging.info('Plotting data..')
    output_df = pd.read_csv(OUTPUT_DIR / 'output.csv')
    figures_path = OUTPUT_DIR / 'figures'
    if not figures_path.is_dir():
        figures_path.mkdir()
    output_df['snapshot date'] = pd.to_datetime(output_df['snapshot date'])
    metric_cols = output_df.columns[2:]
    for metric in metric_cols:
        df_pivot = output_df.pivot(index='snapshot date', columns='ledger', values=metric)
        df_pivot.plot(title=metric, grid=True, marker='o', xlabel='time', ylabel=metric)
        plt.savefig(figures_path / f'{metric}.png', bbox_inches='tight')
