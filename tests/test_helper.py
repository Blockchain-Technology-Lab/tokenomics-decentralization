import tokenomics_decentralization.helper as hlp
import pathlib
import os
import argparse
import datetime
import pytest


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


def test_increment_date():
    date = datetime.datetime.strptime('2021-01-01', '%Y-%m-%d').date()

    new_date = hlp.increment_date(date, 'day')
    assert new_date == datetime.date(2021, 1, 2)

    new_date = hlp.increment_date(date, 'week')
    assert new_date == datetime.date(2021, 1, 8)

    new_date = hlp.increment_date(date, 'month')
    assert new_date == datetime.date(2021, 2, 1)

    new_date = hlp.increment_date(date, 'year')
    assert new_date == datetime.date(2022, 1, 1)

    with pytest.raises(ValueError):
        hlp.increment_date(date, 'other')


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


def test_get_tau_threshold_from_parameter():
    tau = hlp.get_tau_threshold_from_parameter('tau=0.1')
    assert tau == 0.1
    with pytest.raises(ValueError):
        hlp.get_tau_threshold_from_parameter('tau=blah')


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

    get_granularity_mock.return_value = 'year'
    fee1 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee1 == 3347

    get_granularity_mock.return_value = 'month'
    fee1 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee1 == 2820
    fee2 = hlp.get_median_tx_fee('ethereum', '2023-10-18')
    assert fee2 == 626000

    get_granularity_mock.return_value = 'week'
    fee3 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee3 == 2712

    get_granularity_mock.return_value = 'blahblah'
    fee4 = hlp.get_median_tx_fee('bitcoin', '2023-10-18')
    assert fee4 == 0

    get_granularity_mock.return_value = 'week'
    fee5 = hlp.get_median_tx_fee('bitcoin', '3333-10-18')
    assert fee5 == 0


def test_get_denomination_from_coin():
    assert hlp.get_denomination_from_coin('bitcoin') == 1e8
    assert hlp.get_denomination_from_coin('bitcoin_cash') == 1e8
    assert hlp.get_denomination_from_coin('cardano') == 1e6
    assert hlp.get_denomination_from_coin('ethereum') == 1e9
    assert hlp.get_denomination_from_coin('litecoin') == 1e8
    assert hlp.get_denomination_from_coin('tezos') == 1e6
    assert hlp.get_denomination_from_coin('blahblah') == 1


def test_config_flags(mocker):
    functions_to_test = [
        hlp.get_plot_flag,
        hlp.get_force_map_addresses_flag,
        hlp.get_clustering_flag,
        hlp.get_exclude_contracts_flag,
        hlp.get_exclude_below_fees_flag,
        hlp.get_exclude_below_usd_cent_flag,
    ]

    for function in functions_to_test:
        flag = function()
        assert isinstance(flag, bool)

    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")
    get_config_mock.return_value = {}

    for function in functions_to_test:
        with pytest.raises(ValueError):
            function()

    get_active_source_keywords_mock = mocker.patch("tokenomics_decentralization.helper.get_active_source_keywords")

    get_active_source_keywords_mock.return_value = ['test']
    clustering_flag = hlp.get_clustering_flag()
    assert clustering_flag is True

    get_active_source_keywords_mock.return_value = []
    clustering_flag = hlp.get_clustering_flag()
    assert clustering_flag is False


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

    balance_threshold = hlp.get_usd_cent_equivalent(ledger='test', date='2021-03-01')
    assert balance_threshold == 0

    balance_threshold = hlp.get_usd_cent_equivalent(ledger='bitcoin', date='3333-03-01')
    assert balance_threshold == 0


def test_get_output_row(mocker):
    get_metrics_mock = mocker.patch('tokenomics_decentralization.helper.get_metrics')
    get_metrics_mock.return_value = ['hhi', 'gini']

    get_clustering_mock = mocker.patch('tokenomics_decentralization.helper.get_clustering_flag')
    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_exclude_below_usd_cent_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_usd_cent_flag')
    get_top_limit_type_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_type')
    get_top_limit_value_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_value')

    get_clustering_mock.return_value = True
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_exclude_below_usd_cent_mock.return_value = False
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    metrics = {'hhi': 1, 'gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, False, 'absolute', 0, False, False, 1, 0]

    get_clustering_mock.return_value = False
    metrics = {'non-clustered hhi': 1, 'non-clustered gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, False, 'absolute', 0, False, False, 1, 0]

    get_exclude_contracts_mock.return_value = True
    metrics = {'exclude_contracts non-clustered hhi': 1, 'exclude_contracts non-clustered gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, True, 'absolute', 0, False, False, 1, 0]

    get_top_limit_value_mock.return_value = 1
    metrics = {'top-1_absolute exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_contracts non-clustered gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, True, 'absolute', 1, False, False, 1, 0]

    get_exclude_below_fees_mock.return_value = True
    get_top_limit_value_mock.return_value = 1
    metrics = {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_below_fees exclude_contracts non-clustered gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, True, 'absolute', 1, True, False, 1, 0]

    get_exclude_below_fees_mock.return_value = False
    get_exclude_below_usd_cent_mock.return_value = True
    metrics = {'top-1_absolute exclude_below_usd_cent exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_below_usd_cent exclude_contracts non-clustered gini': 0}
    csv_row = hlp.get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, True, 'absolute', 1, False, True, 1, 0]


def test_write_csv_output(mocker):
    get_metrics_mock = mocker.patch('tokenomics_decentralization.helper.get_metrics')
    get_metrics_mock.return_value = ['hhi']

    get_output_directories_mock = mocker.patch('tokenomics_decentralization.helper.get_output_directories')
    get_output_directories_mock.return_value = [pathlib.Path(__file__).resolve().parent]

    get_clustering_mock = mocker.patch('tokenomics_decentralization.helper.get_clustering_flag')
    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_exclude_below_usd_cent_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_usd_cent_flag')
    get_top_limit_type_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_type')
    get_top_limit_value_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_value')

    get_clustering_mock.return_value = True
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_exclude_below_usd_cent_mock.return_value = False
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    hlp.write_csv_output([
        ['bitcoin', '2010-01-01', True, False, 'absolute', 0, False, False, 100],
        ['ethereum', '2010-01-01', True, False, 'absolute', 0, False, False, 200],
        ])
    with open(pathlib.Path(__file__).resolve().parent / 'output.csv') as f:
        lines = f.readlines()
        assert lines[0] == ','.join(['ledger', 'snapshot_date', 'clustering', 'exclude_contract_addresses',
                                     'top_limit_type', 'top_limit_value', 'exclude_below_fees',
                                     'exclude_below_usd_cent', 'hhi']) + '\n'
        assert lines[1] == ','.join(['bitcoin', '2010-01-01', 'True', 'False', 'absolute', '0', 'False', 'False',
                                     '100']) + '\n'
        assert lines[2] == ','.join(['ethereum', '2010-01-01', 'True', 'False', 'absolute', '0', 'False', 'False',
                                     '200']) + '\n'
    os.remove(pathlib.Path(__file__).resolve().parent / 'output.csv')

    get_clustering_mock.return_value = False
    get_exclude_contracts_mock.return_value = True
    get_exclude_below_fees_mock.return_value = True
    get_exclude_below_usd_cent_mock.return_value = True
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 10

    hlp.write_csv_output([
        ['bitcoin', '2010-01-01', False, False, 'absolute', 0, False, False, 100],
        ['ethereum', '2010-01-01', False, False, 'absolute', 0, False, False, 200],
    ])
    with open(pathlib.Path(__file__).resolve().parent / 'output-no_clustering-exclude_contract_addresses-absolute_10-exclude_below_fees-exclude_below_usd_cent.csv') as f:
        lines = f.readlines()
        assert lines[0] == ','.join(['ledger', 'snapshot_date', 'clustering', 'exclude_contract_addresses',
                                     'top_limit_type', 'top_limit_value', 'exclude_below_fees',
                                     'exclude_below_usd_cent', 'hhi']) + '\n'
        assert lines[1] == ','.join(['bitcoin', '2010-01-01', 'False', 'False', 'absolute', '0', 'False', 'False',
                                     '100']) + '\n'
        assert lines[2] == ','.join(['ethereum', '2010-01-01', 'False', 'False', 'absolute', '0', 'False', 'False',
                                     '200']) + '\n'
    os.remove(pathlib.Path(__file__).resolve().parent / 'output-no_clustering-exclude_contract_addresses-absolute_10-exclude_below_fees-exclude_below_usd_cent.csv')


def test_get_active_source_keywords(mocker):
    get_config_mock = mocker.patch("tokenomics_decentralization.helper.get_config_data")
    get_config_mock.return_value = {'analyze_flags': {'clustering_sources': ['test']}}

    active_sources = hlp.get_active_source_keywords()
    assert active_sources == ['test']


def test_get_active_sources(mocker):
    json_load_mock = mocker.patch('json.load')
    json_load_mock.return_value = {'Test 1': ['test1', 'test11'], 'Test 2': ['test2']}

    get_active_source_keywords_mock = mocker.patch("tokenomics_decentralization.helper.get_active_source_keywords")
    get_active_source_keywords_mock.return_value = ['Test 1']

    active_sources = hlp.get_active_sources()
    assert active_sources == set(['test1', 'test11'])


def test_get_clusters(mocker):
    mocker.patch('builtins.open', mocker.mock_open(
        read_data='{"name": "entity1", "address": "addr1", "source": "test"}\n{"name": "entity2", "address": "addr2", "source": "test"}\n{"name": "entity3", "address": "addr2", "source": "test2"}\n{"name": "entity3", "address": "addr1", "source": "test2"}\n{"name": "entity4", "address": "addr4", "source": "test"}\n{"name": "entity5", "address": "addr4", "source": "test2"}\n{"name": "entity6", "address": "addr6", "source": "test"}\n{"name": "entity7", "address": "addr1", "source": "test3"}'
    ))

    get_active_sources_mock = mocker.patch("tokenomics_decentralization.helper.get_active_sources")
    get_active_sources_mock.return_value = ['test', 'test2']

    clusters = hlp.get_clusters('bitcoin')
    assert clusters['entity1'] == clusters['entity2']
    assert clusters['entity1'] == clusters['entity3']
    assert clusters['entity4'] == clusters['entity5']
