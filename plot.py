import tokenomics_decentralization.helper as hlp
import logging
import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler


tickers = {
    'bitcoin': 'BTC',
    'bitcoin_cash': 'BCH',
    'dogecoin': 'DOGE',
    'ethereum': 'ETH',
    'litecoin': 'LTC',
    'tezos': 'XTZ',
}


def plot():
    """
    Plots the data contained in the output file
    """
    logging.info('Plotting data..')
    output_dir = hlp.get_output_directories()[0]

    figures_path = output_dir / 'figures'
    if not figures_path.is_dir():
        figures_path.mkdir()

    # Combine all output files in a single dataframe
    output_df = pd.concat([pd.read_csv(output_dir / filename) for filename in hlp.get_output_files()], ignore_index=True)

    plot_config = hlp.get_plot_config_data()

    # Filter rows with ledgers defined in config
    ledgers = plot_config['ledgers']
    output_df = output_df[output_df['ledger'].isin(ledgers)]

    # Filter rows with metrics defined in config
    metrics = plot_config['metrics']
    metric_cols = output_df.columns[6:]
    for metric in metric_cols:
        if metric not in metrics:
            output_df = output_df.drop(labels=metric, axis=1)

    plot_line_params = plot_config['plot_line_params']

    # Filter rows with top limit params defined in config
    # If no top limit is defined in either 'absolute' or 'percentage', then 0 is used by default
    top_limits = {}
    for top_limit_type in ['absolute', 'percentage']:
        top_limits[top_limit_type] = plot_line_params[f'top_limit_{top_limit_type}']
        if not top_limits[top_limit_type]:
            top_limits[top_limit_type] = [-1]
    if top_limits['absolute'][0] == -1 and top_limits['percentage'][0] == -1:
        top_limits['absolute'] = top_limits['percentage'] = [0]
    elif top_limits['absolute'][0] == 0 or top_limits['percentage'][0] == 0:
        top_limits['absolute'].append(0)
        top_limits['percentage'].append(0)

    output_df = output_df[
        ((output_df['top_limit_type'] == 'absolute') & (output_df['top_limit_value'].isin(top_limits['absolute']))) |
        ((output_df['top_limit_type'] == 'percentage') & (output_df['top_limit_value'].isin(top_limits['percentage'])))
    ]

    # Filter rows with boolean flag params defined in config.
    # If no value is set for a flag, False is used by default
    # If the param consists of more than 2 and/or non-boolean entries, a ValueError is raised
    for flag in ['no_clustering', 'exclude_contract_addresses']:
        if plot_line_params[flag] is None:
            plot_line_params[flag] = [False]
        if len(plot_line_params[flag]) == 1:
            if plot_line_params[flag][0] not in [True, False]:
                raise ValueError(f'Invalid arguments in {flag} plotting flag')
            output_df = output_df[output_df[flag] == plot_line_params[flag][0]]
        elif len(plot_line_params[flag]) != 2 or any([item not in plot_line_params[flag] for item in [True, False]]):
            raise ValueError(f'Invalid arguments in {flag} plotting flag')

    # Plot each param in a line sequentially (keeping the other params at the default), instead of plotting the param combinations
    if plot_line_params['combine_params'] is False:
        dataframes = []
        for flag_value in plot_line_params['no_clustering']:
            dataframes.append(output_df[
                (output_df['no_clustering'] == flag_value) &
                (output_df['exclude_contract_addresses'] == False) &  # noqa
                (output_df['top_limit_value'] == 0)
            ])
        for flag_value in plot_line_params['exclude_contract_addresses']:
            dataframes.append(output_df[
                (output_df['no_clustering'] == False) &  # noqa
                (output_df['exclude_contract_addresses'] == flag_value) &
                (output_df['top_limit_value'] == 0)
            ])
        for limit_type in top_limits.keys():
            for limit_val in top_limits[limit_type]:
                dataframes.append(output_df[
                    (output_df['no_clustering'] == False) &  # noqa
                    (output_df['exclude_contract_addresses'] == False) &  # noqa
                    (output_df['top_limit_type'] == limit_type) &
                    (output_df['top_limit_value'] == limit_val)
                ])

        output_df = pd.concat(dataframes)
    elif plot_line_params['combine_params'] is not True:
        raise ValueError('Plot param combine_params should be set to either true or false')

    # Update ledger column name to reflect params used with tickers
    # This column will be used as the plot's legend
    for i, row in output_df.iterrows():
        output_df.at[i, 'ledger'] = tickers[row['ledger']]
        if row['no_clustering']:
            output_df.at[i, 'ledger'] += '_nocluster'
        if row['exclude_contract_addresses']:
            output_df.at[i, 'ledger'] += '_nocontracts'
        if row['top_limit_value'] > 0:
            limit_val = row['top_limit_value']
            if row['top_limit_type'] == 'absolute':
                limit_val = int(limit_val)
            output_df.at[i, 'ledger'] += f'_top_{limit_val}'

    output_df['snapshot date'] = pd.to_datetime(output_df['snapshot date'])

    output_df = output_df.drop_duplicates(subset=['ledger', 'snapshot date'])

    params = {'legend.fontsize': 14,
              'figure.titlesize': 40,
              'figure.figsize': (25, 13),
              'axes.labelsize': 'xx-large',
              'axes.titlesize': 'xx-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Define the styles of the lines to be plotted
    # If multiple ledgers are plotted, then use one color per ledger and a different line style per param, when possible
    # If a single ledger is plotted, then use solid lines and a different color per param
    line_names = set([row['ledger'] for _, row in output_df.iterrows()])
    lines_per_ledger = set(['_'.join(item.split('_')[1:]) for item in line_names])
    if len(ledgers) > 1:
        linestyles = ['-', '--', ':', '-.'][:len(lines_per_ledger)]
    else:
        linestyles = ['-']
    colorstyles = list('rbgkcmy') + ['tab:orange', 'tab:pink', 'tab:gray', 'tab:brown', 'tab:purple']
    plt.rc('axes', prop_cycle=(cycler('color', colorstyles) * cycler('linestyle', linestyles)))

    metric_cols = output_df.columns[6:]
    for metric in metric_cols:
        df_pivot = output_df.pivot(index='snapshot date', columns='ledger', values=metric)
        df_pivot.plot(figsize=(25, 13), grid=True, xlabel='Date', ylabel=metric, lw=2)
        plt.title(metric.upper(), fontsize=30)
        plt.gca().legend().set_title('')
        plt.savefig(figures_path / f'{metric}.png', bbox_inches='tight')


if __name__ == '__main__':
    if hlp.get_plot_flag():
        plot()
