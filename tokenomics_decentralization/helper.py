"""
Module with helper functions
"""
import csv
import pathlib
import os
import datetime
import calendar
import psutil
import json
from collections import defaultdict
import logging
from yaml import safe_load
from dateutil.rrule import rrule, MONTHLY, WEEKLY, YEARLY, DAILY

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
MAPPING_INFO_DIR = ROOT_DIR / 'mapping_information'
TX_FEES_DIR = ROOT_DIR / 'tx_fees'
PRICE_DATA_DIR = ROOT_DIR / 'price_data'

with open(ROOT_DIR / "config.yaml") as f:
    config = safe_load(f)


def valid_date(date_string):
    """
    Validates the given string if it corresponds to a correct date and is in YYYY-MM-DD, YYYY-MM or YYYY format
    :param date_string: a string representation of a date
    :returns: the string as it was given, if it corresponds to a valid date in the specified format
    :raises argparse.ArgumentTypeError: if the wrong format is used or if the date_string doesn't correspond to a valid
    date
    """
    try:
        get_date_beginning(date_string)
    except ValueError:
        raise ValueError("Please use the format YYYY-MM-DD for the timeframe argument "
                         "(day and month can be omitted).")
    return date_string


def get_date_beginning(date_string):
    """
    Determines the first day that corresponds to a given date string
    :param date_string: a string representation of a date in YYYY-MM-DD, YYYY-MM or YYYY format
    :returns: a date object corresponding to the first day associated with this date (e.g. first day of the year if only the year is given)
    """
    return datetime.date.fromisoformat(date_string.ljust(10, 'x').replace('xxx', '-01'))


def get_date_end(date_string):
    """
    Determines the last day that corresponds to a given date string
    :param date_string: a string representation of a date in YYYY-MM-DD, YYYY-MM or YYYY format
    :returns: a date object corresponding to the last day associated with this date (e.g. last day of the year if only the year is given)
    """
    date_with_month = date_string.ljust(7, 'x').replace('xxx', '-12')
    year, month = [int(i) for i in date_with_month.split('-')][:2]
    days_in_month = calendar.monthrange(year, month)[1]
    date_with_day = date_with_month.ljust(10, 'x').replace('xxx', f'-{days_in_month}')
    return datetime.date.fromisoformat(date_with_day)


def get_config_data():
    """
    Reads the configuration data of the project. This data is read from a file named "config.yaml" located at the
    root directory of the project.
    :returns: a dictionary of configuration keys and values
    """
    return config


def get_ledgers():
    """
    Retrieves data regarding the ledgers to use
    :returns: a list of strings that correspond to the ledgers that will be used (unless overriden by the relevant cmd
    arg)
    """
    return get_config_data()['ledgers']


def get_snapshot_dates():
    """
    Retrieves the snapshot dates for which to analyze data
    :returns: a list of strings
    """
    return sorted(get_config_data()['snapshot_dates'])


def get_dates_between(start_date, end_date, granularity):
    """
    Determines the dates between the given start and end dates according to the given granularity
    :param start_date: a datetime.date object corresponding to the start date
    :param end_date: a datetime.date object corresponding to the end date
    :param granularity: the granularity that will be used for the analysis. It can be one of: day, week, month, year
    :returns: a list of strings in YYYY-MM-DD format, corresponding to the dates between the given start and end dates based on the given granularity.
    Note that the end date may not be part of the list, depending on the start date and granularity.
    :raises ValueError: if the end date preceeds start_date or if the granularity is not
    one of the allowed values (day, week, month, year)
    """
    if end_date < start_date:
        raise ValueError(f'Invalid start / end dates: {start_date, end_date}')
    if granularity == 'day':
        dates = [get_date_string_from_date(dt) for dt in rrule(freq=DAILY, dtstart=start_date, until=end_date)]
    elif granularity == 'week':
        dates = [get_date_string_from_date(dt) for dt in rrule(freq=WEEKLY, dtstart=start_date, until=end_date)]
    elif granularity == 'month':
        dates = [get_date_string_from_date(dt) for dt in rrule(freq=MONTHLY, dtstart=start_date, until=end_date)]
    elif granularity == 'year':
        dates = [get_date_string_from_date(dt) for dt in rrule(freq=YEARLY, dtstart=start_date, until=end_date)]
    else:
        raise ValueError(f'Invalid granularity: {granularity}')
    return dates


def get_date_string_from_date(date_object):
    """
    Converts a date object to a string in the format YYYY-MM-DD
    :param date_object: a datetime.date object
    :returns: a string representation of the given date in the format YYYY-MM-DD
    """
    return date_object.strftime('%Y-%m-%d')


def increment_date(date, by):
    """
    Increments a date by a given time period
    :param date: a datetime.date object
    :param by: a string in ['day', 'week', 'month', 'year']
    :returns: a datetime.date object that corresponds to the date incremented by the number of days that correspond to the given granularity
    :raises ValueError: if the granularity is not one of the allowed values
    """
    if by == 'day':
        return date + datetime.timedelta(days=1)
    elif by == 'week':
        return date + datetime.timedelta(weeks=1)
    elif by == 'month':
        return date + datetime.timedelta(days=calendar.monthrange(date.year, date.month)[1])
    elif by == 'year':
        return datetime.date(date.year + 1, date.month, date.day)
    else:
        raise ValueError(f'Invalid granularity: {by}')


def get_output_directory():
    """
    Reads the config file and retrieves the output directories
    :returns: a list of directories that might contain the db files
    """
    config = get_config_data()
    sources = ' - '.join(get_active_source_keywords())
    if not sources:
        sources = 'No clustering'
    return [pathlib.Path(db_dir).resolve() for db_dir in config['output_directories']][0] / sources


def get_input_directories():
    """
    Reads the config file and retrieves the input directories
    :returns: a list of directories that might contain the raw input data
    """
    config = get_config_data()
    return [pathlib.Path(db_dir).resolve() for db_dir in config['input_directories']]


def get_tau_thresholds():
    """
    Reads the config file and retrieves the thresholds of tau decentralization
    :returns: a list of floating point thresholds to be used to compute tau decentralization
    """
    config = get_config_data()
    return [float(name.split('=')[1].strip()) for name in config['metrics'] if 'tau' in name]


def get_tau_threshold_from_parameter(parameter):
    """
    Retrieves the tau threshold that should be used in the computation from the parameter string
    :param parameter: string of the form 'tau=<threshold>'
    :returns: a float of the tau decentralization parameter
    """
    return float(parameter.split('=')[1])


def get_plot_flag():
    """
    Gets the flag that determines whether generate plots for the output
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['plot_parameters']['plot']
    except KeyError:
        raise ValueError('Flag "plot" not in config file')


def get_force_map_addresses_flag():
    """
    Gets the flag that determines whether to forcefully map addresses in db
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['execution_flags']['force_map_addresses']
    except KeyError:
        raise ValueError('Flag "force_map_addresses" not in config file')


def get_clustering_flag():
    """
    Gets a flag that determines whether to cluster addresses into entities
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    if get_active_source_keywords():
        return True
    return False


def get_metrics():
    """
    Retrieves the metrics to be analyzed
    :returns: list of strings of the metric names to be used
    :raises ValueError: if the metrics are not set in the config file
    """
    try:
        return get_config_data()['metrics']
    except KeyError:
        raise ValueError('"metrics" not set in config file')


def get_granularity():
    """
    Retrieves the granularity to be used in the analysis
    :returns: string in ['day', 'week', 'month', 'year'] that represents the chosen granularity
    or None if the relevant field is empty in the config file
    :raises ValueError: if the granularity field is missing from the config file or if
    the chosen value is not one of the allowed ones
    """
    try:
        granularity = get_config_data()['granularity']
        if granularity:
            if granularity in ['day', 'week', 'month', 'year']:
                return granularity
            else:
                raise ValueError('Malformed "granularity" in config; should be one of: "day", "week", "month", "year", or empty')
        else:
            return None
    except KeyError:
        raise ValueError('"granularity" not in config file')


def get_top_limit_type():
    """
    Retrieves the type of top limit
    :returns: a string in ["absolute", "percentage"]
    :raises ValueError: if the top limit type is not set in the config file or if it is not one of the allowed values
    """
    config = get_config_data()
    try:
        if config['analyze_flags']['top_limit_type'] in ['absolute', 'percentage']:
            return config['analyze_flags']['top_limit_type']
        else:
            raise ValueError('Malformed "top_limit_type" in config; should be "absolute" or "percentage"')
    except KeyError:
        raise ValueError('Flag "top_limit_type" not set in config file')


def get_top_limit_value():
    """
    Retrieves the value of the top limit to be applied
    :returns: a positive integer if the limit type is 'absolute', else a float in [0, 1] if type is 'percentage'
    :raises ValueError: if the top limit value is not set in the config file or if it is not one of the allowed values
    """
    config = get_config_data()
    top_limit_type = get_top_limit_type()
    try:
        top_limit_value = config['analyze_flags']['top_limit_value']
        if top_limit_value is None:
            return 0
        elif top_limit_type == 'absolute':
            if top_limit_value >= 0:
                return int(top_limit_value)
            else:
                raise ValueError('Malformed "top_limit_value" in config; should be non-negative')
        elif top_limit_type == 'percentage':
            if 0 <= top_limit_value <= 1:
                return top_limit_value
            else:
                raise ValueError('Malformed "top_limit_value" in config; should be in [0, 1]')
    except KeyError:
        raise ValueError('Flag "top_limit_value" not in config file')


def get_circulation_from_entries(entries):
    """
    Computes the aggregate value of a list of db entries.
    Uses a greedy execution, instead of an one-liner that sums a list, to avoid memory consumption.
    :param entries: a list of integers
    :returns: integer
    """
    return sum(entries)


def get_exclude_contracts_flag():
    """
    Retrieves the flag on whether to exclude contract addresses from the analysis
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['analyze_flags']['exclude_contract_addresses']
    except KeyError:
        raise ValueError('Flag "exclude_contract_addresses" not in config file')


def get_exclude_below_fees_flag():
    """
    Retrieves the flag on whether to exclude from the analysis addresses with
    balances lower than the median transaction fees
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['analyze_flags']['exclude_below_fees']
    except KeyError:
        raise ValueError('Flag "exclude_below_fees" not in config file')


def get_exclude_below_usd_cent_flag():
    """
    Retrieves the flag on whether to exclude from the analysis addresses with
    balances lower than the USD cent equivalent of the ledger's currency
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['analyze_flags']['exclude_below_usd_cent']
    except KeyError:
        raise ValueError('Flag "exclude_below_usd_cent" not in config file')


def get_plot_config_data():
    """
    Retrieves the plot-related config parameters
    :returns: dictionary
    """
    return get_config_data()['plot_parameters']


def get_special_addresses(ledger):
    """
    Retrieves the ledger's special addresses that should be excluded from the analysis
    :returns: a list of addresses
    """
    try:
        with open(MAPPING_INFO_DIR / 'special_addresses' / f'{ledger}.json') as f:
            special_addresses = json.load(f)
        return [entry['address'] for entry in special_addresses]
    except FileNotFoundError:
        return []


def get_median_tx_fee(ledger, date):
    """
    Retrieves the median transaction fee for the given ledger and date
    :param ledger: string that represents the ledger to retrieve the data for (e.g. bitcoin)
    :param date: string that represents the date to retrieve the data for
    (it should be in YYYY-MM-DD format, e.g. 2021-01-01)
    :returns: an integer representing the median transaction fee in the
    smallest unit of the ledger's currency or 0 if no median tx fee
    is found for the given ledger and date
    """
    granularity = get_granularity()
    try:
        with open(TX_FEES_DIR / ledger / f'median_tx_fees_{granularity}.json') as f:
            fees = json.load(f)
    except FileNotFoundError:
        logging.warning(f'No median tx fees found for {ledger}')
        return 0
    if granularity == 'year':
        date = date[:4]
    elif granularity == 'month':
        date = date[:7]
    elif granularity == 'week':
        # get date of that week's Monday
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        date = date - datetime.timedelta(days=date.weekday())
        date = get_date_string_from_date(date)
    try:
        return fees[date]
    except KeyError:
        logging.warning(f'No median tx fee found for {ledger} on {date}')
        return 0


def get_denomination_from_coin(ledger):
    """
    Retrieves the denomination of the given ledger's currency that we use in the analysis
    :param ledger: string that represents the ledger to retrieve the data for (e.g. bitcoin)
    :returns: a float representing how much of the denomination corresponds to one coin or 1 if no denomination
    information is found for the given ledger
    """
    denominations = {
        'bitcoin': 1e8,
        'bitcoin_cash': 1e8,
        'cardano': 1e6,
        'ethereum': 1e9,
        'litecoin': 1e8,
        'tezos': 1e6
    }
    try:
        return denominations[ledger]
    except KeyError:
        logging.warning(f'No denomination found for {ledger}')
        return 1


def get_usd_cent_equivalent(ledger, date):
    """
    Retrieves the amount of tokens that corresponds to one USD cent for the given ledger and date
    :param ledger: string that represents the ledger to retrieve the data for (e.g. bitcoin)
    :param date: string that represents the date to retrieve the data for
    (it should be in YYYY-MM-DD format, e.g. 2021-01-01)
    :returns: an integer representing the USD cent equivalent of the ledger's currency
    or 0 if no USD cent equivalent is found for the given ledger and date
    """
    try:
        with open(PRICE_DATA_DIR / f'{ledger}-USD.csv') as f:
            reader = csv.reader(f)
            prices = {key: float(value) for key, value in reader}
    except FileNotFoundError:
        logging.warning(f'No price data found for {ledger}')
        return 0
    try:
        price = prices[date]
        denomination_price = price / get_denomination_from_coin(ledger)
        cent_equivalent = 0.01 / denomination_price
        return cent_equivalent
    except KeyError:
        logging.warning(f'No price data found for {ledger} on {date}')
        return 0


def get_output_row(ledger, date, metrics):
    """
    Constructs a line of the csv output.
    :param ledger: a string with the ledger's name
    :param date: a snapshot date in YYYY-MM-DD format
    :param metrics: a dictionary where the key is the name of the computed metric prefixed with the applied thresholds and the value is a number
    :returns: a list of strings which comprises a single line of the csv output
    """
    clustering = get_clustering_flag()
    exclude_contract_addresses_flag = get_exclude_contracts_flag()
    exclude_below_fees_flag = get_exclude_below_fees_flag()
    exclude_below_usd_cent_flag = get_exclude_below_usd_cent_flag()
    top_limit_type = get_top_limit_type()
    top_limit_value = get_top_limit_value()

    csv_row = [ledger, date, clustering, exclude_contract_addresses_flag, top_limit_type, top_limit_value,
               exclude_below_fees_flag, exclude_below_usd_cent_flag]

    for metric_name in get_metrics():
        val = metric_name
        if not clustering:
            val = 'non-clustered ' + val
        if exclude_contract_addresses_flag:
            val = 'exclude_contracts ' + val
        if exclude_below_fees_flag:
            val = 'exclude_below_fees ' + val
        if exclude_below_usd_cent_flag:
            val = 'exclude_below_usd_cent ' + val
        if top_limit_value > 0:
            val = f'top-{top_limit_value}_{top_limit_type} ' + val
        csv_row.append(metrics[val])
    return csv_row


def get_output_filename():
    """
    Produces the name (full path) of the output file.
    :returns output_filename: a pathlib path of the output file
    """
    exclude_contract_addresses_flag = get_exclude_contracts_flag()
    top_limit_type = get_top_limit_type()
    top_limit_value = get_top_limit_value()
    exclude_below_fees_flag = get_exclude_below_fees_flag()
    exclude_below_usd_cent_flag = get_exclude_below_usd_cent_flag()
    output_filename = 'output'
    if exclude_contract_addresses_flag:
        output_filename += '-exclude_contract_addresses'
    if top_limit_value:
        output_filename += f'-{top_limit_type}_{top_limit_value}'
    if exclude_below_fees_flag:
        output_filename += '-exclude_below_fees'
    if exclude_below_usd_cent_flag:
        output_filename += '-exclude_below_usd_cent'
    output_filename += '.csv'
    return get_output_directory() / output_filename


def write_csv_output(output_rows):
    """
    Produces the output csv file for the given data.
    :param output_rows: a list of lists, where each list corresponds to a line in the output csv file
    """
    header = ['ledger', 'snapshot_date', 'clustering', 'exclude_contract_addresses', 'top_limit_type',
              'top_limit_value', 'exclude_below_fees', 'exclude_below_usd_cent']
    header += get_metrics()

    with open(get_output_filename(), 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        csv_writer.writerows(output_rows)


def get_active_source_keywords():
    """
    Returns the keywords of the sources that should be used in the analysis based on the config parameters.
    :returns: a list of strings of mapping information source keywords
    """
    try:
        return get_config_data()['analyze_flags']['clustering_sources']
    except KeyError:
        raise ValueError('Clustering sources does not exist in analyze flags')


def get_active_sources():
    """
    Returns the sources that should be used in the analysis based on the config parameters.
    :returns: a list of strings of mapping information sources
    """
    with open(MAPPING_INFO_DIR / 'sources.json') as f:
        source_keywords = json.load(f)

    active_sources = set()
    for kw in get_active_source_keywords():
        for source in source_keywords[kw]:
            active_sources.add(source)

    return active_sources


def get_clusters(ledger):
    """
    Retrieves the clusters of addresses that form from the mapping information.
    First identifies the addresses that are associated (in the mapping
    information) with more than one entities.
    Then it retrieves the set of all entities that each such address is
    associated with and constructs the clusters by finding overlapping entities in these sets.
    Finally it constructs a dictionary that maps entities to their cluster.
    :param ledger: a string of the ledger's name
    :returns: a dictionary where the key is an entity and the value is the cluster to which it belongs
    """
    # Find addresses that are associated with more than one entities.
    # Note: If the mapping file is very large, loading the whole dictionary can result to running out of memory. Using this step consumes less memory but requires one extra pass of the file.
    addresses = set()
    multi_entity_addresses = set()
    with open(MAPPING_INFO_DIR / f'addresses/{ledger}.jsonl') as f:
        for line in f:
            info = json.loads(line)
            address = info['address']
            if address in addresses:
                multi_entity_addresses.add(address)
            addresses.add(address)
    del addresses

    # Get the entities associated with the multi-entity addresses.
    address_entities = defaultdict(set)
    with open(MAPPING_INFO_DIR / f'addresses/{ledger}.jsonl') as f:
        for line in f:
            info = json.loads(line)
            address = info['address']
            if address in multi_entity_addresses:
                source = info['source']
                entity_name = info['name']
                if source not in get_active_sources():
                    continue
                address_entities[address].add((entity_name, source))
    del multi_entity_addresses

    clusters = list(address_entities.values())
    del address_entities

    # If an entity is present in two entries, then these are merged.
    # If an entry cannot be merged with any other entry, then it is finalized.
    finalized_counter = 0
    cluster_mapping = {}
    while clusters:
        cluster = clusters.pop()
        merged_flag = False
        for idx, new_item in enumerate(clusters):
            if new_item.intersection(cluster):
                merged_flag = True
                clusters[idx] = new_item.union(cluster)
                break
        if not merged_flag:
            finalized_counter += 1
            cluster_name = f'-++-{finalized_counter}-++-'
            for item in cluster:  # item = (entity, source)
                cluster_mapping[item[0]] = cluster_name

    return cluster_mapping


def get_concurrency_per_ledger():
    """
    Computes the maximum number of parallel processes that can run per ledger,
    based on the system's available memory.
    :returns: a dictionary where the keys are ledger names and values are integers
    """
    system_memory_total = psutil.virtual_memory().total  # Get the system's total memory
    system_memory_total -= 10**9  # Leave 1GB of memory to be used by other processes

    concurrency = {}
    too_large_ledgers = set()
    input_dirs = get_input_directories()
    for ledger in get_ledgers():
        # Find the size of the largest input file per ledger
        max_file_size = 0
        for input_dir in input_dirs:
            for folder, _, files in os.walk(input_dir):
                for file in files:
                    if file.startswith(ledger):
                        max_file_size = max(max_file_size, os.stat(os.path.join(folder, file)).st_size)
        # Compute the max number of processes that can open the largest ledger file
        # and run in parallel without exhausting the system's memory.
        if max_file_size > 0:
            # When loaded in (a dict in) memory, each file consumes approx. 2.5x space compared to storage.
            # Limit processes to CPU count to avoid OS process management overhead.
            concurrency[ledger] = min(os.cpu_count(), int(system_memory_total / (2.5 * max_file_size)))
            # Find if some ledger files are too large to fit in the system's available memory.
            if concurrency[ledger] == 0:
                too_large_ledgers.add(ledger)
        else:
            concurrency[ledger] = 1

    if too_large_ledgers:
        raise ValueError('The max input files of the following ledgers are too'
                         'large to load in memory' + ','.join(too_large_ledgers))

    return concurrency
