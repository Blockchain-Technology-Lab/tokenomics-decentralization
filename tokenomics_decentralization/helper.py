"""
Module with helper functions
"""
import pathlib
import os
import datetime
import calendar
import argparse
import json
import logging
from yaml import safe_load
from dateutil.rrule import rrule, MONTHLY, WEEKLY, YEARLY, DAILY

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
MAPPING_INFO_DIR = ROOT_DIR / 'mapping_information'
TX_FEES_DIR = ROOT_DIR / 'tx_fees'

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
        raise argparse.ArgumentTypeError("Please use the format YYYY-MM-DD for the timeframe argument "
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


def get_output_directories():
    """
    Reads the config file and retrieves the output directories
    :returns: a list of directories that might contain the db files
    """
    config = get_config_data()
    return [pathlib.Path(db_dir).resolve() for db_dir in config['output_directories']]


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


def get_force_map_balances_flag():
    """
    Gets the flag that determines whether to forcefully map balances in db
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['execution_flags']['force_map_balances']
    except KeyError:
        raise ValueError('Flag "force_map_balances" not in config file')


def get_force_analyze_flag():
    """
    Gets the flag that determines whether to forcefully recalculate metrics
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['execution_flags']['force_analyze']
    except KeyError:
        raise ValueError('Flag "force_analyze" not in config file')


def get_no_clustering_flag():
    """
    Gets the flag that determines whether to forcefully recreate metrics
    :returns: boolean
    :raises ValueError: if the flag is not set in the config file
    """
    config = get_config_data()
    try:
        return config['analyze_flags']['no_clustering']
    except KeyError:
        raise ValueError('Flag "no_clustering" not in config file')


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
    :returns: string in ['day', 'week', 'month', 'year'] or None
    :raises ValueError: if the granularity is not set in the config file or if it is not one of the allowed values
    """
    try:
        granularity = get_config_data()['granularity']
        if granularity in ['day', 'week', 'month', 'year']:
            return granularity
        else:
            raise ValueError('Malformed "granularity" in config; should be one of: "day", "week", "month", "year", or empty')
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
        else:
            raise ValueError('Malformed "top_limit_type" in config')
    except KeyError:
        raise ValueError('Flag "top_limit_value" not in config file')


def get_circulation_from_entries(entries):
    """
    Computes the aggregate value of a list of db entries
    :returns: integer
    """
    return sum([int(entry[1]) for entry in entries])


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


def get_plot_config_data():
    """
    Retrieves the plot-related config parameters
    :returns: dictionary
    """
    return get_config_data()['plot_parameters']


def get_output_files():
    """
    Retrieves all output files produced by some run
    :returns: a list of filenames
    """
    output_dir = str(get_output_directories()[0])
    return [filename for filename in os.listdir(output_dir) if filename.startswith('output') and filename.endswith('.csv')]


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
