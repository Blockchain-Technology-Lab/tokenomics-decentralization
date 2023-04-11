import argparse
from src.helper import valid_date
from src.parsers.parser import Parser
from src.mappings.mapping import Mapping
from src.helper import OUTPUT_DIR
from src.metrics.entropy import compute_entropy
from src.metrics.herfindahl_hirschman_index import compute_hhi
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.gini import compute_gini

metrics_funcs = {
    'Gini': compute_gini,
    'NC': compute_nakamoto_coefficient,
    'Entropy': compute_entropy,
    'HHI': compute_hhi
}

additional_metric_args = {
    'Entropy': ['entropy_alpha']
}

START_YEAR = 2018
END_YEAR = 2024
PROJECTS = ['bitcoin', 'bitcoin_cash', 'dash', 'dogecoin', 'ethereum', 'litecoin', 'tezos', 'zcash']


def run(projects, timeframes, force_parse, entropy_alpha):
    print(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        parsed_data_file = OUTPUT_DIR / project / 'parsed_data.csv'
        if force_parse or not parsed_data_file.is_file():
            print(f'parsing {project} data..')
            parser = Parser(project)
            parser.parse()
        print(f'mapping {project} data..')
        mapping = Mapping(project_name=project, io_dir=OUTPUT_DIR / project)
        mapping.map()

    csv_contents = {}
    for metric in metrics_funcs.keys():
        csv_contents[metric] = {'0': 'timeframe'}

    for project in projects:
        # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
        # The special entry '0': '<comma-separated names of projects>' is for the csv header
        for metric in metrics_funcs.keys():
            csv_contents[metric]['0'] += f',{project}'

        for timeframe in timeframes:
            for metric in metrics_funcs.keys():
                if timeframe not in csv_contents[metric].keys():
                    csv_contents[metric][timeframe] = timeframe

            # Get mapped data for the year that corresponds to the timeframe.
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            yearly_entities = set()
            with open(OUTPUT_DIR / f'{project}/{year}.csv') as f:
                for line in f.readlines()[1:]:
                    row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                    yearly_entities.add(row[0])

            # Get mapped data for the defined timeframe.
            with open(OUTPUT_DIR / f'{project}/{timeframe}.csv') as f:
                blocks_per_entity = {}
                for line in f.readlines()[1:]:
                    blocks_per_entity[line.split(',')[0]] = int(line.split(',')[1])

            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0
                assert blocks_per_entity.keys() == yearly_entities
                results = {}
                scope = locals()
                for metric, func in metrics_funcs.items():
                    if metric in additional_metric_args.keys():
                        results[metric] = func(blocks_per_entity,
                                               *[eval(arg, scope) for arg in additional_metric_args[metric]])
                    else:
                        results[metric] = func(blocks_per_entity)
                entropy = compute_entropy(blocks_per_entity, entropy_alpha)
                print(f'[{project:12} {timeframe:7}] \t { {metric: value for metric, value in results.items()} }')
                print("\t".join(f"{k}:\t{v}" for k, v in results.items()))
            else:
                gini, nc, hhi, entropy = '', ('', ''), '', ''
                print(f'[{project:12} {timeframe:7}] \t No data')

            for metric in metrics_funcs.keys():
                csv_contents[metric][timeframe] += f',{results[metric]}'

    for metric in metrics_funcs.keys():
        with open(OUTPUT_DIR / f'{metric}.csv', 'w') as f:
            f.write('\n'.join([i[1] for i in sorted(csv_contents[metric].items(), key=lambda x: x[0])]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=PROJECTS,
        choices=[ledger for ledger in PROJECTS],
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="?",
        type=valid_date,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    parser.add_argument(
        '--force-parse',
        action='store_true',
        help='Flag to specify whether to parse the raw data, regardless if the parsed data file exists.'
    )
    parser.add_argument(
        '--entropy-alpha',
        nargs="?",
        type=int,
        default=1,
        help='The alpha parameter for entropy computation. Default Shannon entropy. Examples: -1: min, 0: Hartley, '
             '1: Shannon, 2: collision.'
    )
    args = parser.parse_args()

    projects = args.ledgers

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(START_YEAR, END_YEAR):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    run(projects, timeframes, args.force_parse, args.entropy_alpha)
