from tokenomics_decentralization.analyze import analyze_snapshot, analyze, get_entries
from unittest.mock import call
import pathlib


def test_analyze_snapshot(mocker):
    get_clustering_mock = mocker.patch('tokenomics_decentralization.helper.get_clustering_flag')
    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_exclude_below_usd_cent_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_usd_cent_flag')
    get_top_limit_type_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_type')
    get_top_limit_value_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_value')

    get_metrics_mock = mocker.patch('tokenomics_decentralization.helper.get_metrics')

    compute_hhi_mock = mocker.patch('tokenomics_decentralization.analyze.compute_hhi')
    compute_tau_mock = mocker.patch('tokenomics_decentralization.analyze.compute_tau')

    get_clustering_mock.return_value = True
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_exclude_below_usd_cent_mock.return_value = False
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    get_circulation_mock = mocker.patch('tokenomics_decentralization.helper.get_circulation_from_entries')
    circulation = 5
    get_circulation_mock.return_value = circulation

    get_metrics_mock.return_value = ['hhi']

    compute_hhi_mock.return_value = 1

    entries = [(1, ), (2, )]

    hhi_calls = []

    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries, circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'hhi': 1}

    get_clustering_mock.return_value = False
    get_exclude_contracts_mock.return_value = True
    get_exclude_below_fees_mock.return_value = True
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 1

    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries[:1], circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 1}

    compute_hhi_mock.return_value = 2
    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries[:1], circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 2}

    get_clustering_mock.return_value = True
    compute_hhi_mock.return_value = 3
    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries[:1], circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts hhi': 3}

    get_top_limit_value_mock.return_value = 0
    compute_hhi_mock.return_value = 4
    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries, circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'exclude_below_fees exclude_contracts hhi': 4}

    get_top_limit_type_mock.return_value = 'percentage'
    get_top_limit_value_mock.return_value = 0.5
    compute_hhi_mock.return_value = 5
    output = analyze_snapshot(entries)
    hhi_calls.append(call(entries[:int(len(entries)*0.5)], circulation))
    assert compute_hhi_mock.call_args_list == hhi_calls
    assert output == {'top-0.5_percentage exclude_below_fees exclude_contracts hhi': 5}

    get_top_limit_value_mock.return_value = 0
    get_exclude_below_usd_cent_mock.return_value = True
    get_exclude_below_fees_mock.return_value = False
    get_metrics_mock.return_value = ['tau=0.5']
    compute_tau_mock.return_value = 100
    output = analyze_snapshot(entries)
    assert compute_tau_mock.call_args_list == [call(entries, circulation, 0.5)]
    assert output == {'exclude_below_usd_cent exclude_contracts tau=0.5': 100}


def test_get_entries(mocker):
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_exclude_below_fees_mock.return_value = False
    get_exclude_below_usd_cent_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_usd_cent_flag')
    get_exclude_below_usd_cent_mock.return_value = False

    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_contracts_mock.return_value = False

    get_median_tx_fee_mock = mocker.patch('tokenomics_decentralization.helper.get_median_tx_fee')
    get_median_tx_fee_mock.return_value = 0
    get_usd_cent_equivalent_mock = mocker.patch('tokenomics_decentralization.helper.get_usd_cent_equivalent')
    get_usd_cent_equivalent_mock.return_value = 0

    get_db_connector_mock = mocker.patch('tokenomics_decentralization.db_helper.get_connector')
    get_db_connector_mock.return_value = 'connector'

    get_special_addresses_mock = mocker.patch('tokenomics_decentralization.helper.get_special_addresses')
    get_special_addresses_mock.return_value = set(['addr2'])

    get_db_filename_mock = mocker.patch('tokenomics_decentralization.db_helper.get_db_filename')
    get_db_filename_mock.return_value = 'bitcoin_Test.db'

    mocker.patch('builtins.open', mocker.mock_open(read_data='address,balance\naddr1,1\naddr2,2'))

    get_address_entity_mock = mocker.patch('tokenomics_decentralization.db_helper.get_address_entity')
    get_address_entity_mock.side_effect = [('entity1', 1), ('entity2', 0)]

    entries = get_entries('bitcoin', '2010-01-01', 'test_filename')
    assert entries == [1]
    assert get_db_connector_mock.call_args_list == [call('bitcoin_Test.db')]


def test_analyze(mocker):
    get_input_directories_mock = mocker.patch('tokenomics_decentralization.helper.get_input_directories')
    get_input_directories_mock.return_value = [pathlib.Path('/').resolve()]

    is_file_mock = mocker.patch('os.path.isfile')
    is_file_mock.side_effect = {
        pathlib.Path('/bitcoin_2010-01-01_raw_data.csv').resolve(): True,
        pathlib.Path('/bitcoin_2011-01-01_raw_data.csv').resolve(): False,
        pathlib.Path('/ethereum_2010-01-01_raw_data.csv').resolve(): False,
        pathlib.Path('/ethereum_2011-01-01_raw_data.csv').resolve(): True,
    }.get

    get_db_connector_mock = mocker.patch('tokenomics_decentralization.db_helper.get_connector')
    get_db_connector_mock.return_value = 'connector'

    get_entries_mock = mocker.patch('tokenomics_decentralization.analyze.get_entries')
    entries = [1, 2]
    get_entries_mock.return_value = entries

    analyze_snapshot_mock = mocker.patch('tokenomics_decentralization.analyze.analyze_snapshot')
    analyze_snapshot_mock.return_value = {'hhi': 1}

    get_output_row_mock = mocker.patch('tokenomics_decentralization.helper.get_output_row')
    get_output_row_mock.return_value = 'row'

    write_csv_output_mock = mocker.patch('tokenomics_decentralization.helper.write_csv_output')

    get_input_dirs_calls = []
    get_entries_calls = []
    analyze_snapshot_calls = []
    get_row_calls = []
    write_output_calls = []

    analyze(['bitcoin'], ['2010-01-01'])
    get_input_dirs_calls.append(call())
    assert get_input_directories_mock.call_args_list == get_input_dirs_calls
    get_entries_calls.append(call('bitcoin', '2010-01-01', pathlib.Path('/bitcoin_2010-01-01_raw_data.csv').resolve()))
    assert get_entries_mock.call_args_list == get_entries_calls
    analyze_snapshot_calls.append(call(entries))
    assert analyze_snapshot_mock.call_args_list == analyze_snapshot_calls
    get_row_calls.append(call('bitcoin', '2010-01-01', {'hhi': 1}))
    assert get_output_row_mock.call_args_list == get_row_calls
    write_output_calls.append(call(['row']))
    assert write_csv_output_mock.call_args_list == write_output_calls

    analyze(['bitcoin', 'ethereum'], ['2010-01-01', '2011-01-01'])
    get_input_dirs_calls += 4 * [call()]
    assert get_input_directories_mock.call_args_list == get_input_dirs_calls
    get_entries_calls.append(call('bitcoin', '2010-01-01', pathlib.Path('/bitcoin_2010-01-01_raw_data.csv').resolve()))
    get_entries_calls.append(call('ethereum', '2011-01-01', pathlib.Path('/ethereum_2011-01-01_raw_data.csv').resolve()))
    assert get_entries_mock.call_args_list == get_entries_calls
    analyze_snapshot_calls += 2 * [call(entries)]
    assert analyze_snapshot_mock.call_args_list == analyze_snapshot_calls
    get_row_calls.append(call('bitcoin', '2010-01-01', {'hhi': 1}))
    get_row_calls.append(call('ethereum', '2011-01-01', {'hhi': 1}))
    assert get_output_row_mock.call_args_list == get_row_calls
    write_output_calls.append(call(['row', 'row']))
    assert write_csv_output_mock.call_args_list == write_output_calls
