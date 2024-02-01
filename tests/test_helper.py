import argparse
import datetime
import os
import pytest
import tokenomics_decentralization.helper as hlp
import pathlib


def test_valid_date():
    for d in ['2022', '2022-01', '2022-01-01']:
        assert hlp.valid_date(d)

    for d in ['2022/1/01', '2022/01/1', '2022/1', '2022/01', '2022.1.01', '2022.01.1', '2022.1', '2022.01', 'blah',
              '2022-', '2022-1-1', '2022-1-01', '2022-1', '2022-01-1', '2022-02-29']:
        with pytest.raises(argparse.ArgumentTypeError) as e_info:
            hlp.valid_date(d)
        assert e_info.type == argparse.ArgumentTypeError


def test_get_date_beginning():
    dates = {'2022': datetime.date(2022, 1, 1), '2022-03': datetime.date(2022, 3, 1),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, start_date in dates.items():
        assert hlp.get_date_beginning(date) == start_date


def test_get_date_end():
    dates = {'2022': datetime.date(2022, 12, 31), '2024-02': datetime.date(2024, 2, 29),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, end_date in dates.items():
        assert hlp.get_date_end(date) == end_date


def test_get_ledgers():
    ledgers = hlp.get_ledgers()
    assert isinstance(ledgers, list)
    assert len(ledgers) > 0


def test_get_snapshot_dates():
    snapshot_dates = hlp.get_snapshot_dates()
    assert isinstance(snapshot_dates, list)
    assert len(snapshot_dates) > 0


def test_input_directories():
    input_dirs = hlp.get_input_directories()
    assert isinstance(input_dirs, list)
    assert len(input_dirs) > 0


def test_output_directories():
    output_dirs = hlp.get_output_directories()
    assert isinstance(output_dirs, list)
    assert len(output_dirs) > 0


def test_tau_thresholds():
    tau_thresholds = hlp.get_tau_thresholds()
    assert isinstance(tau_thresholds, list)
    assert len(tau_thresholds) > 0
    for tau in tau_thresholds:
        assert isinstance(tau, float)


def test_get_dates_between():
    start_date = datetime.date(2023, 9, 25)
    end_date = datetime.date(2023, 11, 20)
    dates_day = hlp.get_dates_between(start_date, end_date, granularity='day')
    assert len(dates_day) == 57
    assert dates_day[0] == "2023-09-25"
    assert dates_day[2] == "2023-09-27"
    assert dates_day[-1] == "2023-11-20"

    start_date = datetime.date(2023, 11, 10)
    end_date = datetime.date(2023, 11, 10)
    dates_day = hlp.get_dates_between(start_date, end_date, granularity='day')
    assert len(dates_day) == 1
    assert dates_day[0] == "2023-11-10"

    start_date = datetime.date(2023, 11, 8)
    end_date = datetime.date(2023, 12, 25)
    dates_week = hlp.get_dates_between(start_date, end_date, granularity='week')
    assert len(dates_week) == 7
    assert dates_week[0] == "2023-11-08"
    assert dates_week[3] == "2023-11-29"
    assert dates_week[-1] == "2023-12-20"

    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2023, 1, 15)
    dates_month = hlp.get_dates_between(start_date, end_date, granularity='month')
    assert len(dates_month) == 13
    assert dates_month[3] == "2022-04-01"
    assert dates_month[10] == "2022-11-01"
    assert dates_month[-1] == "2023-01-01"

    start_date = datetime.date(1996, 9, 25)
    end_date = datetime.date(2023, 9, 24)
    dates_year = hlp.get_dates_between(start_date, end_date, granularity='year')
    assert len(dates_year) == 27
    assert dates_year[0] == "1996-09-25"
    assert dates_year[14] == "2010-09-25"
    assert dates_year[-1] == "2022-09-25"

    start_date = datetime.date(2023, 11, 11)
    end_date = datetime.date(2023, 11, 10)
    with pytest.raises(ValueError) as e_info:
        hlp.get_dates_between(start_date, end_date, granularity='day')
    assert e_info.type == ValueError

    start_date = datetime.date(2023, 11, 10)
    end_date = datetime.date(2023, 11, 10)
    with pytest.raises(ValueError) as e_info:
        hlp.get_dates_between(start_date, end_date, granularity='bla')
    assert e_info.type == ValueError


def test_get_median_tx_fee(mocker):
    get_granularity_mock = mocker.patch("tokenomics_decentralization.helper.get_granularity")

    get_granularity_mock.return_value = 'month'
    fee1 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee1 == 2820
    fee2 = hlp.get_median_tx_fee('ethereum', '2023-10-18')
    assert fee2 == 626000

    get_granularity_mock.return_value = 'week'
    fee3 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee3 == 2712


def test_config_flags(mocker):
    functions_to_test = [
        hlp.get_plot_flag,
        hlp.get_force_map_addresses_flag,
        hlp.get_force_map_balances_flag,
        hlp.get_force_analyze_flag,
        hlp.get_no_clustering_flag,
        hlp.get_exclude_contracts_flag,
        hlp.get_exclude_below_fees_flag,
    ]

    for function in functions_to_test:
        flag = function()
        assert isinstance(flag, bool)

    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")
    get_config_mock.return_value = {}

    for function in functions_to_test:
        with pytest.raises(ValueError):
            function()


def test_get_metrics(mocker):
    metrics = hlp.get_metrics()
    assert isinstance(metrics, list)
    assert len(metrics) > 0

    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")
    get_config_mock.return_value = {}

    with pytest.raises(ValueError):
        hlp.get_metrics()


def test_get_granularity(mocker):
    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")

    get_config_mock.return_value = {'granularity': 'month'}
    granularity = hlp.get_granularity()
    assert isinstance(granularity, str)

    get_config_mock.return_value = {'granularity': ''}
    granularity = hlp.get_granularity()
    assert granularity is None

    get_config_mock.return_value = {'granularity': 'blah'}
    with pytest.raises(ValueError):
        hlp.get_granularity()

    get_config_mock.return_value = {}
    with pytest.raises(ValueError):
        hlp.get_granularity()


def test_get_top_limit_type(mocker):
    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'absolute'}}
    top_limit_type = hlp.get_top_limit_type()
    assert isinstance(top_limit_type, str)

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'blah'}}
    with pytest.raises(ValueError):
        hlp.get_top_limit_type()

    get_config_mock.return_value = {}
    with pytest.raises(ValueError):
        hlp.get_top_limit_type()


def test_get_top_limit_value(mocker):
    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'percentage', 'top_limit_value': 0}}
    top_limit_value = hlp.get_top_limit_value()
    assert top_limit_value >= 0

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'percentage', 'top_limit_value': None}}
    top_limit_value = hlp.get_top_limit_value()
    assert top_limit_value == 0

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'percentage', 'top_limit_value': 0.33}}
    top_limit_value = hlp.get_top_limit_value()
    assert isinstance(top_limit_value, float)
    assert top_limit_value == 0.33

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'percentage', 'top_limit_value': 1.1}}
    with pytest.raises(ValueError):
        hlp.get_top_limit_value()

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'absolute', 'top_limit_value': None}}
    top_limit_value = hlp.get_top_limit_value()
    assert top_limit_value == 0

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'absolute', 'top_limit_value': 10}}
    top_limit_value = hlp.get_top_limit_value()
    assert isinstance(top_limit_value, int)
    assert top_limit_value == 10

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'absolute', 'top_limit_value': -1}}
    with pytest.raises(ValueError):
        hlp.get_top_limit_value()

    get_config_mock.return_value = {'analyze_flags': {'top_limit_type': 'percentage'}}
    with pytest.raises(ValueError):
        hlp.get_top_limit_value()


def test_get_circulation_from_entries():
    entries = [[10, ], [11, ]]
    circulation = hlp.get_circulation_from_entries(entries)
    assert circulation == 21


def test_get_output_files(mocker):
    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_output_directories")
    get_config_mock.return_value = [pathlib.Path(__file__).resolve().parent]
    output_files = hlp.get_output_files()
    assert isinstance(output_files, list)


def test_get_special_addresses():
    ethereum_special_addresses = hlp.get_special_addresses('ethereum')
    assert isinstance(ethereum_special_addresses, list)
    assert ethereum_special_addresses[0] == '0x00000000219ab540356cBB839Cbe05303d7705Fa'

    special_addresses = hlp.get_special_addresses('blah')
    assert isinstance(special_addresses, list)
    assert special_addresses == []


def test_get_plot_config_data():
    plot_config = hlp.get_plot_config_data()
    assert isinstance(plot_config, dict)


def test_get_usd_cent_equivalent(mocker):
    with open(hlp.PRICE_DATA_DIR / 'test-USD.csv', 'w') as f:
        f.write('2021-03-01,100\n')
        f.write('2023-10-18,0.1\n')
    get_denomination_mock = mocker.patch("tokenomics_decentralization.helper.get_denomination_from_coin")
    get_denomination_mock.return_value = 1e8

    balance_threshold = hlp.get_usd_cent_equivalent(ledger='test', date='2021-03-01')
    assert balance_threshold == 1e4

    balance_threshold = hlp.get_usd_cent_equivalent(ledger='test', date='2023-10-18')
    assert balance_threshold == 1e7

    os.remove(hlp.PRICE_DATA_DIR / 'test-USD.csv')
