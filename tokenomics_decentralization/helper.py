"""
Module with helper functions
"""
import pathlib
import datetime
import calendar
import argparse
from yaml import safe_load
from dateutil.rrule import rrule, MONTHLY, WEEKLY, YEARLY, DAILY

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
MAPPING_INFO_DIR = ROOT_DIR / 'mapping_information'


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
    with open(ROOT_DIR / "config.yaml") as f:
        config = safe_load(f)
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
    :param granularity: the granularity that will be used for the analysis. It can be one of: day, week, month, year, none
    :returns: a list of strings in YYYY-MM-DD format, corresponding to the dates between the given start and end dates based on the given granularity.
    Note that the end date may not be part of the list, depending on the start date and granularity.
    If granularity is none then the list will only contain the start and end dates.
    :raises ValueError: if the end date preceeds start_date or if the granularity is not
        one of: day, week, month, year, none
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
    elif granularity == 'none':
        dates = [get_date_string_from_date(start_date), get_date_string_from_date(end_date)]
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
    Gets the flag whether to plot output
    :returns: boolean
    """
    config = get_config_data()
    value = None
    for flag in config['execution_flags']:
        if flag['name'] == 'plot':
            return flag['value']
    if value is None:
        raise ValueError('Flag "plot" not in config file')


def get_force_map_addresses_flag():
    """
    Gets the flag whether to forcefully map addresses in db
    :returns: boolean
    """
    config = get_config_data()
    value = None
    for flag in config['execution_flags']:
        if flag['name'] == 'force_map_addresses':
            return flag['value']
    if value is None:
        raise ValueError('Flag "force_map_addresses" not in config file')


def get_force_map_balances_flag():
    """
    Gets the flag whether to forcefully map balances in db
    :returns: boolean
    """
    config = get_config_data()
    value = None
    for flag in config['execution_flags']:
        if flag['name'] == 'force_map_balances':
            return flag['value']
    if value is None:
        raise ValueError('Flag "force_map_balances" not in config file')


def get_force_analyze_flag():
    """
    Gets the flag whether to forcefully recreate metrics
    :returns: boolean
    """
    config = get_config_data()
    value = None
    for flag in config['execution_flags']:
        if flag['name'] == 'force_analyze':
            return flag['value']
    if value is None:
        raise ValueError('Flag "force_analyze" not in config file')


def get_no_clustering_flag():
    """
    Gets the flag whether to forcefully recreate metrics
    :returns: boolean
    """
    config = get_config_data()
    value = None
    for flag in config['analyze_flags']:
        if flag['name'] == 'no_clustering':
            return flag['value']
    if value is None:
        raise ValueError('Flag "no_clustering" not in config file')


def get_metrics():
    """
    Retrieves the metrics to be analyzed
    :returns: list of strings of the metric names to be used
    """
    return get_config_data()['metrics']


def get_granularity():
    """
    Retrieves the granularity to be used in the analysis
    :returns: string in ['day', 'week', 'month', 'year']
    """
    return get_config_data()['granularity']
